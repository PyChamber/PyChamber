import functools
import itertools
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union

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
from pychamber.classes.polarization import Polarization
from pychamber.classes.positioner import PositionerError
from pychamber.classes.scan_worker import ScanWorker
from pychamber.classes.settings_manager import SettingsManager
from pychamber.lib import load
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


class ScanType(Enum):
    FULL = auto()
    AZIMUTH = auto()
    ELEVATION = auto()


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
        self.pyconsole = PyConsole(theme=self.settings['python-theme'])

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
        self.view.experimentFullScanButton.clicked.connect(
            functools.partial(self.scan, scan_type=ScanType.FULL)
        )
        self.view.experimentAzScanButton.clicked.connect(
            functools.partial(self.scan, scan_type=ScanType.AZIMUTH)
        )
        self.view.experimentElScanButton.clicked.connect(
            functools.partial(self.scan, scan_type=ScanType.ELEVATION)
        )
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
                self.start_jog_thread(JogAxis.AZIMUTH, diff, relative=True)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            try:
                self.start_jog_thread(JogAxis.AZIMUTH, angle, relative=False)
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
                self.start_jog_thread(JogAxis.ELEVATION, diff, relative=True)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            try:
                self.start_jog_thread(JogAxis.ELEVATION, angle, relative=False)
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
            self.start_jog_zero_thread()
        elif az_not_at_zero:
            self.jog_az(angle=0.0)
        elif el_not_at_zero:
            self.jog_el(angle=0.0)

    def scan(self, scan_type: ScanType) -> None:
        if not self.positioner:
            PopUpMessage("Not connected")
            return

        self.ntwk_models = {}
        polarizations: List[Polarization] = []

        if (pol1 := self.view.pol_1) is not None:
            label = pol1.label if pol1.label != "" else "Polarization 1"
            self.ntwk_models[label] = NetworkModel()
            polarizations.append(Polarization(label, pol1.param))
        if (pol2 := self.view.pol_2) is not None:
            label = pol2.label if pol2.label != "" else "Polarization 2"
            self.ntwk_models[label] = NetworkModel()
            polarizations.append(Polarization(label, pol2.param))

        if pol1 is None and pol2 is None:
            log.info("No polarizations selected.")
            return

        self.view.experimentCutProgressLabel.show()
        self.view.experimentCutProgressBar.show()
        self.view.update_plot_pols([pol.label for pol in polarizations])

        if self.view.analyzer_start_freq is not None:
            self.view.polar_plot_freq = self.view.analyzer_start_freq

        az_min = az_max = az_step = 0.0
        el_min = el_max = el_step = 0.0
        azimuths = np.asarray([0])
        elevations = np.asarray([0])

        if scan_type == ScanType.FULL or scan_type == ScanType.AZIMUTH:
            azimuths = np.arange(
                az_min := self.view.az_extent_start,
                az_max := self.view.az_extent_stop,
                az_step := self.view.az_extent_step,
            )

        if scan_type == ScanType.FULL or scan_type == ScanType.ELEVATION:
            elevations = np.arange(
                el_min := self.view.el_extent_start,
                el_max := self.view.el_extent_stop,
                el_step := self.view.el_extent_step,
            )

        self.update_over_freq_plot_lims(
            az_min=az_min,
            az_max=az_max,
            az_step=az_step,
            el_min=el_min,
            el_max=el_max,
            el_step=el_step,
        )

        try:
            self.start_scan_thread(polarizations, azimuths, elevations)
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
            self.analyzer = None
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
        log.info("Connected")

        self.view.az_pos = self.positioner.azimuth_deg
        self.view.el_pos = self.positioner.elevation_deg
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

    def update_over_freq_plot_lims(
        self,
        az_min: float = 0.0,
        az_max: float = 0.0,
        az_step: float = 0.0,
        el_min: float = 0.0,
        el_max: float = 0.0,
        el_step: float = 0.0,
    ) -> None:
        self.view.overFreqPlotAzSpinBox.setMinimum(az_min)
        self.view.overFreqPlotAzSpinBox.setMaximum(az_max)
        self.view.overFreqPlotAzSpinBox.setSingleStep(az_step)

        self.view.overFreqPlotElSpinBox.setMinimum(el_min)
        self.view.overFreqPlotElSpinBox.setMaximum(el_max)
        self.view.overFreqPlotElSpinBox.setSingleStep(el_step)

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

        azimuths = np.deg2rad(self.ntwk_models[pol].azimuths)
        mags = self.ntwk_models[pol].mags(
            freq=self.view.polar_plot_freq.render(), elevation=0
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
        try:
            mags = self.ntwk_models[pol].mags(azimuth=az, elevation=el).reshape(-1, 1)
        except IndexError:  # FIXME
            return

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
            try:
                val = load(file_name)
                self.ntwk_models = val
            except Exception:
                PopUpMessage("Invalid file", MsgLevel.ERROR)
                return

            self.view.update_plot_pols(list(self.ntwk_models.keys()))

            azs = list(self.ntwk_models.values())[0].azimuths
            az_step = (azs[1] - azs[0]) if len(azs) > 1 else 0
            els = list(self.ntwk_models.values())[0].elevations
            el_step = (els[1] - els[0]) if len(els) > 1 else 0

            self.update_over_freq_plot_lims(
                az_min=min(azs),
                az_max=max(azs),
                az_step=az_step,
                el_min=min(els),
                el_max=max(els),
                el_step=el_step,
            )
            self.update_over_freq_plot()
            self.auto_scale_over_freq()

            self.view.polar_plot_freq = list(self.ntwk_models.values())[0].freqs.min()
            self.update_polar_plot()
            self.auto_scale_polar()
            self.update_python_with_ntwk_models()

    def show_settings(self) -> None:
        diag = SettingsDialog(self.settings, parent=None)
        diag.exec_()

    def settings_updated(self, key: str) -> None:
        if key == "backend":
            self.update_analyzer_ports()

    def show_python(self) -> None:
        if self.pyconsole is None:
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

    def receive_experiment_data(self, data: Tuple[str, Network]) -> None:
        label = data[0]
        ntwk = data[1]

        log.debug(f"Updating {label}")

        if self.cal is not None:
            ntwk = ntwk - self.cal['data'][label]
        self.ntwk_models[label] = self.ntwk_models[label].append(ntwk)

        if self.view.polar_plot_pol == label:
            self.update_polar_plot()
            if self.settings['polar-autoscale']:
                self.auto_scale_polar()

        if self.view.over_freq_plot_pol == label:
            self.update_over_freq_plot()
            if self.settings['overfreq-autoscale']:
                self.auto_scale_over_freq()

    def start_scan_thread(
        self,
        polarizations: List[Polarization],
        azimuths: np.ndarray,
        elevations: np.ndarray,
    ) -> None:
        assert self.positioner
        assert self.analyzer

        self.thread = QThread()
        self.worker = ScanWorker(
            MUTEX,
            self.positioner,
            self.analyzer,
            polarizations,
            azimuths,
            elevations,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(lambda p: setattr(self.view, 'total_progress', p))
        if self.view.experimentCutProgressBar.isVisible():
            self.worker.cutProgress.connect(
                lambda p: setattr(self.view, 'cut_progress', p)
            )
        self.worker.timeUpdate.connect(lambda t: setattr(self.view, 'time_remaining', t))
        self.worker.azMoveComplete.connect(lambda p: setattr(self.view, 'az_pos', p))
        self.worker.elMoveComplete.connect(lambda p: setattr(self.view, 'el_pos', p))
        self.worker.dataAcquired.connect(lambda data: self.receive_experiment_data(data))

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

        self.thread.start()

    def start_jog_thread(self, axis: JogAxis, angle: float, relative: bool) -> None:
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

    def start_jog_zero_thread(self) -> None:
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
