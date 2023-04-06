from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychamber.app.widgets import AnalyzerControls, ExperimentControls, PositionerControls
    from pychamber.positioner import Postioner

import os
import pathlib

import numpy as np
import qdarkstyle
import qtawesome as qta
import skrf
from qtpy.QtCore import Qt, QThread
from qtpy.QtGui import QCloseEvent
from qtpy.QtWidgets import (
    QApplication,
    QFileDialog,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from pychamber import ExperimentResult
from pychamber.app.objects import ExperimentWorker
from pychamber.app.ui.mainwindow import Ui_MainWindow
from pychamber.app.widgets import LogDialog
from pychamber.settings import CONF


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.app = QApplication.instance()
        self.log_dialog = LogDialog()
        self.active_result: ExperimentResult | None = None
        self.saved = []
        self._results = []
        self._thread = QThread()

        self.apply_theme(CONF["theme"])

        self.setupUi(self)
        self.results_widget.hide()
        self.connect_signals()

    def post_visible_setup(self):
        self.total_progress_gb.hide()
        self.cut_progress_gb.hide()
        self.time_remaining_gb.hide()

        CONF.update_widgets_from_settings()

    def connect_signals(self):
        self.save_action.triggered.connect(self.on_save_action_triggered)
        self.load_action.triggered.connect(self.on_load_action_triggered)
        self.view_logs_action.triggered.connect(self.on_view_logs_action_triggered)

        self.exit_action.triggered.connect(self.close)

        self.analyzer_controls.analyzerConnected.connect(self.on_analyzer_connected)
        self.analyzer_controls.analyzerDisonnected.connect(self.on_analyzer_disconnected)
        self.positioner_controls.positionerConnected.connect(self.on_positioner_connected)
        self.positioner_controls.positionerDisonnected.connect(self.on_positioner_disconnected)

        self.phi_scan_btn.pressed.connect(self.on_phi_scan_btn_pressed)
        self.theta_scan_btn.pressed.connect(self.on_theta_scan_btn_pressed)
        self.full_scan_btn.pressed.connect(self.on_full_scan_btn_pressed)
        self.abort_btn.pressed.connect(self.on_abort_btn_pressed)

        self.results.model().rowsInserted.connect(self.on_results_rows_changed)
        self.results.currentItemChanged.connect(self.on_current_result_changed)

    def closeEvent(self, event: QCloseEvent) -> None:
        if len(self.saved) < self.results.count():
            quit_dlg = QMessageBox.warning(
                self,
                "Are you sure?",
                "You have unsaved data that will be lost. Are you sure you want to quit?",
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Ok,
            )
            if quit_dlg == QMessageBox.Ok:
                if self._thread.isRunning():
                    self._thread.quit()
                    self._thread.wait()
                return super().closeEvent(event)
            else:
                event.ignore()
                return

        return super().closeEvent(event)

    def on_save_action_triggered(self):
        if self.active_result is None:
            QMessageBox.information(
                self,
                "No Data to Save",
                "There is no experiment data to save.",
            )
            return

        fname, _ = QFileDialog.getSaveFileName(self, "Save Result", filter="Result File (*.mdif)")
        if fname == "":
            return

        path = pathlib.Path(fname).with_suffix(".mdif")
        self.active_result.save(path)
        self.saved.append(self.active_result.uuid)
        self.update_results_rows()

    def on_load_action_triggered(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Result", filter="Result File (*.mdif)")
        if fname == "":
            return

        path = pathlib.Path(fname)
        result = ExperimentResult.load(path)
        if result.uuid in self.saved:
            return
        self.active_result = result
        self._results.append(result)
        self.saved.append(result.uuid)
        self.plot_dock_widget.results = result

        item = QListWidgetItem(self.results)
        item.setData(Qt.UserRole, result.uuid)
        item.setText(result.created)
        self.results.setCurrentItem(item)
        self.update_results_rows()

    def on_view_logs_action_triggered(self):
        self.log_dialog.show()

    def on_results_rows_changed(self):
        if self.results.count() == 0:
            self.results_widget.hide()
            return

        self.results_widget.show()

    def on_current_result_changed(self, item: QListWidgetItem):
        result = None
        for res in self._results:
            if res.uuid == item.data(Qt.UserRole):
                result = res
                break
        self.plot_dock_widget.results = result

    def on_analyzer_connected(self):
        if self.positioner is not None:
            self.set_scan_btns_enabled(True)

        self.set_pol_params()

    def on_analyzer_disconnected(self):
        self.set_scan_btns_enabled(False)

    def on_positioner_connected(self):
        if self.analyzer is not None:
            self.set_scan_btns_enabled(True)
        self.positioner.jogStarted.connect(lambda: self.set_scan_btns_enabled(False))
        self.positioner.jogCompleted.connect(lambda: self.set_scan_btns_enabled(True))

    def on_positioner_disconnected(self):
        self.set_scan_btns_enabled(False)

    def on_abort_btn_pressed(self) -> None:
        if self._thread.isRunning():
            self._thread.requestInterruption()

    def on_phi_scan_btn_pressed(self) -> None:
        start = CONF["phi_start"]
        stop = CONF["phi_stop"]
        step = CONF["phi_step"]
        phis = np.arange(start, stop + step, step)
        thetas = np.array([self.positioner.theta])

        self.total_progress_gb.show()
        self.cut_progress_gb.hide()
        self.time_remaining_gb.show()

        self.total_progress_bar.setMaximum(len(phis))
        self.time_remaining_le.setText("00:00:00")

        pols = self.experiment_controls.polarizations
        self.run_scan(phis, thetas, pols)

    def on_theta_scan_btn_pressed(self) -> None:
        start = CONF["theta_start"]
        stop = CONF["theta_stop"]
        step = CONF["theta_step"]
        phis = np.array([self.positioner.phi])
        thetas = np.arange(start, stop + step, step)

        self.total_progress_gb.show()
        self.cut_progress_gb.hide()
        self.time_remaining_gb.show()

        self.total_progress_bar.setMaximum(len(thetas))
        self.time_remaining_le.setText("00:00:00")

        pols = self.experiment_controls.polarizations
        self.run_scan(phis, thetas, pols)

    def on_full_scan_btn_pressed(self) -> None:
        phi_start = CONF["phi_start"]
        phi_stop = CONF["phi_stop"]
        phi_step = CONF["phi_step"]
        theta_start = CONF["theta_start"]
        theta_stop = CONF["theta_stop"]
        theta_step = CONF["theta_step"]
        phis = np.arange(phi_start, phi_stop + phi_step, phi_step)
        thetas = np.arange(theta_start, theta_stop + theta_step, theta_step)

        self.total_progress_gb.show()
        self.cut_progress_gb.show()
        self.time_remaining_gb.show()

        self.total_progress_bar.setMaximum(len(phis) * len(thetas))
        self.cut_progress_bar.setMaximum(len(phis))
        self.time_remaining_le.setText("00:00:00")

        pols = self.experiment_controls.polarizations
        self.run_scan(phis, thetas, pols)

    def on_total_progress_updated(self, iters: int) -> None:
        self.total_progress_bar.setValue(iters)

    def on_cut_progress_updated(self, iters: int) -> None:
        self.cut_progress_bar.setValue(iters)

    def on_time_est_updated(self, time_est: float) -> None:
        est = round(time_est)
        hours, minutes = divmod(est, 3600)
        minutes, seconds = divmod(minutes, 60)
        time_str = f"{hours} hours {minutes:0>2} minutes {seconds:0>2} seconds"
        self.time_remaining_le.setText(time_str)

    def on_experiment_started(self) -> None:
        self.total_progress_bar.setValue(0)
        self.cut_progress_bar.setValue(0)
        self.set_controls_enabled(False)
        self.set_scan_btns_enabled(False)
        self.abort_btn.setEnabled(True)

    def on_experiment_finished(self) -> None:
        self.set_controls_enabled(True)
        self.set_scan_btns_enabled(True)
        self.abort_btn.setEnabled(False)

    def update_results_rows(self):
        for i in range(self.results.count()):
            item = self.results.item(i)
            uuid = item.data(Qt.UserRole)
            item.setIcon(qta.icon("fa5s.exclamation", color="#ff6961") if uuid not in self.saved else qta.icon())

    def set_scan_btns_enabled(self, state: bool) -> None:
        self.full_scan_btn.setEnabled(state)
        self.phi_scan_btn.setEnabled(state)
        self.theta_scan_btn.setEnabled(state)

    def set_controls_enabled(self, state: bool) -> None:
        self.experiment_controls.setEnabled(state)
        self.analyzer_controls.setEnabled(state)
        self.positioner_controls.enable_on_jog_completed = state
        self.positioner_controls.set_enabled(state)

    def apply_theme(self, theme: str | None) -> None:
        if theme is None:
            theme = "Light"

        palette = qdarkstyle.LightPalette if theme == "Light" else qdarkstyle.DarkPalette
        self.app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ["PYQTGRAPH_QT_LIB"], palette=palette))

        from pyqtgraph import setConfigOptions

        if theme == "Light":
            setConfigOptions(foreground="#54687a", background="#f5fbff")
        else:
            setConfigOptions(foreground="#c2e3fa", background="#455364")

    @property
    def analyzer(self) -> skrf.vi.VNA | None:
        return self.controls_area.analyzer_controls.analyzer

    @property
    def analyzer_controls(self) -> AnalyzerControls:
        return self.controls_area.analyzer_controls

    @property
    def positioner_controls(self) -> PositionerControls:
        return self.controls_area.positioner_controls

    @property
    def experiment_controls(self) -> ExperimentControls:
        return self.controls_area.experiment_controls

    @property
    def positioner(self) -> Postioner | None:
        return self.controls_area.positioner_controls.positioner

    def set_pol_params(self) -> None:
        params = self.analyzer_controls.available_params
        self.experiment_controls.update_params(params)

    def run_scan(self, phis: np.ndarray, thetas: np.ndarray, polarizations: list[tuple[str, int, int]]) -> None:
        freq = self.analyzer_controls.frequency
        result = ExperimentResult(thetas, phis, [p[0] for p in polarizations], freq)
        item = QListWidgetItem(self.results)
        item.setData(Qt.UserRole, result.uuid)
        item.setText(result.created)
        self.results.setCurrentItem(item)
        self.active_result = result
        self.update_results_rows()
        self._results.append(result)

        self.worker = ExperimentWorker(self.analyzer, self.positioner, phis, thetas, polarizations)
        self.worker.moveToThread(self._thread)
        self._thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.worker.started.connect(self.on_experiment_started)
        self.worker.dataAcquired.connect(self.active_result.append)
        self.worker.totalIterCountUpdated.connect(self.on_total_progress_updated)
        self.worker.cutIterCountUpdated.connect(self.on_cut_progress_updated)
        self.worker.timeEstUpdated.connect(self.on_time_est_updated)
        self.worker.finished.connect(self.on_experiment_finished)
        self.worker.finished.connect(self.total_progress_gb.hide)
        self.worker.finished.connect(self.time_remaining_gb.hide)
        self.worker.finished.connect(self.cut_progress_gb.hide)

        self._thread.start()
