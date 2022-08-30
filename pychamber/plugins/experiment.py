"""Defines the experiment plugin."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import skrf
    from typing import Dict, List, Optional
    from PyQt5.QtGui import QCloseEvent
    from pychamber.main_window import MainWindow
    from pychamber.polarization import Polarization
    from pychamber.plugins import (
        AnalyzerPlugin,
        CalibrationPlugin,
        PlotsPlugin,
        PositionerPlugin,
    )

import functools
import time
from datetime import timedelta
from enum import Enum, auto
from math import ceil

import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from pychamber.logger import LOG
from pychamber.models import NetworkModel
from pychamber.plugins import PyChamberPlugin
from pychamber.ui import font, size_policy


class ExperimentType(Enum):
    AZIMUTH = auto()
    ELEVATION = auto()
    FULL = auto()


class ExperimentPlugin(PyChamberPlugin):
    """The Experiment plugin.

    This plugin handles the actual nuts and bolts of taking a measurement. It
    spins up a new thread to keep the GUI responsive, and manages the positioner
    and analyzer.

    Attributes:
        start_experiment: Signal the start of an experiment
        experiment_done: Signal an experiment has concluded
        abort_clicked: Signal raised when the abort button is clicked (passed to
            the measurement thread)
        progress_updated: Signal raised when the total progress is updated
        update_remaining: Signal to indicate remaining iteration counter should be updated
        cut_progress_updated: Signal raised when cut progress is updated
        time_remaining_updated: Signal to indicate time remaining has been updated
        data_acquired: Signal raised when new data is acquired
    """

    NAME = "experiment"
    CONFIG: Dict = {}

    # Signals
    start_experiment = pyqtSignal(object)
    experiment_done = pyqtSignal()
    abort_clicked = pyqtSignal()
    progress_updated = pyqtSignal(int)
    update_remaining = pyqtSignal(int)
    cut_progress_updated = pyqtSignal(int)
    time_remaining_updated = pyqtSignal(float)
    data_acquired = pyqtSignal(object)

    def __init__(self, parent: MainWindow) -> None:
        """Instantiate the plugin.

        Arguments:
            parent: the PyChamber main window
        """
        super().__init__(parent)

        self.setObjectName("experiment")
        self.setLayout(QVBoxLayout())

        self.analyzer: Optional[AnalyzerPlugin] = None
        self.positioner: Optional[PositionerPlugin] = None
        self.plots: Optional[PlotsPlugin] = None
        self.calibration: Optional['CalibrationPlugin'] = None

        self.experiment_thread: QThread = QThread(None)
        self.ntwk_model: NetworkModel = NetworkModel()

        self.analyzer_connected: bool = False
        self.positioner_connected: bool = False

        self._remaining_iters = 0
        self._avg_iter_time: float = 0.0
        self._iter_start_time: float = 0.0
        self._iter_stop_time: float = 0.0

    def _setup(self) -> None:
        from pychamber.plugins import AnalyzerPlugin, PlotsPlugin, PositionerPlugin

        self._add_widgets()

        self.analyzer = cast(AnalyzerPlugin, self.main.get_plugin("analyzer"))
        self.positioner = cast(PositionerPlugin, self.main.get_plugin("positioner"))
        self.plots = cast(PlotsPlugin, self.main.get_plugin("plots"))
        # I have no idea why the interpreter threw a fit for only this module...
        self.calibration = cast('CalibrationPlugin', self.main.get_plugin("calibration"))

    def _post_visible_setup(self) -> None:
        self._connect_signals()

    def _add_widgets(self) -> None:
        LOG.debug("Creating Experiment widget...")
        self.groupbox = QGroupBox("Experiment", self)
        self.layout().addWidget(self.groupbox)

        layout = QHBoxLayout(self.groupbox)

        vlayout = QVBoxLayout()

        self.full_scan_btn = QPushButton("Full Scan", self.groupbox)
        self.full_scan_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.full_scan_btn.setFont(font["BOLD_12"])
        vlayout.addWidget(self.full_scan_btn)

        self.az_scan_btn = QPushButton("Scan Azimuth", self.groupbox)
        self.az_scan_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.az_scan_btn.setFont(font["BOLD_12"])
        vlayout.addWidget(self.az_scan_btn)

        self.el_scan_btn = QPushButton("Scan Elevation", self.groupbox)
        self.el_scan_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.el_scan_btn.setFont(font["BOLD_12"])
        vlayout.addWidget(self.el_scan_btn)

        self.abort_btn = QPushButton("ABORT", self.groupbox)
        self.abort_btn.setStyleSheet("background-color: rgb(237, 51, 59)")
        self.abort_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.abort_btn.setFont(font["BOLD_12"])
        self.abort_btn.setEnabled(False)
        vlayout.addWidget(self.abort_btn)

        layout.addLayout(vlayout)

        vlayout = QVBoxLayout()

        total_progress_label = QLabel("Total Progress", self.groupbox)
        total_progress_label.setSizePolicy(size_policy["PREF_PREF"])
        total_progress_label.setFont(font["BOLD_12"])
        total_progress_label.setAlignment(Qt.AlignHCenter)
        vlayout.addWidget(total_progress_label)

        self.total_progressbar = QProgressBar(self.groupbox)
        self.total_progressbar.setSizePolicy(size_policy["PREF_PREF"])
        vlayout.addWidget(self.total_progressbar)

        self.cut_progress_label = QLabel("Cut Progress", self.groupbox)
        self.cut_progress_label.setSizePolicy(size_policy["PREF_PREF"])
        self.cut_progress_label.setFont(font["BOLD_12"])
        self.cut_progress_label.setAlignment(Qt.AlignHCenter)
        vlayout.addWidget(self.cut_progress_label)

        self.cut_progressbar = QProgressBar(self.groupbox)
        self.cut_progressbar.setSizePolicy(size_policy["EXP_PREF"])
        vlayout.addWidget(self.cut_progressbar)

        time_remaining_label = QLabel("Time Remaining Estimate", self.groupbox)
        time_remaining_label.setSizePolicy(size_policy["PREF_PREF"])
        time_remaining_label.setFont(font["BOLD_12"])
        time_remaining_label.setAlignment(Qt.AlignHCenter)
        vlayout.addWidget(time_remaining_label)

        self.time_remaining_lineedit = QLineEdit(self.groupbox)
        self.time_remaining_lineedit.setSizePolicy(size_policy["EXP_PREF"])
        vlayout.addWidget(self.time_remaining_lineedit)

        layout.addLayout(vlayout)

        self.set_enabled(False)
        self.cut_progress_label.hide()
        self.cut_progressbar.hide()

    def _connect_signals(self) -> None:
        assert self.analyzer is not None
        assert self.positioner is not None
        assert self.plots is not None

        self.az_scan_btn.clicked.connect(
            functools.partial(self.start_experiment.emit, ExperimentType.AZIMUTH)
        )

        self.el_scan_btn.clicked.connect(
            functools.partial(self.start_experiment.emit, ExperimentType.ELEVATION)
        )

        self.full_scan_btn.clicked.connect(
            functools.partial(self.start_experiment.emit, ExperimentType.FULL)
        )

        self.start_experiment.connect(self._on_start_experiment)
        self.abort_btn.clicked.connect(self._on_abort_experiment)
        self.experiment_done.connect(self._on_experiment_done)
        self.progress_updated.connect(self._on_progress_updated)
        self.cut_progress_updated.connect(self._on_cut_progress_updated)
        self.time_remaining_updated.connect(self._on_time_remaining_updated)
        self.update_remaining.connect(lambda r: setattr(self, "_remaining_iters", r))

        self.experiment_thread.finished.connect(self.experiment_done.emit)
        self.experiment_thread.finished.connect(self._on_experiment_done)
        self.data_acquired.connect(self._on_data_acquired)
        self.data_acquired.connect(self._calc_time_remaining)

        self.analyzer.analyzer_connected.connect(self._on_analyzer_connected)
        self.positioner.positioner_connected.connect(self._on_positioner_connected)

        self.ntwk_model.data_added.connect(self.plots.rx_updated_data)

    def _on_start_experiment(self, experiment_type: ExperimentType) -> None:
        assert self.analyzer is not None
        assert self.positioner is not None
        assert self.plots is not None
        assert self.calibration is not None

        self.set_enabled(False)
        self.calibration.set_enabled(False)

        match experiment_type:
            case ExperimentType.AZIMUTH:
                az_extents = self.positioner.az_extents()
                el_extents = np.asarray([0.0])
            case ExperimentType.ELEVATION:
                az_extents = np.asarray([0.0])
                el_extents = self.positioner.el_extents()
            case ExperimentType.FULL:
                az_extents = self.positioner.az_extents()
                el_extents = self.positioner.el_extents()

        pols = self.analyzer.polarizations()
        if len(pols) == 0:
            LOG.debug("No polarizations. No experiment to run")
            return

        self.reset_experiment()
        if experiment_type == ExperimentType.FULL:
            self.enable_cut_progress(True)
        self.ntwk_model.reset()
        self.plots.set_polarizations([p.label for p in pols])
        self.plots.init_plots(
            frequencies=self.analyzer.frequencies(),
            azimuths=az_extents,
            elevations=el_extents,
        )

        self.experiment_thread.run = functools.partial(
            self.run_experiment,
            polarizations=pols,
            azimuths=az_extents,
            elevations=el_extents,
        )
        self._remaining_iters = len(az_extents) * len(el_extents)
        self.experiment_thread.start()

    def _on_data_acquired(self, ntwk: skrf.Network) -> None:
        assert self.analyzer is not None
        assert self.calibration is not None
        if (cal := self.calibration.calibration()) is None:
            self.ntwk_model.add_data(ntwk)
        else:
            pol = ntwk.params["polarization"]
            if pol == self.analyzer.pol_name(1):
                LOG.debug("Applying calibration pol1")
                loss = cal.pol1
            elif pol == self.analyzer.pol_name(2):
                LOG.debug("Applying calibration pol2")
                loss = cal.pol2
            else:
                raise ValueError("This should be unreachable...")

            assert loss is not None
            LOG.debug(f"{ntwk.s_db[0]=}")
            LOG.debug(f"{loss.s_db[0]=}")
            corrected_ntwk = ntwk / loss
            self.ntwk_model.add_data(corrected_ntwk)

    def _on_experiment_done(self) -> None:
        assert self.calibration is not None
        self.enable_cut_progress(False)
        self.total_progressbar.setValue(100)
        self.time_remaining_lineedit.setText("Done!")
        self.calibration.set_enabled(True)
        self.set_enabled(True)

    def _on_abort_experiment(self) -> None:
        LOG.debug("Aborting experiment...")
        if self.experiment_thread.isRunning():
            self.experiment_thread.requestInterruption()

    def _on_progress_updated(self, progress: int) -> None:
        self.total_progressbar.setValue(progress)

    def _on_cut_progress_updated(self, progress: int) -> None:
        self.cut_progressbar.setValue(progress)

    def _on_time_remaining_updated(self, secs: float) -> None:
        t_secs = str(timedelta(seconds=ceil(secs)))
        hours, minutes, seconds = t_secs.split(":")
        self.time_remaining_lineedit.setText(
            f"{hours} hours {minutes} minutes {seconds} seconds remaining"
        )

    def _on_analyzer_connected(self) -> None:
        self.analyzer_connected = True
        if self.analyzer_connected and self.positioner_connected:
            self.set_enabled(True)

    def _on_positioner_connected(self) -> None:
        self.positioner_connected = True
        if self.analyzer_connected and self.positioner_connected:
            self.set_enabled(True)

    def _calc_time_remaining(self, _) -> None:
        self._iter_stop_time = time.time()
        self._avg_iter_time = 0.5 * (
            self._avg_iter_time + self._iter_stop_time - self._iter_start_time
        )
        self._iter_start_time = time.time()
        self.time_remaining_updated.emit(self._remaining_iters * self._avg_iter_time)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensures threads are killed."""
        self.experiment_thread.quit()
        self.experiment_thread.wait()
        super().closeEvent(event)

    # ========== API ==========
    def set_enabled(self, enable: bool) -> None:
        """Enable/Disable the plugin.

        Arguments:
            enable: True to enable, False to disable
        """
        self.az_scan_btn.setEnabled(enable)
        self.el_scan_btn.setEnabled(enable)
        self.full_scan_btn.setEnabled(enable)
        self.abort_btn.setEnabled(not enable)

    def enable_cut_progress(self, state: bool) -> None:
        if state:
            self.cut_progress_label.show()
            self.cut_progressbar.show()
        else:
            self.cut_progress_label.hide()
            self.cut_progressbar.hide()

    def reset_experiment(self) -> None:
        """Reset experiment to initial state."""
        self.total_progressbar.setValue(0)
        self.cut_progressbar.setValue(0)
        self.enable_cut_progress(False)
        self.time_remaining_lineedit.setText("")

    def run_experiment(
        self,
        polarizations: List[Polarization],
        azimuths: np.ndarray,
        elevations: np.ndarray,
    ) -> None:
        """Run an experiment!

        This is the primary purpose of this plugin...to do the actual data
        gathering. This function is meant to be the run function of a QThread to
        ensure the GUI remains responsive.

        It will create measurements on the analyzer and delete them when it's finished.

        Arguments:
            polarizations: List of Polarizations which contain measurement names
                and parameters
            azimuths: array of azimuths to steer the positioner to
            elevations: array of elevations to steer the positioner to

        Raises:
            AssertionError: if any of the required plugins are unavailable
            RuntimeError: if any other exception is raised during the experiment
        """
        LOG.debug("Starting experiment thread")
        LOG.debug(f"{polarizations=}")
        LOG.debug(f"{azimuths=}")
        LOG.debug(f"{elevations=}")
        assert self.analyzer is not None
        assert self.plots is not None
        assert self.positioner is not None

        # Signals
        progress_updated = self.progress_updated
        cut_progress_updated = self.cut_progress_updated
        data_acquired = self.data_acquired

        self.positioner.set_enabled(False)
        self.analyzer.set_enabled(False)
        self.plots.reset_plots()

        self.positioner.listen_to_jog_complete_signals = False

        params = {}
        # Now we can use move_spy.wait() to ensure we wait
        # for the move to finish before taking data
        move_spy = QSignalSpy(self.positioner.jog_complete)

        total_iters = len(azimuths) * len(elevations)
        completed = 0
        progress = 0

        try:
            for pol in polarizations:
                self.analyzer.create_measurement(f"ANT_{pol.param}", pol.param)

            for i, azimuth in enumerate(azimuths):
                LOG.debug(f"Azimuth: {azimuth}")
                if self.experiment_thread.isInterruptionRequested():
                    self.main.statusBar().showMessage("Experiment aborted!", 4000)
                    break

                params["azimuth"] = azimuth
                self.positioner.jog_az(azimuth)
                LOG.debug("Waiting for azimuth jog to finish...")
                move_spy.wait()

                for j, elevation in enumerate(elevations):
                    LOG.debug(f"Elevation: {elevation}")
                    if self.experiment_thread.isInterruptionRequested():
                        self.main.statusBar().showMessage("Experiment aborted!", 4000)
                        break

                    params["elevation"] = elevation
                    self.positioner.jog_el(elevation)
                    LOG.debug("Waiting for elevation jog to finish...")
                    move_spy.wait()

                    for pol in polarizations:
                        params["polarization"] = pol.label
                        ntwk = self.analyzer.get_data(f"ANT_{pol.param}")
                        ntwk.params = params.copy()
                        LOG.debug(f"Got data for {ntwk.params}")
                        data_acquired.emit(ntwk)

                    LOG.debug(f"{len(elevations)}")
                    completed = i * len(elevations) + j
                    self.update_remaining.emit(total_iters - completed)
                    LOG.debug(f"{i=}; {j=}")
                    LOG.debug(f"{completed=}")
                    progress = int(completed / total_iters * 100)
                    cut_progress = int(j / len(elevations) * 100)

                    progress_updated.emit(progress)
                    cut_progress_updated.emit(cut_progress)

        except Exception as e:
            raise RuntimeError(f"Encountered error during measurement: {e}")
        finally:
            for pol in polarizations:
                self.analyzer.delete_measurement(f"ANT_{pol.param}")
            self.positioner.listen_to_jog_complete_signals = True
            self.positioner.set_enabled(True)
