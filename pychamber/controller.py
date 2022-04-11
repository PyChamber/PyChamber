import functools
import itertools
import logging
import pathlib
import pickle
import time
from enum import Enum, auto
from typing import Optional, Tuple, Union

import numpy as np
from PyQt5.QtCore import QMutex, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from pyvisa.errors import VisaIOError
from serial.tools import list_ports
from skrf.vi import vna

from pychamber import positioner
from pychamber.app import AppUI, ClearDataWarning, MsgLevel, PopUpMessage, WhichPol
from pychamber.network_model import NetworkModel
from pychamber.positioner import PositionerError

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


class ScanWorker(QObject):
    finished = pyqtSignal()
    aborted = pyqtSignal()
    progress = pyqtSignal(int)
    cutProgress = pyqtSignal(int)
    timeUpdate = pyqtSignal(float)
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)

    azimuths: Optional[np.ndarray] = None
    elevations: Optional[np.ndarray] = None
    # analyzer: Optional[vna.VNA] = None
    positioner_: Optional[positioner.Positioner] = None
    # ntwk_models: Optional[List[NetworkModel]] = None
    pol1: Optional[Tuple] = None
    pol2: Optional[Tuple] = None

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
        # assert self.analyzer is not None
        assert self.positioner_ is not None
        # assert self.ntwk_models is not None

        total_iters = len(self.azimuths) * len(self.elevations)
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

                start = time.time()
                MUTEX.lock()
                self.positioner_.move_elevation_absolute(el)
                pos = self.positioner_.current_elevation
                self.elMoveComplete.emit(pos)
                # if self.pol1:
                #     self.ntwk_models[0].append(self.analyzer.get_snp_network(self.pol1))
                # if self.pol2:
                #     self.ntwk_models[1].append(self.analyzer.get_snp_network(self.pol2))
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

    def _run_az_scan(self) -> None:
        assert self.azimuths is not None
        # assert self.analyzer is not None
        assert self.positioner_ is not None
        # assert self.ntwk_models is not None

        for i, az in enumerate(self.azimuths):
            if self.abort:
                MUTEX.lock()
                self.positioner_.abort_all()
                MUTEX.unlock()
                break

            start = time.time()
            MUTEX.lock()
            self.positioner_.move_azimuth_absolute(az)
            pos = self.positioner_.current_azimuth
            self.azMoveComplete.emit(pos)

            # if self.pol1:
            #     self.ntwk_models[0].append(self.analyzer.get_snp_network(self.pol1))
            # if self.pol2:
            #     self.ntwk_models[1].append(self.analyzer.get_snp_network(self.pol2))
            MUTEX.unlock()
            end = time.time()

            progress = i * 100 // len(self.azimuths)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.azimuths) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)

    def _run_el_scan(self) -> None:
        assert self.elevations is not None
        # assert self.analyzer is not None
        assert self.positioner_ is not None
        # assert self.ntwk_models is not None

        for i, el in enumerate(self.elevations):
            if self.abort:
                MUTEX.lock()
                self.positioner_.abort_all()
                MUTEX.unlock()
                break

            start = time.time()
            MUTEX.lock()
            self.positioner_.move_elevation_absolute(el)
            pos = self.positioner_.current_elevation
            self.elMoveComplete.emit(pos)

            # if self.pol1:
            #     self.ntwk_models[0].append(self.analyzer.get_snp_network(self.pol1))
            # if self.pol2:
            #     self.ntwk_models[1].append(self.analyzer.get_snp_network(self.pol2))
            MUTEX.unlock()
            end = time.time()

            progress = i * 100 // len(self.elevations)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.elevations) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)


