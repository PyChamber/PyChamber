import functools
import itertools
import logging
from enum import Enum, auto
from typing import Dict, Optional, Union

import cloudpickle as pickle
import numpy as np
from PyQt5.QtCore import QMutex, QThread
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from pyvisa.errors import LibraryError, VisaIOError
from serial.tools import list_ports
from skrf import Network
from skrf.vi import vna

from pychamber import positioner
from pychamber.jog_worker import JogAxis, JogWorker, JogZeroWorker
from pychamber.network_model import NetworkModel
from pychamber.positioner import PositionerError
from pychamber.scan_worker import ScanWorker
from pychamber.ui.calibration import CalibrationViewDialog, CalibrationWizard
from pychamber.ui.main_window import MainWindow
from pychamber.ui.pop_ups import ClearDataWarning, MsgLevel, PopUpMessage

log = logging.getLogger(__name__)
MUTEX = QMutex()


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


class PyChamberCtrl:
    analyzer_models = {
        "Agilent PNA": vna.PNA,
    }
    positioner_models = {
        "D6050": positioner.D6050,
    }

    cal: Optional[Dict] = None
    worker: Optional[Union[JogWorker, JogZeroWorker, ScanWorker]] = None

    def __init__(self, view: MainWindow) -> None:
        self.view = view
        self.ntwk_models: Dict[str, NetworkModel] = {}
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
        self.view.calibrationFileBrowseButton.clicked.connect(self.load_cal_file)
        self.view.calibrationButton.clicked.connect(self.exec_cal_dialog)
        self.view.calibrationViewButton.clicked.connect(self.exec_view_cal_dialog)

        # SpinBoxes
        self.view.polarPlotFreqSpinBox.valueChanged.connect(self.update_polar_plot)
        self.view.overFreqPlotAzSpinBox.valueChanged.connect(self.update_over_freq_plot)
        self.view.overFreqPlotElSpinBox.valueChanged.connect(self.update_over_freq_plot)

        # Combo Boxes
        self.view.polarPlotPolarizationComboBox.currentIndexChanged.connect(
            self.update_polar_plot
        )
        self.view.overFreqPlotPolarizationComboBox.currentIndexChanged.connect(
            self.update_over_freq_plot
        )

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
            step = self.view.az_jog_step
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
            step = self.view.el_jog_step
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
        if angle := self.view.az_jog_to:
            self.jog_az(angle=angle)

    def jog_el_to(self) -> None:
        if angle := self.view.el_jog_to:
            self.jog_el(angle=angle)

    def set_zero(self) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return
        self.positioner.zero()
        self.view.az_pos = 0.0
        self.view.el_pos = 0.0

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

        self.view.experimentCutProgressLabel.show()
        self.view.experimentCutProgressBar.show()
        self.view.update_polar_plot_freqs()

        azimuths = np.arange(
            self.view.az_extent_start, self.view.az_extent_stop, self.view.az_extent_step
        )
        elevations = np.arange(
            self.view.el_extent_start, self.view.el_extent_stop, self.view.el_extent_step
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

        self.view.update_polar_plot_freqs()

        azimuths = np.arange(
            self.view.az_extent_start, self.view.az_extent_stop, self.view.az_extent_step
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

        self.view.update_polar_plot_freqs()

        elevations = np.arange(
            self.view.el_extent_start, self.view.el_extent_stop, self.view.el_extent_step
        )

        try:
            self.start_scan_thread(elevations=elevations)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

    def connect_to_analyzer(self) -> None:
        if self.analyzer:
            return
        model = self.view.analyzer_model
        addr = self.view.analyzer_address

        if model == "" or addr == "":
            return

        try:
            log.info("Connecting to analyzer...")
            self.analyzer = self.analyzer_models[model](
                addr, backend='/usr/lib/x86_64-linux-gnu/libktvisa32.so.0'
            )
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        try:
            self.view.analyzer_start_freq = self.analyzer.start_freq
            self.view.analyzer_stop_freq = self.analyzer.stop_freq
            self.view.analyzer_n_points = self.analyzer.npoints
            # self.view.analyzer_freq_step = self.analyzer.freq_step
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
        self.view.analyzerPol1ComboBox.addItems(ports)
        self.view.analyzerPol2ComboBox.addItems(ports)
        log.info("Connected")
        self.view.enable_freq()
        self.view.enable_experiment()

    def connect_to_positioner(self) -> None:
        if self.positioner:
            return
        model = self.view.positioner_model
        port = self.view.positioner_port

        if model == "" or port == "":
            return

        log.info("Connecting to positioner...")
        try:
            self.positioner = self.positioner_models[model](port)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        self.view.az_pos = self.positioner.azimuth_deg
        self.view.el_pos = self.positioner.elevation_deg
        log.info("Connected")
        self.view.enable_jog()
        self.view.enable_experiment()

    def set_freq(self, setting: FreqSetting) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected", MsgLevel.WARNING)
            return

        try:
            if setting == FreqSetting.START:
                if freq := self.view.analyzer_start_freq:
                    self.analyzer.start_freq = freq.real
            elif setting == FreqSetting.STOP:
                if freq := self.view.analyzer_stop_freq:
                    self.analyzer.stop_freq = freq.real
            # elif setting == FreqSetting.STEP:
            #     if freq := self.view.analyzer_freq_step:
            #         self.analyzer.freq_step = freq.real
        except VisaIOError as e:
            log.error(f"Failed to communicate with analyzer: {str(e)}")
            PopUpMessage("Failed to communicate with analyzer", MsgLevel.ERROR)
            return

    def set_npoints(self) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected")
            return

        if npoints := self.view.analyzer_n_points:
            self.analyzer.npoints = npoints

    def exec_cal_dialog(self) -> None:
        dialog = CalibrationWizard(self.analyzer)
        dialog.exec_()
        val = dialog.get_cal()
        if val:
            self.view.cal_file_name = val[0]
            self.cal = val[1]

    def exec_view_cal_dialog(self) -> None:
        dialog = CalibrationViewDialog(self.cal_file)
        dialog.exec_()

    def load_cal_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            self.view.cal_file_name = file_name
            with open(file_name, 'rb') as f:
                self.cal_file = pickle.load(f)
                self.view.calibrationViewButton.setEnabled(True)

    def update_polar_plot(self) -> None:
        freq = str(self.view.polar_plot_freq)

        pol = self.view.polar_plot_pol
        if pol not in self.ntwk_models:
            return
        if len(self.ntwk_models[pol]) == 0:
            return

        azimuths = np.deg2rad(self.ntwk_models[pol].azimuths.reshape(-1, 1))
        mags = self.ntwk_models[pol].mags(freq, elevation=0).reshape(-1, 1)

        self.view.update_polar_plot(azimuths, mags)

    def update_over_freq_plot(self) -> None:
        pol = self.view.over_freq_plot_pol
        if pol not in self.ntwk_models:
            return
        if len(self.ntwk_models[pol]) == 0:
            return

        freqs = self.ntwk_models[pol].freqs.reshape(-1, 1)
        mags = self.ntwk_models[pol].mags(azimuth=0.0, elevation=0.0).reshape(-1, 1)

        self.view.update_over_freq_plot(freqs, mags)

    def clear_data(self) -> None:
        if len(self.ntwk_models) == 0:
            return
        actually_clear = ClearDataWarning(
            "This will delete all data. Are you sure?"
        ).warn()
        if actually_clear:
            self.ntwk_models = {}

    def save_data(self) -> None:
        if len(self.ntwk_models) == 0:
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

            self.view.update_plot_pols(list(self.ntwk_models.keys()))

            temp = next(iter(val.values()))
            self.view.polarPlotFreqSpinBox.setMinimum(temp.freqs[0])
            self.view.polarPlotFreqSpinBox.setMaximum(temp.freqs[-1])
            self.view.polarPlotFreqSpinBox.setSingleStep(temp.freqs[1] - temp.freqs[0])

            self.view.polarPlotPolarizationComboBox.blockSignals(False)
            self.view.polarPlotFreqSpinBox.blockSignals(False)
            self.view.overFreqPlotPolarizationComboBox.blockSignals(False)

            self.update_over_freq_plot()
            self.view.overFreqPlot.auto_scale()
            self.update_polar_plot()
            self.view.polarPlot.auto_scale()

    def export_csv(self) -> None:
        if len(self.ntwk_models) == 0:
            PopUpMessage("No data to export")
            return

        pols = list(self.ntwk_models.keys())
        which, ok = QInputDialog.getItem(
            None,
            "Which Polarization",
            "Polarizations:",
            pols,
            editable=False,  # type: ignore
        )
        if not ok:
            return
        to_export = self.ntwk_models[which]
        to_export.write_spreadsheet(file_name='testing.xlsx')

        # save_name, _ = QFileDialog.getSaveFileName()
        # if save_name != "":
        #     save_path = pathlib.Path(save_name)
        #     if save_path.suffix != ".csv":
        #         save_path = save_path.with_suffix(".csv")
        #         to_export.write_spreadsheet(save_name)

    def update_ntwk_models(self, data: Network) -> None:
        log.info(f"\n{data[0].s_db}")
        if pol1:=self.view.pol_1:
            label = pol1[0] if pol1[0] != "" else "Polarization 1"
            port = pol1[1]
            temp = Network(
                frequency=data.frequency, s=data.s[:, port[0] - 1, port[1] - 1], params=data.params
            )
            if self.cal is not None:
                temp = temp - self.cal['data'][label]
            self.ntwk_models[label] = self.ntwk_models[label].append(temp)
        if pol2:=self.view.pol_2:
            label = pol2[0] if pol2[0] != "" else "Polarization 2"
            port = pol2[1]
            temp = Network(
                frequency=data.frequency, s=data.s[:, port[0] - 1, port[1] - 1], params=data.params
            )
            if self.cal is not None:
                temp = temp - self.cal['data'][label]
            self.ntwk_models[label] = self.ntwk_models[label].append(temp)

            self.update_polar_plot()
            self.update_over_freq_plot()

    def start_scan_thread(
        self,
        azimuths: Optional[np.ndarray] = None,
        elevations: Optional[np.ndarray] = None,
    ) -> None:
        assert self.positioner
        assert self.analyzer

        if pol1 := self.view.pol_1:
            label1 = pol1[0] if pol1[0] != "" else "Polarization 1"
        if pol2 := self.view.pol_2:
            label2 = pol2[0] if pol2[0] != "" else "Polarization 2"

        if pol1 is None and pol2 is None:
            log.info("No polarizations selected.")
            return

        if len(self.ntwk_models) == 0:
            self.ntwk_models = {
                label1: NetworkModel(),
                label2: NetworkModel(),
            }

        self.view.update_plot_pols(list(self.ntwk_models.keys()))

        self.thread = QThread()
        self.worker = ScanWorker(
            MUTEX,
            self.positioner,
            self.analyzer,
            azimuths,
            elevations,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(lambda p: setattr(self.view, 'total_progress', p))
        self.worker.finished.connect(self.update_polar_plot)
        self.worker.finished.connect(self.update_over_freq_plot)
        if self.view.experimentCutProgressBar.isVisible():
            self.worker.cutProgress.connect(
                lambda p: setattr(self.view, 'cut_progress', p)
            )
        self.worker.timeUpdate.connect(lambda t: setattr(self.view, 'time_remaining', t))
        self.worker.azMoveComplete.connect(lambda p: setattr(self.view, 'az_pos', p))
        self.worker.elMoveComplete.connect(lambda p: setattr(self.view, 'el_pos', p))
        self.worker.dataAcquired.connect(lambda data: self.update_ntwk_models(data))

        self.thread.start()

        self.view.analyzerGroupBox.setEnabled(False)
        self.view.positionerGroupBox.setEnabled(False)
        self.view.experimentFullScanButton.setEnabled(False)
        self.view.experimentAzScanButton.setEnabled(False)
        self.view.experimentElScanButton.setEnabled(False)
        self.view.experimentAbortButton.setEnabled(True)

        self.view.experimentAbortButton.clicked.connect(lambda: setattr(self.worker, 'abort', True))

        self.thread.finished.connect(lambda: self.view.analyzerGroupBox.setEnabled(True))
        self.thread.finished.connect(
            lambda: self.view.positionerGroupBox.setEnabled(True)
        )
        self.thread.finished.connect(lambda: self.view.experimentFullScanButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.view.experimentAzScanButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.view.experimentElScanButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.view.experimentAbortButton.setEnabled(False))
        self.thread.finished.connect(lambda: setattr(self.view, 'total_progress', 100))
        self.thread.finished.connect(lambda: setattr(self.view, 'time_remaining', 0.0))
        self.thread.finished.connect(lambda: log.info("Scan complete"))

        if self.view.experimentCutProgressBar.isVisible():
            self.thread.finished.connect(lambda: self.view.experimentCutProgressBar.hide())

    def jog_thread(self, axis: JogAxis, angle: float, relative: bool) -> None:
        assert self.positioner
        self.thread = QThread()
        self.worker = JogWorker(MUTEX, axis, angle, self.positioner, relative)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.azMoveComplete.connect(lambda p: setattr(self.view, 'az_pos', p))
        self.worker.elMoveComplete.connect(lambda p: setattr(self.view, 'el_pos', p))

        self.thread.start()

        self.view.disable_jog_buttons()
        self.thread.finished.connect(self.view.enable_jog_buttons)

    def jog_zero_thread(self) -> None:
        assert self.positioner

        self.thread = QThread()
        self.worker = JogZeroWorker(MUTEX, self.positioner)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.azMoveComplete.connect(lambda p: setattr(self.view, 'az_pos', p))
        self.worker.elMoveComplete.connect(lambda p: setattr(self.view, 'el_pos', p))

        self.thread.start()

        self.view.disable_jog_buttons()
        self.thread.finished.connect(self.view.enable_jog_buttons)
