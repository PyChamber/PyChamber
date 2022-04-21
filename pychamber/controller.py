import functools
import itertools
import logging
import pathlib
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Union

import cloudpickle as pickle
import numpy as np
from PyQt5.QtCore import QMutex, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from pyvisa.errors import LibraryError, VisaIOError
from serial.tools import list_ports
from skrf.vi import vna

from pychamber import positioner
from pychamber.network_model import NetworkModel
from pychamber.positioner import PositionerError
from pychamber.ui.main_window import MainWindow
from pychamber.ui.pop_ups import ClearDataWarning, MsgLevel, PopUpMessage, WhichPol

log = logging.getLogger(__name__)
MUTEX = QMutex()


class JogAxis(Enum):
    AZIMUTH = auto()
    ELEVATION = auto()


class AzJogDir(Enum):
    LEFT = -1
    RIGHT = 1


class ElJogDir(Enum):
    DOWN = -1
    UP = 1


class FreqSetting(Enum):
    START = auto()
    STOP = auto()
    STEP = auto()


class JogWorker(QObject):
    finished = pyqtSignal()
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)

    axis: Optional[JogAxis] = None
    angle: Optional[float] = None
    positioner_: Optional[positioner.Positioner] = None
    relative = False

    def run(self) -> None:
        if self.axis == JogAxis.AZIMUTH:
            self._jog_az()
        elif self.axis == JogAxis.ELEVATION:
            self._jog_el()
        self.finished.emit()

    def _jog_az(self) -> None:
        assert self.positioner_
        assert self.angle is not None

        if self.relative:
            MUTEX.lock()
            self.positioner_.move_azimuth_relative(self.angle)
            pos = self.positioner_.current_azimuth
            MUTEX.unlock()
        else:
            MUTEX.lock()
            self.positioner_.move_azimuth_absolute(self.angle)
            pos = self.positioner_.current_azimuth
            MUTEX.unlock()
        self.azMoveComplete.emit(pos)

    def _jog_el(self) -> None:
        assert self.positioner_
        assert self.angle is not None

        if self.relative:
            MUTEX.lock()
            self.positioner_.move_elevation_relative(self.angle)
            pos = self.positioner_.current_elevation
            MUTEX.unlock()
        else:
            MUTEX.lock()
            self.positioner_.move_elevation_absolute(self.angle)
            pos = self.positioner_.current_elevation
            MUTEX.unlock()
        self.elMoveComplete.emit(pos)


class JogZeroWorker(QObject):
    finished = pyqtSignal()
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)

    positioner_: Optional[positioner.Positioner] = None

    def run(self) -> None:
        assert self.positioner_

        MUTEX.lock()
        self.positioner_.move_elevation_absolute(0.0)
        MUTEX.unlock()
        self.elMoveComplete.emit(0.0)

        MUTEX.lock()
        self.positioner_.move_azimuth_absolute(0.0)
        MUTEX.unlock()
        self.azMoveComplete.emit(0.0)

        self.finished.emit()


