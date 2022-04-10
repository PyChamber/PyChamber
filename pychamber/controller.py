import functools
import itertools
import logging
import time
from enum import Enum, auto
from typing import Callable, Optional

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from pyvisa.errors import VisaIOError
from serial.tools import list_ports
from skrf.vi import vna

from pychamber import positioner
from pychamber.app import AppUI, MsgLevel, PopUpMessage
from pychamber.network_model import NetworkModel
from pychamber.positioner import PositionerError

log = logging.getLogger(__name__)


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


class Worker(QObject):
    finished = pyqtSignal()
    func: Optional[Callable] = None

    def run(self) -> None:
        if self.func:
            self.func()
        self.finished.emit()


class PyChamberCtrl:
    analyzer_models = {
        "Agilent PNA": vna.PNA,
    }
    positioner_models = {
        "D6050": positioner.D6050,
    }

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
        self.view.abortButton.clicked.connect(self.abort)
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

        # Line Edits
        self.view.startFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.START)
        )
        self.view.stopFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.STOP)
        )
        self.view.stepFreqLineEdit.returnPressed.connect(
            functools.partial(self.set_freq, FreqSetting.STEP)
        )
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
        ports = vna.VNA.available()
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
                self.positioner.move_azimuth_relative(diff)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                self.view.enable_jog_buttons()
                return
        elif angle is not None:
            log.info(f"Jogging azimuth to {angle}")
            self.positioner.move_azimuth_absolute(angle)

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
                self.positioner.move_elevation_relative(diff)
            except PositionerError as e:
                log.error(str(e))
                PopUpMessage(str(e), MsgLevel.ERROR)
                return
        elif angle is not None:
            log.info(f"Jogging elevation to {angle}")
            self.positioner.move_elevation_absolute(angle)

        self.view.el_pos = self.positioner.current_elevation

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
        if not self.positioner or not self.analyzer:
            PopUpMessage("Not connected")
            return

        self.view.disable_jog()
        self.view.disable_freq()
        self.update_monitor_freqs()

        azimuths = np.arange(self.view.az_start, self.view.az_stop, self.view.az_step)
        elevations = np.arange(self.view.el_start, self.view.el_stop, self.view.el_step)
        total_iters = len(azimuths) * len(elevations)

        pol1 = self.view.pol1
        pol2 = self.view.pol2

        try:
            log.info("Starting full scan")
            self.view.reset_progress()
            for i, az in enumerate(azimuths):
                self.jog_az(angle=az)
                for j, el in enumerate(elevations):
                    start = time.time()
                    self.jog_el(angle=el)
                    if pol1:
                        self.ntwk_models[0].append(self.analyzer.get_snp_network(pol1))
                    if pol2:
                        self.ntwk_models[1].append(self.analyzer.get_snp_network(pol2))
                    end = time.time()

                    completed = i * len(azimuths) + j
                    remaining = total_iters - completed
                    self.view.update_progress(completed, total_iters)
                    self.view.update_time_remaining(end - start, remaining)
                    self.update_polar_data_plot()
                    self.update_over_freq_plot()
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

        log.info("Full Scan Done")
        self.view.enable_jog()
        self.view.enable_freq()

    def az_scan(self) -> None:
        if not self.positioner or not self.analyzer:
            PopUpMessage("Not connected")
            return

        self.view.disable_jog()
        self.view.disable_freq()
        self.update_monitor_freqs()

        azimuths = np.arange(self.view.az_start, self.view.az_stop, self.view.az_step)
        total_iters = len(azimuths)

        pol1 = self.view.pol1
        pol2 = self.view.pol2

        try:
            log.info("Starting azimuth scan")
            self.view.reset_progress()
            for i, az in enumerate(azimuths):
                start = time.time()
                self.jog_az(angle=az)
                if pol1:
                    self.ntwk_models[0].append(self.analyzer.get_snp_network(pol1))
                if pol2:
                    self.ntwk_models[1].append(self.analyzer.get_snp_network(pol2))
                end = time.time()

                remaining = total_iters - i
                self.view.update_progress(i, total_iters)
                self.view.update_time_remaining(end - start, remaining)
                self.update_polar_data_plot()
                self.update_over_freq_plot()
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

        log.info("Azimuth scan done")

        self.view.enable_freq()
        self.view.enable_jog()

    def el_scan(self) -> None:
        if not self.positioner or not self.analyzer:
            PopUpMessage("Not connected")
            return

        self.view.disable_jog()
        self.view.disable_freq()
        self.update_monitor_freqs()

        elevations = np.arange(self.view.el_start, self.view.el_stop, self.view.el_step)
        total_iters = len(elevations)

        pol1 = self.view.pol1
        pol2 = self.view.pol2

        try:
            log.info("Starting elevation scan")
            self.view.reset_progress()
            for i, el in enumerate(elevations):
                start = time.time()
                self.view.progressBar.setValue(int(i / total_iters))
                self.jog_el(angle=el)
                if pol1:
                    self.ntwk_models[0].append(self.analyzer.get_snp_network(pol1))
                if pol2:
                    self.ntwk_models[1].append(self.analyzer.get_snp_network(pol2))
                end = time.time()

                remaining = total_iters - i
                self.view.update_progress(i, total_iters)
                self.view.update_time_remaining(end - start, remaining)
                self.update_polar_data_plot()
                self.update_over_freq_plot()
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return

        log.info("Elevation scan done")
        self.view.enable_jog()
        self.view.enable_freq()

    def abort(self) -> None:
        log.warn("HALTING ALL MOTION")
        if not self.positioner:
            PopUpMessage("Not connected")
            return
        self.positioner.abort_all()

    def connect_to_analyzer(self) -> None:
        if self.analyzer:
            log.info("Already connected.")
            return
        model = self.view.analyzer_model
        port = self.view.analyzer_port

        if model == "" or port == "":
            log.info("Model not selected. Ignoring")
            return

        try:
            log.info("Connecting to analyzer...")
            self.analyzer = self.analyzer_models[model](port)
        except Exception as e:
            PopUpMessage(str(e), MsgLevel.ERROR)
            return
        try:
            self.view.start_freq = self.analyzer.start_freq
            self.view.stop_freq = self.analyzer.stop_freq
            self.view.npoints = self.analyzer.npoints
            self.view.step_freq = self.analyzer.freq_step
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
        if self.view.positionerGroupBox.enabled():
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
        step = self.view.freq_step

        if start:
            self.view.dataPolarFreqSpinBox.setMinimum(start)
        if stop:
            self.view.dataPolarFreqSpinBox.setMaximum(stop)
        if step:
            self.view.dataPolarFreqSpinBox.setSingleStep(step)
