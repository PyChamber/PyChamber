import functools
import itertools
from enum import Enum, auto
from typing import Dict, Optional, Union

import cloudpickle as pickle
import numpy as np
from PyQt5.QtCore import QMutex, QThread
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pyvisa.errors import LibraryError, VisaIOError
from serial.tools import list_ports
from skrf import Network
from skrf.vi import vna

from pychamber.classes import positioner
from pychamber.classes.jog_worker import JogAxis, JogWorker, JogZeroWorker
from pychamber.classes.logger import log
from pychamber.classes.network_model import NetworkModel
from pychamber.classes.positioner import PositionerError
from pychamber.classes.scan_worker import ScanWorker
from pychamber.classes.settings_manager import SettingsManager
from pychamber.ui.about import AboutPyChamber
from pychamber.ui.calibration import CalibrationViewDialog, CalibrationWizard
from pychamber.ui.log_viewer import LogViewer
from pychamber.ui.main_window import MainWindow
from pychamber.ui.pop_ups import MsgLevel, PopUpMessage
from pychamber.ui.pyconsole import PyConsole
from pychamber.ui.settings_dialog import SettingsDialog

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
    pyconsole: Optional[PyConsole] = None

    def __init__(self, view: MainWindow) -> None:
        self.view: MainWindow = view
        self.ntwk_models: Dict[str, NetworkModel] = {}
        self.analyzer: Optional[vna.VNA] = None
        self.positioner: Optional[positioner.Positioner] = None

        self.settings = SettingsManager()

        self.connect_signals()

        self.update_analyzer_ports()
        self.update_analyzer_models()
        self.update_positioner_ports()
        self.update_positioner_models()

        self.view.updateFromSettings(self.settings)

    def connect_signals(self) -> None:
        # Menu
        self.view.save.triggered.connect(self.save_data)
        self.view.load.triggered.connect(self.load_data)
        self.view.settings.triggered.connect(self.show_settings)
        self.view.python_interpreter.triggered.connect(self.show_python)
        self.view.about.triggered.connect(self.about)
        self.view.log.triggered.connect(self.show_log)
        self.view.closeEvent = self.closeEvent  # type: ignore
        self.view.quit.triggered.connect(self.view.close)

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
        self.view.calibrationFileBrowseButton.clicked.connect(self.load_cal_file)
        self.view.calibrationButton.clicked.connect(self.exec_cal_dialog)
        self.view.calibrationViewButton.clicked.connect(self.exec_view_cal_dialog)
        self.view.polarPlotAutoScaleButton.clicked.connect(self.auto_scale_polar)
        self.view.overFreqPlotAutoScaleButton.clicked.connect(self.auto_scale_over_freq)

        # SpinBoxes
        self.view.overFreqPlotAzSpinBox.valueChanged.connect(self.update_over_freq_plot)
        self.view.overFreqPlotElSpinBox.valueChanged.connect(self.update_over_freq_plot)
        self.view.positionerAzExtentStartSpinBox.valueChanged.connect(
            lambda val: self.settings.setval('az-start', val)
        )
        self.view.positionerAzExtentStopSpinBox.valueChanged.connect(
            lambda val: self.settings.setval('az-stop', val)
        )
        self.view.positionerAzExtentStepSpinBox.valueChanged.connect(
            lambda val: self.settings.setval('az-step', val)
        )
        self.view.positionerElExtentStartSpinBox.valueChanged.connect(
            lambda val: self.settings.setval('el-start', val)
        )
        self.view.positionerElExtentStopSpinBox.valueChanged.connect(
            lambda val: self.settings.setval('el-stop', val)
        )
        self.view.positionerElExtentStepSpinBox.valueChanged.connect(
            lambda val: self.settings.setval('el-step', val)
        )

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
        self.view.analyzerStepFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.STEP)
        )
        self.view.analyzerNPointsLineEdit.returnPressed.connect(self.set_npoints)

        self.view.analyzerPol1LineEdit.textChanged.connect(
            lambda val: self.settings.setval('pol1-label', val)
        )
        self.view.analyzerPol2LineEdit.textChanged.connect(
            lambda val: self.settings.setval('pol2-label', val)
        )
        self.view.polarPlotFreqLineEdit.returnPressed.connect(self.update_polar_plot)

        self.settings.settingsChanged.connect(self.settings_updated)

    def closeEvent(self, event) -> None:
        warning = QMessageBox()
        warning.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        warning.setDefaultButton(QMessageBox.Cancel)
        warning.setText("Are you sure you want to quit?\n(Any unsaved data will be LOST)")

        resp = warning.exec_()
        if resp == QMessageBox.Yes:
            del self.settings
            event.accept()
        else:
            event.ignore()

    def update_positioner_ports(self) -> None:
        self.view.positionerPortComboBox.clear()
        ports = [p.device for p in list_ports.comports()]
        self.view.positionerPortComboBox.addItems(ports)
        self.view.positionerPortComboBox.setCurrentText(self.settings['positioner-port'])

    def update_analyzer_ports(self) -> None:
        self.view.analyzerAddressComboBox.clear()

        backend = self.settings['backend']

        # If we can't find the library, default to pyvisa-py
        try:
            addrs = vna.VNA.available(backend=backend)
        except LibraryError:
            addrs = vna.VNA.available()

        self.view.analyzerAddressComboBox.addItems(addrs)
        self.view.analyzerAddressComboBox.setCurrentText(self.settings['analyzer-addr'])

    def update_analyzer_models(self) -> None:
        self.view.analyzerModelComboBox.clear()
        self.view.analyzerModelComboBox.addItems(list(self.analyzer_models.keys()))
        self.view.analyzerModelComboBox.setCurrentText(self.settings['analyzer-model'])

    def update_positioner_models(self) -> None:
        self.view.positionerModelComboBox.clear()
        self.view.positionerModelComboBox.addItems(list(self.positioner_models.keys()))
        self.view.positionerModelComboBox.setCurrentText(
            self.settings['positioner-model']
        )

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

        azimuths = np.arange(
            self.view.az_extent_start,
            self.view.az_extent_stop + self.view.az_extent_step,
            self.view.az_extent_step,
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

        elevations = np.arange(
            self.view.el_extent_start,
            self.view.el_extent_stop + self.view.el_extent_step,
            self.view.el_extent_step,
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
                addr, backend=self.settings['backend']
            )
            self.settings["analyzer-model"] = model
            self.settings["analyzer-addr"] = addr
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        try:
            self.view.analyzer_start_freq = self.analyzer.start_freq()
            self.view.analyzer_stop_freq = self.analyzer.stop_freq()
            self.view.analyzer_n_points = self.analyzer.npoints()
            self.view.analyzer_freq_step = self.analyzer.freq_step()
            ports = self.analyzer.ports
        except VisaIOError as e:
            log.error(f"Error communicating with the analyzer: {e}")
            PopUpMessage(
                "Error connecting to analyzer.\nDo you have the right port?",
                MsgLevel.ERROR,
            )
            self.analyzer = None
            return
        ports = [f"S{''.join(p)}" for p in itertools.permutations(ports, 2)] + [
            f"S{p}{p}" for p in ports
        ]
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
            self.settings["positioner-model"] = model
            self.settings["positioner-port"] = port
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
                    self.analyzer.set_start_freq(freq.real)
            elif setting == FreqSetting.STOP:
                if freq := self.view.analyzer_stop_freq:
                    self.analyzer.set_stop_freq(freq.real)
            elif setting == FreqSetting.STEP:
                if freq := self.view.analyzer_freq_step:
                    self.analyzer.set_freq_step(freq.real)
                    self.view.analyzer_n_points = self.analyzer.npoints()
        except VisaIOError as e:
            log.error(f"Failed to communicate with analyzer: {str(e)}")
            PopUpMessage("Failed to communicate with analyzer", MsgLevel.ERROR)
            return

    def set_npoints(self) -> None:
        if not self.analyzer:
            PopUpMessage("Not connected")
            return

        if npoints := self.view.analyzer_n_points:
            self.analyzer.set_npoints(npoints)
            self.view.analyzer_freq_step = self.analyzer.freq_step()

    def exec_cal_dialog(self) -> None:
        dialog = CalibrationWizard(self.analyzer)
        dialog.exec_()
        val = dialog.get_cal()
        if val:
            self.view.cal_file_name = val[0]
            self.settings['cal-file'] = val[0]
            self.cal = val[1]

    def exec_view_cal_dialog(self) -> None:
        dialog = CalibrationViewDialog(self.cal_file)
        dialog.exec_()

    def load_cal_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            self.view.cal_file_name = file_name
            self.settings['cal-file'] = file_name
            with open(file_name, 'rb') as f:
                self.cal_file = pickle.load(f)
                self.view.calibrationViewButton.setEnabled(True)

    def update_polar_plot(self) -> None:
        if not self.view.polar_plot_freq:
            return
        pol = self.view.polar_plot_pol
        if pol not in self.ntwk_models:
            return
        if len(self.ntwk_models[pol]) == 0:
            return

        freq = self.view.polar_plot_freq
        freqs = self.ntwk_models[pol].freqs
        if (freq < min(freqs)) or (freq > max(freqs)):
            return

        array = np.asarray(freqs)
        idx = (np.abs(array - freq)).argmin()
        freq = array[idx]

        azimuths = np.deg2rad(self.ntwk_models[pol].azimuths.reshape(-1, 1))
        mags = (
            self.ntwk_models[pol]
            .mags(freq=self.view.polar_plot_freq.render(), elevation=0)
            .reshape(-1, 1)
        )

        self.view.update_polar_plot(azimuths, mags)

    def auto_scale_polar(self) -> None:
        self.view.polarPlot.auto_scale()
        self.view.polar_plot_min = int(self.view.polarPlot.rmin)
        self.view.polar_plot_max = int(self.view.polarPlot.rmax)
        self.view.polar_plot_step = int(self.view.polarPlot.rstep)

    def update_over_freq_plot(self) -> None:
        pol = self.view.over_freq_plot_pol
        az = self.view.over_freq_plot_az
        el = self.view.over_freq_plot_el
        if pol not in self.ntwk_models:
            return
        if len(self.ntwk_models[pol]) == 0:
            return

        freqs = self.ntwk_models[pol].freqs.reshape(-1, 1)
        mags = self.ntwk_models[pol].mags(azimuth=az, elevation=el).reshape(-1, 1)

        self.view.update_over_freq_plot(freqs, mags)

    def auto_scale_over_freq(self) -> None:
        self.view.overFreqPlot.auto_scale()
        self.view.over_freq_plot_min = int(self.view.overFreqPlot.ymin)
        self.view.over_freq_plot_max = int(self.view.overFreqPlot.ymax)
        self.view.over_freq_plot_step = int(self.view.overFreqPlot.ystep)

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

            self.update_over_freq_plot()
            self.view.overFreqPlot.auto_scale()
            self.update_polar_plot()
            self.view.polarPlot.auto_scale()

    def show_settings(self) -> None:
        diag = SettingsDialog(self.settings, parent=None)
        diag.exec_()

    def settings_updated(self, key: str) -> None:
        if key == "backend":
            self.update_analyzer_ports()

    def show_python(self) -> None:
        self.pyconsole = PyConsole(theme=self.settings['python-theme'])
        self.pyconsole.setMinimumSize(600, 600)
        self.pyconsole.show()
        self.pyconsole.eval_in_thread()

    def update_python_with_ntwk_models(self) -> None:
        if self.pyconsole:
            self.pyconsole.push_local_ns("measurements", self.ntwk_models)

    def about(self) -> None:
        AboutPyChamber.display()

    def show_log(self) -> None:
        LogViewer.display()

    def update_pol1_ntwk_model(self, data: Network) -> None:
        if pol1 := self.view.pol_1:
            label = pol1.label if pol1.label != "" else "Polarization 1"
            if self.cal is not None:
                data = data - self.cal['data'][label]
            self.ntwk_models[label].append(data)

            self.update_polar_plot()
            self.update_over_freq_plot()

    def update_pol2_ntwk_model(self, data: Network) -> None:
        if pol2 := self.view.pol_2:
            label = pol2.label if pol2.label != "" else "Polarization 2"
            if self.cal is not None:
                data = data - self.cal['data'][label]
            self.ntwk_models[label].append(data)

            self.update_polar_plot()
            self.update_over_freq_plot()

    def recalc_ntwk_models(self) -> None:
        # When taking data, we directly append to the internal NetworkSet's
        # list. This doesn't update the statistics that are generated in
        # NetworkSet's constructor. This function simply reconstructs the
        # NetworkModel to generate those statistics for the user.
        if pol1 := self.view.pol_1:
            label = pol1.label if pol1.label != "" else "Polarization 1"
            self.ntwk_models[label] = NetworkModel(self.ntwk_models[label].to_dict())

        if pol2 := self.view.pol_2:
            label = pol2.label if pol2.label != "" else "Polarization 2"
            self.ntwk_models[label] = NetworkModel(self.ntwk_models[label].to_dict())

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
            label1 = pol1.label if pol1.label != "" else "Polarization 1"
        if pol2 := self.view.pol_2:
            label2 = pol2.label if pol2.label != "" else "Polarization 2"

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
            (pol1, pol2),
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
        self.worker.pol1Acquired.connect(lambda data: self.update_pol1_ntwk_model(data))
        self.worker.pol2Acquired.connect(lambda data: self.update_pol2_ntwk_model(data))

        self.thread.start()

        self.view.analyzerGroupBox.setEnabled(False)
        self.view.positionerGroupBox.setEnabled(False)
        self.view.experimentFullScanButton.setEnabled(False)
        self.view.experimentAzScanButton.setEnabled(False)
        self.view.experimentElScanButton.setEnabled(False)
        self.view.python_interpreter.setEnabled(False)
        self.view.experimentAbortButton.setEnabled(True)

        self.view.experimentAbortButton.clicked.connect(
            lambda: setattr(self.worker, 'abort', True)
        )

        self.thread.finished.connect(lambda: self.view.analyzerGroupBox.setEnabled(True))
        self.thread.finished.connect(
            lambda: self.view.positionerGroupBox.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.view.experimentFullScanButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.view.experimentAzScanButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.view.experimentElScanButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.view.python_interpreter.setEnabled(True)
        )
        self.thread.finished.connect(self.recalc_ntwk_models)
        self.thread.finished.connect(self.update_python_with_ntwk_models)
        self.thread.finished.connect(
            lambda: self.view.experimentAbortButton.setEnabled(False)
        )
        self.thread.finished.connect(lambda: setattr(self.view, 'total_progress', 100))
        self.thread.finished.connect(lambda: setattr(self.view, 'time_remaining', 0.0))
        self.thread.finished.connect(lambda: log.info("Scan complete"))

        if self.view.experimentCutProgressBar.isVisible():
            self.thread.finished.connect(
                lambda: self.view.experimentCutProgressBar.hide()
            )

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