class PyChamberCtrl:
    analyzer_models = {
        "Agilent PNA": vna.PNA,
    }
    positioner_models = {
        "D6050": positioner.D6050,
    }

    worker: Optional[Union[JogWorker, ScanWorker]] = None

    def __init__(self, view: AppUI) -> None:
        self.view = view
        self.ntwk_models = [NetworkModel(), NetworkModel()]
        self.analyzer: Optional[vna.VNA] = None
        self.positioner: Optional[positioner.Positioner] = None

        self.connect_signals()

        self.update_analyzer_ports()
        self.update_analyzer_models()
        self.update_positioner_ports()
        self.update_positioner_models()

        self.init_over_freq_plot()
        self.init_polar_data_plot()

    def connect_signals(self) -> None:
        # Buttons
        self.view.fullScanButton.clicked.connect(self.full_scan)
        self.view.azScanButton.clicked.connect(self.az_scan)
        self.view.elScanButton.clicked.connect(self.el_scan)
        self.view.azJogLeftButton.clicked.connect(
            functools.partial(self.jog_az, AzJogDir.LEFT)
        )
        self.view.azJogZeroButton.clicked.connect(functools.partial(self.jog_az, angle=0))
        self.view.azJogRightButton.clicked.connect(
            functools.partial(self.jog_az, AzJogDir.RIGHT)
        )
        self.view.azJogToSubmitButton.clicked.connect(self.jog_az_to)
        self.view.elJogUpButton.clicked.connect(
            functools.partial(self.jog_el, ElJogDir.UP)
        )
        self.view.elJogZeroButton.clicked.connect(functools.partial(self.jog_el, angle=0))
        self.view.elJogDownButton.clicked.connect(
            functools.partial(self.jog_el, ElJogDir.DOWN)
        )
        self.view.elJogToSubmitButton.clicked.connect(self.jog_el_to)
        self.view.setZeroButton.clicked.connect(self.set_zero)
        self.view.returnToZeroButton.clicked.connect(self.return_to_zero)
        self.view.analyzerConnectButton.clicked.connect(self.connect_to_analyzer)
        self.view.positionerConnectButton.clicked.connect(self.connect_to_positioner)
        self.view.clearDataButton.clicked.connect(self.clear_data)
        self.view.saveDataButton.clicked.connect(self.save_data)
        self.view.loadDataButton.clicked.connect(self.load_data)
        self.view.exportCSVButton.clicked.connect(self.export_csv)

        # Line Edits
        self.view.startFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.START)
        )
        self.view.stopFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.STOP)
        )
        # self.view.stepFreqLineEdit.returnPressed.connect(
        #     functools.partial(self.set_freq, FreqSetting.STEP)
        # )
        self.view.nPointsLineEdit.returnPressed.connect(self.set_npoints)

        # Spin Boxes
        self.view.dataPolarFreqSpinBox.valueChanged.connect(self.update_polar_data_plot)
        self.view.dataPolarMinSpinBox.valueChanged.connect(self.update_polar_data_plot)
        self.view.dataPolarMaxSpinBox.valueChanged.connect(self.update_polar_data_plot)
        self.view.dataPolarDbPerSpinBox.valueChanged.connect(self.update_polar_data_plot)
        self.view.overFreqMinSpinBox.valueChanged.connect(self.update_over_freq_plot)
        self.view.overFreqMaxSpinBox.valueChanged.connect(self.update_over_freq_plot)
        self.view.overFreqDbPerSpinBox.valueChanged.connect(self.update_over_freq_plot)

        # Combo Boxes
        self.view.dataPolarPolComboBox.currentIndexChanged.connect(
            self.update_polar_data_plot
        )
        self.view.overFreqPolComboBox.currentIndexChanged.connect(
            self.update_over_freq_plot
        )

    def update_positioner_ports(self) -> None:
        self.view.positionerPortComboBox.clear()
        ports = [p.device for p in list_ports.comports()]
        log.info("Available ports:")
        for p in ports:
            log.info(f"\t{p}")
        self.view.positionerPortComboBox.addItems(ports)

    def update_analyzer_ports(self) -> None:
        self.view.analyzerPortComboBox.clear()
        ports = vna.VNA.available(backend='/usr/lib/x86_64-linux-gnu/libktvisa32.so.0')
        log.info("Available analyzers:")
        for p in ports:
            log.info(f"\t{p}")
        self.view.analyzerPortComboBox.addItems(ports)

    def update_analyzer_models(self) -> None:
        self.view.analyzerComboBox.clear()
        self.view.analyzerComboBox.addItems(["Agilent PNA"])

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
            step = self.view.az_jog_step
            diff = dir.value * step
            log.info(f"Jogging azimuth {diff}")
            try:
                self.jog_thread(JogAxis.AZIMUTH, diff, relative=True)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            log.info(f"Jogging azimuth to {angle}")
            try:
                self.jog_thread(JogAxis.AZIMUTH, angle, relative=False)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return

        self.view.az_pos = self.positioner.current_azimuth

    def jog_el(
        self, dir: Optional[ElJogDir] = None, angle: Optional[float] = None
    ) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        if dir:
            step = self.view.el_jog_step
            diff = dir.value * step
            log.info(f"Jogging elevation {diff}")
            try:
                self.jog_thread(JogAxis.ELEVATION, diff, relative=True)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            log.info(f"Jogging elevation to {angle}")
            try:
                self.jog_thread(JogAxis.ELEVATION, angle, relative=False)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return

    def jog_az_to(self) -> None:
        if angle := self.view.az_jog_to:
            self.jog_az(angle=angle)

    def jog_el_to(self) -> None:
        if angle := self.view.el_jog_to:
            self.jog_el(angle=angle)

    def set_zero(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return
        log.info("Setting current position as 0,0")
        self.positioner.zero()

    def return_to_zero(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return
        log.info("Jogging to 0,0")
        self.jog_el(angle=0)
        self.jog_az(angle=0)

    def full_scan(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.view.cutProgressLabel.show()
        self.view.cutProgressBar.show()
        self.update_monitor_freqs()

        azimuths = np.arange(self.view.az_start, self.view.az_stop, self.view.az_step)
        elevations = np.arange(self.view.el_start, self.view.el_stop, self.view.el_step)

        try:
            log.info("Starting full scan")
            self.start_scan_thread(azimuths, elevations)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def az_scan(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.update_monitor_freqs()

        azimuths = np.arange(self.view.az_start, self.view.az_stop, self.view.az_step)

        try:
            log.info("Starting azimuth scan")
            self.start_scan_thread(azimuths=azimuths)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def el_scan(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.update_monitor_freqs()

        elevations = np.arange(self.view.el_start, self.view.el_stop, self.view.el_step)

        try:
            log.info("Starting elevation scan")
            self.start_scan_thread(elevations=elevations)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def connect_to_analyzer(self) -> None:
        if self.analyzer:
            log.info("Already connected.")
            return
        model = self.view.analyzerComboBox.currentText()
        port = self.view.analyzer_port

        if model == "" or port == "":
            log.info("Model not selected. Ignoring")
            return

        try:
            log.info("Connecting to analyzer...")
            self.analyzer = self.analyzer_models[model](port, backend='/usr/lib/x86_64-linux-gnu/libktvisa32.so.0')
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        try:
            self.view.start_freq = self.analyzer.start_freq
            self.view.stop_freq = self.analyzer.stop_freq
            self.view.npoints = self.analyzer.npoints
            # self.view.step_freq = self.analyzer.freq_step
            ports = self.analyzer.ports
        except VisaIOError as e:
            log.error(f"Error communicating with the analyzer: {e}")
            PopUpMessage(
                "Error connecting to analyzer.\nDo you have the right port?",
                MsgLevel.ERROR,
            )
            self.analyzer = None
            return
        ports = [f"S{''.join(p)}" for p in itertools.combinations(ports, 2)]
        self.view.pol1ComboBox.addItems(ports)
        self.view.pol2ComboBox.addItems(ports)
        log.info("Connected")
        self.view.frequencyGroupBox.setEnabled(True)
        if self.view.positionerGroupBox.isEnabled():
            self.view.experimentGroupBox.setEnabled(True)

    def connect_to_positioner(self) -> None:
        if self.positioner:
            log.info("Already connected.")
            return
        model = self.view.positioner_model
        port = self.view.positioner_port
        log.info(f"Connecting to positioner model [{model}] on port [{port}]")

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
        self.view.enable_experiement()

    def set_freq(self, setting: FreqSetting) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected", MsgLevel.WARNING)
            return

        try:
            if setting == FreqSetting.START:
                if freq := self.view.start_freq:
                    self.analyzer.start_freq = freq
            elif setting == FreqSetting.STOP:
                if freq := self.view.stop_freq:
                    self.analyzer.stop_freq = freq
            elif setting == FreqSetting.STEP:
                if freq := self.view.freq_step:
                    self.analyzer.freq_step = freq
        except VisaIOError as e:
            log.error(f"Failed to communicate with analyzer: {str(e)}")
            PopUpMessage("Failed to communicate with analyzer", MsgLevel.ERROR)
            return

    def set_npoints(self) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected")
            return

        if npoints := self.view.npoints:
            self.analyzer.npoints = npoints

    def init_polar_data_plot(self) -> None:
        log.debug("Initializing Data Polar Plot")
        self.polar_data_ax = self.view.dataPlotMplWidget.canvas.fig.add_subplot(
            projection='polar'
        )
        self.update_polar_data_plot()

    def init_over_freq_plot(self) -> None:
        log.debug("Initializing Over Frequency Plot")
        self.over_freq_ax = self.view.dataOverFreqPlotMplWidget.canvas.fig.add_subplot()
        self.update_over_freq_plot()

    def update_polar_data_plot(self) -> None:
        log.info("Updating Polar Data Plot")

        scale_min = self.view.polar_plot_scale_min
        scale_max = self.view.polar_plot_scale_max
        scale_div = self.view.polar_plot_scale_step
        freq = self.view.polar_plot_freq
        pol = self.view.polar_plot_pol

        self.polar_data_ax.clear()
        try:
            self.polar_data_ax.plot(
                self.ntwk_models[pol].azimuths,
                self.ntwk_models[pol].mags(freq, elevation=0),
                color='tab:blue',
            )
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        self.polar_data_ax.set_rlim(scale_min, scale_max)
        self.polar_data_ax.set_rticks(np.arange(scale_min, scale_max + 1, scale_div))
        self.polar_data_ax.set_thetagrids(np.arange(0, 360, 30))
        self.polar_data_ax.grid(True)
        self.polar_data_ax.set_theta_zero_location('N')

        self.view.dataPlotMplWidget.canvas.draw()

    def update_over_freq_plot(self) -> None:
        log.info("Updating Over Frequency Plot")

        scale_min = self.view.over_freq_scale_min
        scale_max = self.view.over_freq_scale_max
        scale_div = self.view.over_freq_scale_step

        self.over_freq_ax.clear()
        try:
            self.over_freq_ax.plot(
                self.ntwk_models[self.view.over_freq_pol].freqs,
                self.ntwk_models[self.view.over_freq_pol].mags(
                    azimuth=0.0, elevation=0.0
                ),
                color='tab:blue',
            )
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        self.over_freq_ax.set_ylim(scale_min, scale_max)
        self.over_freq_ax.set_yticks(np.arange(scale_min, scale_max + 1, scale_div))
        self.over_freq_ax.grid(True)
        self.over_freq_ax.set_xlabel("Frequency")
        self.over_freq_ax.set_ylabel("Gain [dB]")

        self.view.dataOverFreqPlotMplWidget.canvas.draw()

    def update_monitor_freqs(self) -> None:
        start = self.view.start_freq
        stop = self.view.stop_freq
        step = self.view.step_freq

        if start:
            self.view.dataPolarFreqSpinBox.setMinimum(start)
        if stop:
            self.view.dataPolarFreqSpinBox.setMaximum(stop)
        if step:
            self.view.dataPolarFreqSpinBox.setSingleStep(step)

    def clear_data(self) -> None:
        if len(self.ntwk_models[0]) == 0 and len(self.ntwk_models[1]) == 0:
            return
        actually_clear = ClearDataWarning(
            "This will delete all data. Are you sure?"
        ).warn()
        if actually_clear:
            self.ntwk_models = [NetworkModel(), NetworkModel()]

    def save_data(self) -> None:
        if len(self.ntwk_models[0]) == 0 and len(self.ntwk_models[1]) == 0:
            PopUpMessage("No data to save")
            return
        save_name, _ = QFileDialog.getSaveFileName()
        if save_name != "":
            log.info(f"Saving to {save_name}")
            with open(save_name, 'wb') as save_file:
                pickle.dump(self.ntwk_models, save_file)

    def load_data(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            log.info(f"Loading {file_name}")
            with open(file_name, 'rb') as data:
                try:
                    val = pickle.load(data)
                    self.ntwk_models = val
                except Exception:
                    PopUpMessage("Invalid file", MsgLevel.ERROR)
                    return

    def export_csv(self) -> None:
        if len(self.ntwk_models[0]) > 0 and len(self.ntwk_models[1]) > 0:
            which = WhichPol.ask()
            to_export = self.ntwk_models[which]
        elif len(self.ntwk_models[0]) > 0:
            to_export = self.ntwk_models[0]
        elif len(self.ntwk_models[1]) > 0:
            to_export = self.ntwk_models[1]
        else:
            PopUpMessage("No data to export")
            return

        save_name, _ = QFileDialog.getSaveFileName()
        if save_name != "":
            save_path = pathlib.Path(save_name)
            if save_path.suffix != ".csv":
                save_path = save_path.with_suffix(".csv")
                to_export.write_spreadsheet(save_name)

    def start_scan_thread(
        self,
        azimuths: Optional[np.ndarray] = None,
        elevations: Optional[np.ndarray] = None,
    ) -> None:
        self.thread = QThread()
        self.worker = ScanWorker()

        self.worker.azimuths = azimuths
        self.worker.elevations = elevations
        # self.worker.analyzer = self.analyzer
        self.worker.positioner_ = self.positioner
        # self.worker.ntwk_models = self.ntwk_models
        # self.worker.pol1 = self.view.pol_1
        # self.worker.pol2 = self.view.pol_2

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(lambda p: self.view.update_progress(p))
        self.worker.progress.connect(self.update_polar_data_plot)
        self.worker.progress.connect(self.update_over_freq_plot)
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
        self.thread.finished.connect(lambda: self.view.enable_jog_buttons())