class ScanWorker(QObject):
    finished = pyqtSignal()
    aborted = pyqtSignal()
    progress = pyqtSignal(int)
    cutProgress = pyqtSignal(int)
    timeUpdate = pyqtSignal(float)
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)
    dataAcquired = pyqtSignal(object)

    azimuths: Optional[np.ndarray] = None
    elevations: Optional[np.ndarray] = None
    analyzer: Optional[vna.VNA] = None
    positioner_: Optional[positioner.Positioner] = None
    ntwk_models: Optional[Dict[str, NetworkModel]] = None
    pol1: Optional[List[int]] = None
    pol2: Optional[List[int]] = None

    abort = False

    def set_abort(self, abort: bool) -> None:
        self.abort = abort

    def run(self) -> None:
        if (self.azimuths is not None) and (self.elevations is not None):
            self._run_full_scan()
        elif self.azimuths is not None:
            self._run_az_scan()
        elif self.elevations is not None:
            self._run_el_scan()
        self.finished.emit()

    def _run_full_scan(self) -> None:
        assert self.azimuths is not None
        assert self.elevations is not None
        assert self.analyzer is not None
        assert self.positioner_ is not None
        assert self.ntwk_models is not None

        total_iters = len(self.azimuths) * len(self.elevations)
        pol_1_data = []
        pol_2_data = []
        for i, az in enumerate(self.azimuths):
            MUTEX.lock()
            self.positioner_.move_azimuth_absolute(az)
            pos = self.positioner_.current_azimuth
            MUTEX.unlock()
            self.azMoveComplete.emit(pos)
            for j, el in enumerate(self.elevations):
                if self.abort:
                    MUTEX.lock()
                    self.positioner_.abort_all()
                    MUTEX.unlock()
                    break

                pos_meta = {'azimuth': az, 'elevation': el}
                start = time.time()
                MUTEX.lock()
                self.positioner_.move_elevation_absolute(el)
                pos = self.positioner_.current_elevation
                self.elMoveComplete.emit(pos)
                if self.pol1:
                    ntwk = self.analyzer.get_snp_network(self.pol1).s21  # type: ignore
                    ntwk.params = pos_meta
                    pol_1_data.append(ntwk)
                if self.pol2:
                    ntwk = self.analyzer.get_snp_network(self.pol2).s21  # type: ignore
                    ntwk.params = pos_meta
                    pol_2_data.append(ntwk)
                MUTEX.unlock()
                end = time.time()

                completed = i * len(self.azimuths) + j
                progress = completed * 100 // total_iters
                self.progress.emit(progress)
                self.cutProgress.emit(j * 100 // len(self.elevations))
                single_iter_time = end - start
                remaining = total_iters - completed
                time_remaining = single_iter_time * remaining
                self.timeUpdate.emit(time_remaining)

            if self.abort:
                break

        self.dataAcquired.emit(
            {'pol1': NetworkModel(pol_1_data), 'pol2': NetworkModel(pol_2_data)}
        )

    def _run_az_scan(self) -> None:
        assert self.azimuths is not None
        assert self.analyzer is not None
        assert self.positioner_ is not None
        assert self.ntwk_models is not None

        pol_1_data = []
        pol_2_data = []
        for i, az in enumerate(self.azimuths):
            log.info(f"Iteration: {i+1}/{len(self.azimuths)}")
            if self.abort:
                MUTEX.lock()
                self.positioner_.abort_all()
                MUTEX.unlock()
                break

            pos_meta = {'azimuth': az, 'elevation': 0}
            start = time.time()
            MUTEX.lock()
            self.positioner_.move_azimuth_absolute(az)
            pos = self.positioner_.current_azimuth
            self.azMoveComplete.emit(pos)

            if self.pol1:
                ntwk = self.analyzer.get_snp_network(self.pol1).s21  # type: ignore
                ntwk.params = pos_meta
                pol_1_data.append(ntwk)
            if self.pol2:
                ntwk = self.analyzer.get_snp_network(self.pol2).s21  # type: ignore
                ntwk.params = pos_meta
                pol_2_data.append(ntwk)
            MUTEX.unlock()
            end = time.time()

            progress = i * 100 // len(self.azimuths)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.azimuths) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)

        self.dataAcquired.emit(
            {'pol1': NetworkModel(pol_1_data), 'pol2': NetworkModel(pol_2_data)}
        )

    def _run_el_scan(self) -> None:
        assert self.elevations is not None
        assert self.analyzer is not None
        assert self.positioner_ is not None
        assert self.ntwk_models is not None

        pol_1_data = []
        pol_2_data = []
        for i, el in enumerate(self.elevations):
            if self.abort:
                MUTEX.lock()
                self.positioner_.abort_all()
                MUTEX.unlock()
                break

            pos_meta = {'azimuth': 0, 'elevation': el}
            start = time.time()
            MUTEX.lock()
            self.positioner_.move_elevation_absolute(el)
            pos = self.positioner_.current_elevation
            self.elMoveComplete.emit(pos)

            if self.pol1:
                ntwk = self.analyzer.get_snp_network(self.pol1).s21  # type: ignore
                ntwk.params = pos_meta
                pol_1_data.append(ntwk)
            if self.pol2:
                ntwk = self.analyzer.get_snp_network(self.pol2).s21  # type: ignore
                ntwk.params = pos_meta
                pol_2_data.append(ntwk)
            MUTEX.unlock()
            end = time.time()

            progress = i * 100 // len(self.elevations)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.elevations) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)

        self.dataAcquired.emit(
            {'pol1': NetworkModel(pol_1_data), 'pol2': NetworkModel(pol_2_data)}
        )


class PyChamberCtrl:
    analyzer_models = {
        "Agilent PNA": vna.PNA,
    }
    positioner_models = {
        "D6050": positioner.D6050,
    }

    worker: Optional[Union[JogWorker, JogZeroWorker, ScanWorker]] = None

    def __init__(self, view: MainWindow) -> None:
        self.view = view
        self.ntwk_models = {
            'pol1': NetworkModel(),
            'pol2': NetworkModel(),
        }
        self.analyzer: Optional[vna.VNA] = None
        self.positioner: Optional[positioner.Positioner] = None

        self.connect_signals()

        self.update_analyzer_ports()
        self.update_analyzer_models()
        self.update_positioner_ports()
        self.update_positioner_models()

    def connect_signals(self) -> None:
        # Buttons
        self.view.experimentFullScanButton.clicked.connect(self.full_scan)
        self.view.experimentAzScanButton.clicked.connect(self.az_scan)
        self.view.experimentElScanButton.clicked.connect(self.el_scan)
        self.view.jogAzLeftButton.clicked.connect(
            functools.partial(self.jog_az, AzJogDir.LEFT)
        )
        self.view.jogAzZeroButton.clicked.connect(functools.partial(self.jog_az, angle=0))
        self.view.jogAzRightButton.clicked.connect(
            functools.partial(self.jog_az, AzJogDir.RIGHT)
        )
        self.view.jogAzSubmitButton.clicked.connect(self.jog_az_to)
        self.view.jogElSubmitButton.clicked.connect(
            functools.partial(self.jog_el, ElJogDir.UP)
        )
        self.view.jogElZeroButton.clicked.connect(functools.partial(self.jog_el, angle=0))
        self.view.jogElDownButton.clicked.connect(
            functools.partial(self.jog_el, ElJogDir.DOWN)
        )
        self.view.jogElSubmitButton.clicked.connect(self.jog_el_to)
        self.view.setZeroButton.clicked.connect(self.set_zero)
        self.view.returnToZeroButton.clicked.connect(self.return_to_zero)
        self.view.analyzerConnectButton.clicked.connect(self.connect_to_analyzer)
        self.view.positionerConnectButton.clicked.connect(self.connect_to_positioner)
        self.view.clearDataButton.clicked.connect(self.clear_data)
        self.view.saveDataButton.clicked.connect(self.save_data)
        self.view.loadDataButton.clicked.connect(self.load_data)
        self.view.exportDataButton.clicked.connect(self.export_csv)

        # Line Edits
        self.view.analyzerStartFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.START)
        )
        self.view.analyzerStopFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.STOP)
        )
        # self.view.stepFreqLineEdit.returnPressed.connect(
        #     functools.partial(self.set_freq, FreqSetting.STEP)
        # )
        self.view.analyzerNPointsLineEdit.returnPressed.connect(self.set_npoints)

    def update_positioner_ports(self) -> None:
        self.view.positionerPortComboBox.clear()
        ports = [p.device for p in list_ports.comports()]
        self.view.positionerPortComboBox.addItems(ports)

    def update_analyzer_ports(self) -> None:
        self.view.analyzerAddressComboBox.clear()

        # FIXME: This is only for linux
        backend = '/usr/lib/x86_64-linux-gnu/libktvisa32.so.0'

        # If we can't find the library, default to pyvisa-py
        try:
            addrs = vna.VNA.available(backend=backend)
        except LibraryError:
            addrs = vna.VNA.available()

        self.view.analyzerAddressComboBox.addItems(addrs)

    def update_analyzer_models(self) -> None:
        self.view.analyzerModelComboBox.clear()
        self.view.analyzerModelComboBox.addItems(list(self.analyzer_models.keys()))

    def update_positioner_models(self) -> None:
        self.view.positionerModelComboBox.clear()
        self.view.positionerModelComboBox.addItems(list(self.positioner_models.keys()))

    def jog_az(
        self, dir: Optional[AzJogDir] = None, angle: Optional[float] = None
    ) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        if dir:
            step = self.view.get_az_jog_step()
            if np.isclose(step, 0.0):
                return
            diff = dir.value * step
            try:
                self.jog_thread(JogAxis.AZIMUTH, diff, relative=True)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            try:
                self.jog_thread(JogAxis.AZIMUTH, angle, relative=False)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return

    def jog_el(
        self, dir: Optional[ElJogDir] = None, angle: Optional[float] = None
    ) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        if dir:
            step = self.view.get_el_jog_step()
            if np.isclose(step, 0.0):
                return
            diff = dir.value * step
            try:
                self.jog_thread(JogAxis.ELEVATION, diff, relative=True)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            try:
                self.jog_thread(JogAxis.ELEVATION, angle, relative=False)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return

    def jog_zero(self) -> None:
        if not self.positioner:
            PopUpMessage("Positioner not connected")
            return

        try:
            self.jog_zero_thread()
        except PositionerError as e:
            log.error(str(e))
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def jog_az_to(self) -> None:
        if angle := self.view.get_az_jog_to():
            self.jog_az(angle=angle)

    def jog_el_to(self) -> None:
        if angle := self.view.get_el_jog_to():
            self.jog_el(angle=angle)

    def set_zero(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return
        self.positioner.zero()
        self.view.set_az_pos(0.0)
        self.view.set_el_pos(0.0)

    def return_to_zero(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        az_not_at_zero = not np.isclose(self.positioner.current_azimuth, 0.0)
        el_not_at_zero = not np.isclose(self.positioner.current_elevation, 0.0)

        if az_not_at_zero and el_not_at_zero:
            self.jog_zero_thread()
        elif az_not_at_zero:
            self.jog_az(angle=0.0)
        elif el_not_at_zero:
            self.jog_el(angle=0.0)

    def full_scan(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.view.cutProgressLabel.show()
        self.view.cutProgressBar.show()
        self.view.update_monitor_freqs()

        azimuths = np.arange(
            self.view.get_az_start(), self.view.get_az_stop(), self.view.get_az_step()
        )
        elevations = np.arange(
            self.view.get_el_start(), self.view.get_el_stop(), self.view.get_el_step()
        )

        try:
            self.start_scan_thread(azimuths, elevations)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def az_scan(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.view.update_monitor_freqs()

        azimuths = np.arange(
            self.view.get_az_start(), self.view.get_az_stop(), self.view.get_az_step()
        )

        try:
            self.start_scan_thread(azimuths=azimuths)
        except Exception as e:
            log.error(str(e))
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def el_scan(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.view.update_monitor_freqs()

        elevations = np.arange(
            self.view.get_el_start(), self.view.get_el_stop(), self.view.get_el_step()
        )

        try:
            self.start_scan_thread(elevations=elevations)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def connect_to_analyzer(self) -> None:
        if self.analyzer:
            return
        model = self.view.analyzerComboBox.currentText()
        port = self.view.get_analyzer_port()

        if model == "" or port == "":
            return

        try:
            log.info("Connecting to analyzer...")
            self.analyzer = self.analyzer_models[model](
                port, backend='/usr/lib/x86_64-linux-gnu/libktvisa32.so.0'
            )
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        try:
            self.view.set_start_freq(self.analyzer.start_freq)
            self.view.set_stop_freq(self.analyzer.stop_freq)
            self.view.set_npoints(self.analyzer.npoints)
            # self.view.set_step_freq(self.analyzer.freq_step)
            ports = self.analyzer.ports
        except VisaIOError as e:
            log.error(f"Error communicating with the analyzer: {e}")
            PopUpMessage(
                "Error connecting to analyzer.\nDo you have the right port?",
                MsgLevel.ERROR,
            )
            self.analyzer = None
            return
        ports = [f"S{''.join(p)}" for p in itertools.permutations(ports, 2)]
        self.view.pol1ComboBox.addItems(ports)
        self.view.pol2ComboBox.addItems(ports)
        log.info("Connected")
        self.view.frequencyGroupBox.setEnabled(True)
        if self.view.positionerGroupBox.isEnabled():
            self.view.experimentGroupBox.setEnabled(True)

    def connect_to_positioner(self) -> None:
        if self.positioner:
            return
        model = self.view.get_positioner_model()
        port = self.view.get_positioner_port()
        log.info("Connecting to positioner...")

        if model == "" or port == "":
            log.info("Model or Port not selected. Ignoring")
            return

        try:
            self.positioner = self.positioner_models[model](port)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        self.view.azPosLineEdit.setText(f"{self.positioner.azimuth_deg}")
        self.view.elPosLineEdit.setText(f"{self.positioner.elevation_deg}")
        log.info("Connected")
        self.view.enable_jog()
        self.view.enable_experiment()

    def set_freq(self, setting: FreqSetting) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected", MsgLevel.WARNING)
            return

        try:
            if setting == FreqSetting.START:
                if freq := self.view.get_start_freq():
                    self.analyzer.start_freq = freq
            elif setting == FreqSetting.STOP:
                if freq := self.view.get_stop_freq():
                    self.analyzer.stop_freq = freq
            # elif setting == FreqSetting.STEP:
            #     if freq := self.view.get_freq_step():
            #         self.analyzer.freq_step = freq
        except VisaIOError as e:
            log.error(f"Failed to communicate with analyzer: {str(e)}")
            PopUpMessage("Failed to communicate with analyzer", MsgLevel.ERROR)
            return

    def set_npoints(self) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected")
            return

        if npoints := self.view.get_npoints():
            self.analyzer.npoints = npoints

    def update_polar_data_plot(self) -> None:
        freq = str(self.view.polar_plot_freq)

        pol = "pol1" if self.view.polar_plot_pol == 1 else "pol2"  # FIXME

        if len(self.ntwk_models[pol]) == 0:
            return

        azimuths = np.deg2rad(self.ntwk_models[pol].azimuths.reshape(-1, 1))
        mags = self.ntwk_models[pol].mags(freq, elevation=0).reshape(-1, 1)

        self.view.update_polar_plot(azimuths, mags)

    def update_over_freq_plot(self) -> None:
        pol = "pol1" if self.view.over_freq_plot_pol == 1 else "pol2"

        if len(self.ntwk_models[pol]) == 0:
            return

        freqs = self.ntwk_models[pol].freqs.reshape(-1, 1)
        mags = self.ntwk_models[pol].mags(azimuth=0.0, elevation=0.0).reshape(-1, 1)

        self.view.update_over_freq_plot(freqs, mags)

    def clear_data(self) -> None:
        if len(self.ntwk_models['pol1']) == 0 and len(self.ntwk_models['pol2']) == 0:
            return
        actually_clear = ClearDataWarning(
            "This will delete all data. Are you sure?"
        ).warn()
        if actually_clear:
            self.ntwk_models = {'pol1': NetworkModel(), 'pol2': NetworkModel()}

    def save_data(self) -> None:
        if len(self.ntwk_models['pol1']) == 0 and len(self.ntwk_models['pol2']) == 0:
            PopUpMessage("No data to save")
            return
        save_name, _ = QFileDialog.getSaveFileName()
        if save_name != "":

            with open(save_name, 'wb') as save_file:
                pickle.dump(self.ntwk_models, save_file)

    def load_data(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            with open(file_name, 'rb') as data:
                try:
                    val = pickle.load(data)
                    self.ntwk_models = val
                except Exception:
                    PopUpMessage("Invalid file", MsgLevel.ERROR)
                    return

            temp = next(iter(val.values()))
            self.view.dataPolarFreqSpinBox.setMinimum(temp.freqs[0])
            self.view.dataPolarFreqSpinBox.setMaximum(temp.freqs[-1])
            self.view.dataPolarFreqSpinBox.setSingleStep(temp.freqs[1] - temp.freqs[0])

    def export_csv(self) -> None:
        if len(self.ntwk_models['pol1']) > 0 and len(self.ntwk_models['pol2']) > 0:
            which = "pol1" if WhichPol.ask() == 1 else "pol2"
            to_export = self.ntwk_models[which]
        elif len(self.ntwk_models['pol1']) > 0:
            to_export = self.ntwk_models['pol1']
        elif len(self.ntwk_models['pol2']) > 0:
            to_export = self.ntwk_models['pol2']
        else:
            PopUpMessage("No data to export")
            return

        save_name, _ = QFileDialog.getSaveFileName()
        if save_name != "":
            save_path = pathlib.Path(save_name)
            if save_path.suffix != ".csv":
                save_path = save_path.with_suffix(".csv")
                to_export.write_spreadsheet(save_name)

    def update_ntwk_models(self, data: Dict[str, NetworkModel]) -> None:
        self.ntwk_models = data

    def start_scan_thread(
        self,
        azimuths: Optional[np.ndarray] = None,
        elevations: Optional[np.ndarray] = None,
    ) -> None:
        self.thread = QThread()
        self.worker = ScanWorker()

        self.worker.azimuths = azimuths
        self.worker.elevations = elevations
        self.worker.analyzer = self.analyzer
        self.worker.positioner_ = self.positioner
        self.worker.ntwk_models = self.ntwk_models
        self.worker.pol1 = self.view.get_pol_1()
        self.worker.pol2 = self.view.get_pol_2()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(lambda p: self.view.update_progress(p))
        self.worker.finished.connect(self.update_polar_data_plot)
        self.worker.finished.connect(self.update_over_freq_plot)
        self.worker.progress.connect(lambda p: self.view.update_progress(p))
        if self.view.cutProgressBar.isVisible():
            self.worker.cutProgress.connect(lambda p: self.view.update_cut_progress(p))
        self.worker.timeUpdate.connect(lambda t: self.view.update_time_remaining(t))
        self.worker.azMoveComplete.connect(
            lambda p: self.view.azPosLineEdit.setText(str(p))
        )
        self.worker.elMoveComplete.connect(
            lambda p: self.view.elPosLineEdit.setText(str(p))
        )
        self.worker.dataAcquired.connect(lambda data: self.update_ntwk_models(data))

        self.thread.start()

        self.view.analyzerGroupBox.setEnabled(False)
        self.view.positionerGroupBox.setEnabled(False)
        self.view.fullScanButton.setEnabled(False)
        self.view.azScanButton.setEnabled(False)
        self.view.elScanButton.setEnabled(False)
        self.view.abortButton.setEnabled(True)

        self.view.abortButton.clicked.connect(
            lambda: self.worker.set_abort(True)  # type: ignore
        )

        self.thread.finished.connect(lambda: self.view.analyzerGroupBox.setEnabled(True))
        self.thread.finished.connect(
            lambda: self.view.positionerGroupBox.setEnabled(True)
        )
        self.thread.finished.connect(lambda: self.view.fullScanButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.view.azScanButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.view.elScanButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.view.abortButton.setEnabled(False))
        self.thread.finished.connect(lambda: self.view.update_progress(100))
        self.thread.finished.connect(lambda: self.view.update_time_remaining(0))
        self.thread.finished.connect(lambda: log.info("Scan complete"))

        if self.view.cutProgressBar.isVisible():
            self.thread.finished.connect(lambda: self.view.cutProgressBar.hide())

    def jog_thread(self, axis: JogAxis, angle: float, relative: bool) -> None:
        self.thread = QThread()
        self.worker = JogWorker()

        self.worker.axis = axis
        self.worker.angle = angle
        self.worker.relative = relative
        self.worker.positioner_ = self.positioner

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.azMoveComplete.connect(
            lambda p: self.view.azPosLineEdit.setText(str(p))
        )
        self.worker.elMoveComplete.connect(
            lambda p: self.view.elPosLineEdit.setText(str(p))
        )

        self.thread.start()

        self.view.disable_jog_buttons()
        self.thread.finished.connect(self.view.enable_jog_buttons)

    def jog_zero_thread(self) -> None:
        self.thread = QThread()
        self.worker = JogZeroWorker()

        self.worker.positioner_ = self.positioner

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.azMoveComplete.connect(
            lambda p: self.view.azPosLineEdit.setText(str(p))
        )
        self.worker.elMoveComplete.connect(
            lambda p: self.view.elPosLineEdit.setText(str(p))
        )

        self.thread.start()

        self.view.disable_jog_buttons()
        self.thread.finished.connect(self.view.enable_jog_buttons)
