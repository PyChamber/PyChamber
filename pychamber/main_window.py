import functools
import time
import webbrowser
from typing import Dict, List

import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from pychamber.logger import log
from pychamber.plugins import AnalyzerPlugin, CalibrationPlugin, PositionerPlugin
from pychamber.plugins.base import PyChamberPlugin
from pychamber.polarization import Polarization
from pychamber.ui import resources_rc, size_policy  # noqa: F401
from pychamber.widgets import ExperimentWidget, PlotsWidget
from pychamber.widgets.experiment import ExperimentType

from .models.ntwk_model import NetworkModel


class MainWindow(QMainWindow):
    # Signals
    experiment_finished = pyqtSignal()

    def __init__(self, *args) -> None:
        super().__init__(*args)
        log.debug("Constructing MainWindow...")

        self.setWindowTitle("PyChamber")
        self.setWindowIcon(QIcon(":/logo.png"))

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.core_plugins: Dict[str, PyChamberPlugin] = {}
        self.optional_plugins: Dict[str, PyChamberPlugin] = {}

        self.analyzer_connected = False
        self.positioner_connected = False

        self.experiment_thread: QThread = QThread(None)
        self.abort = False

        self.ntwk_model: NetworkModel = NetworkModel()

    def setup(self) -> None:
        self._setup_menu()
        self._add_widgets()

    def post_visible_setup(self) -> None:
        log.debug("Running post-visible setups")
        to_init = list(self.core_plugins.values()) + list(self.optional_plugins.values())
        for plugin in to_init:
            plugin.post_visible_setup()

        self.experiment_widget.post_visible_setup()
        self.plots_widget.post_visible_setup()

        self._connect_signals()

        self.statusBar().showMessage("Welcome to PyChamber!", 2000)

    def center(self) -> None:
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        log.debug("Close event triggered")
        warning = QMessageBox()
        warning.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        warning.setDefaultButton(QMessageBox.Cancel)
        warning.setText("Are you sure you want to quit?\n(Any unsaved data will be LOST)")

        resp = warning.exec_()
        if resp == QMessageBox.Yes:
            log.debug("Close event accepted")
            del self.settings  # Saves settings
            self.experiment_thread.quit()
            self.experiment_thread.wait()
            super().closeEvent(event)
        else:
            log.debug("Close event canceled")
            event.ignore()

    def _setup_menu(self) -> None:
        log.debug("Setting up menu...")
        self.menu = self.menuBar()

        self.file = self.menu.addMenu("File")
        self.save = self.file.addAction("Save")
        self.load = self.file.addAction("Load")
        self.file.addSeparator()
        self.settings = self.file.addAction("Settings")
        self.file.addSeparator()
        self.quit = self.file.addAction("Quit")

        self.tools = self.menu.addMenu("Tools")
        self.python_interpreter = self.tools.addAction("Python Terminal")

        self.help = self.menu.addMenu("Help")
        self.bug = self.help.addAction("Submit a Bug")
        self.help.addSeparator()
        self.about = self.help.addAction("About")
        self.log = self.help.addAction("View Log")

        bug_report_url = "https://github.com/HRG-Lab/PyChamber/issues/new"
        self.bug.triggered.connect(lambda: webbrowser.open(bug_report_url))

    def _add_widgets(self) -> None:
        log.debug("Setting up widgets...")

        self.experiment_widget = ExperimentWidget(self.centralWidget())
        self.plots_widget = PlotsWidget(self.centralWidget())

        # Add loading of optional_plugins here

        self.ctrl_scroll_area = QScrollArea(widgetResizable=True)
        self.ctrl_widget = QWidget()
        self.ctrl_scroll_area.setWidget(self.ctrl_widget)
        self.ctrl_layout = QVBoxLayout(self.ctrl_widget)
        self.ctrl_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ctrl_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.core_plugins["analyzer"] = AnalyzerPlugin(self.ctrl_widget)
        self.core_plugins["calibration"] = CalibrationPlugin(self.ctrl_widget)
        self.core_plugins["positioner"] = PositionerPlugin(self.ctrl_widget)

        right_side_layout = QVBoxLayout()

        self.main_layout.addWidget(self.ctrl_scroll_area)
        self.main_layout.addLayout(right_side_layout)

        to_init = list(self.core_plugins.values()) + list(self.optional_plugins.values())

        for plugin in to_init:
            plugin.setup()
            self.ctrl_layout.addWidget(plugin)

        self.experiment_widget.setup()
        right_side_layout.addWidget(self.experiment_widget)
        self.plots_widget.setup()
        right_side_layout.addWidget(self.plots_widget)

        self.ctrl_layout.addStretch()

        self.ctrl_scroll_area.setFixedWidth(
            self.ctrl_widget.minimumSizeHint().width()
            + self.ctrl_scroll_area.verticalScrollBar().sizeHint().width()
        )

    def _connect_signals(self) -> None:
        log.debug("Connecting signals...")
        analyzer: AnalyzerPlugin = self.core_plugins["analyzer"]  # type: ignore
        positioner: PositionerPlugin = self.core_plugins["positioner"]  # type: ignore
        experiment: ExperimentWidget = self.experiment_widget

        analyzer.analyzer_connected.connect(
            lambda: setattr(self, "analyzer_connected", True)
        )
        analyzer.analyzer_connected.connect(self._enable_experiment)

        positioner.jog_started.connect(lambda: self.statusBar().showMessage("Jogging..."))
        positioner.jog_complete.connect(
            lambda: self.statusBar().showMessage("Jog complete", 500)
        )
        positioner.positioner_connected.connect(
            lambda: setattr(self, "positioner_connected", True)
        )
        positioner.positioner_connected.connect(self._enable_experiment)

        experiment.start_experiment.connect(self._on_start_experiment)
        self.experiment_thread.finished.connect(
            self.experiment_widget.experiment_done.emit
        )
        self.experiment_thread.finished.connect(lambda: setattr(self, "abort", False))
        self.experiment_widget.data_acquired.connect(self.ntwk_model.add_data)
        self.ntwk_model.data_added.connect(self.plots_widget.rx_updated_data)

    def _enable_experiment(self) -> None:
        if self.analyzer_connected and self.positioner_connected:
            log.debug("Enabling experiment")
            self.experiment_widget.set_enabled(True)

    def _on_start_experiment(self, experiment_type: ExperimentType) -> None:
        log.debug(f"Running experiment {experiment_type}")

        self.ntwk_model.reset()

        match experiment_type:
            case ExperimentType.AZIMUTH:
                az_extents = self.core_plugins["positioner"].az_extents()  # type: ignore
                el_extents = np.asarray([0])
            case ExperimentType.ELEVATION:
                az_extents = np.asarray([0])
                el_extents = self.core_plugins["positioner"].el_extents()  # type: ignore
            case ExperimentType.FULL:
                az_extents = self.core_plugins["positioner"].az_extents()  # type: ignore
                el_extents = self.core_plugins["positioner"].el_extents()  # type: ignore

        pols = self.core_plugins["analyzer"].polarizations()  # type: ignore
        if len(pols) == 0:
            log.debug("No polarizations. No experiment to run")
            return

        self.experiment_thread.run = functools.partial(
            self.run_experiment,
            polarizations=pols,
            azimuths=az_extents,
            elevations=el_extents,
        )
        self.experiment_thread.start()

    def run_experiment(
        self,
        polarizations: List[Polarization],
        azimuths: np.ndarray,
        elevations: np.ndarray,
    ) -> None:
        log.debug("Starting experiment thread")
        log.debug(f"{polarizations=}")
        log.debug(f"{azimuths=}")
        log.debug(f"{elevations=}")

        self.experiment_widget.abort_clicked.connect(lambda: setattr(self, "abort", True))

        analyzer: AnalyzerPlugin = self.core_plugins["analyzer"]  # type: ignore
        positioner: PositionerPlugin = self.core_plugins["positioner"]  # type: ignore

        # Signals
        progress_updated = self.experiment_widget.progress_updated
        cut_progress_updated = self.experiment_widget.cut_progress_updated
        data_acquired = self.experiment_widget.data_acquired

        positioner.set_enabled(False)
        analyzer.set_enabled(False)

        positioner.listen_to_jog_complete_signals = False

        params = {}
        # Now we can use move_spy.wait() to ensure we wait
        # for the move to finish before taking data
        move_spy = QSignalSpy(positioner.jog_complete)

        avg_iter_time = 0.0
        total_iters = len(azimuths) * len(elevations)
        completed = 0
        progress = 0

        try:
            for pol in polarizations:
                analyzer.create_measurement(f"ANT_{pol.param}", pol.param)

            for i, azimuth in enumerate(azimuths):
                log.debug(f"Azimuth: {azimuth}")
                if self.abort:
                    self.statusBar().showMessage("Experiment aborted!", 4000)
                    break

                params["azimuth"] = azimuth
                positioner.jog_az(azimuth)
                log.debug("Waiting for azimuth jog to finish...")
                move_spy.wait()

                for j, elevation in enumerate(elevations):
                    log.debug(f"Elevation: {elevation}")
                    iter_start = time.time()
                    if self.abort:
                        self.statusBar().showMessage("Experiment aborted!", 4000)
                        break

                    params["elevation"] = elevation
                    positioner.jog_el(elevation)
                    log.debug("Waiting for elevation jog to finish...")
                    move_spy.wait()

                    for pol in polarizations:
                        params["polarization"] = pol.label
                        ntwk = analyzer.get_data(f"ANT_{pol.param}")
                        ntwk.params = params.copy()
                        data_acquired.emit(ntwk)

                    completed = i * len(elevations) + j
                    progress = completed // total_iters * 100
                    cut_progress = j // len(elevations) * 100

                    progress_updated.emit(progress)
                    cut_progress_updated.emit(cut_progress)

                    iter_stop = time.time()
                    iter_time = iter_stop - iter_start
                    avg_iter_time = 0.5 * (avg_iter_time + iter_time)

        except Exception as e:
            raise RuntimeError(f"Encountered error during measurement: {e}")
        finally:
            for pol in polarizations:
                analyzer.delete_measurement(f"ANT_{pol.param}")
            positioner.listen_to_jog_complete_signals = True
            positioner.set_enabled(True)
