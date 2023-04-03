from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychamber.app.widgets import AnalyzerControls, ExperimentControls, PositionerControls
    from pychamber.positioner import Postioner


import numpy as np
import skrf
from PySide6.QtCore import QThread, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QVBoxLayout

from pychamber import ExperimentResult
from pychamber.app.objects import ExperimentWorker
from pychamber.app.ui.mainwindow import Ui_MainWindow
from pychamber.app.widgets import LogDialog
from pychamber.settings import CONF


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.log_dialog = LogDialog()
        self.results = None
        self.thread = QThread()

        self.setupUi(self)
        self.connect_signals()
        self.post_visible_setup()

        test_dlg = QDialog(self)
        layout = QVBoxLayout(test_dlg)
        hlayout = QHBoxLayout()
        phi_label = QLabel("Phi: ")
        self.current_phi = QLabel("")
        theta_label = QLabel("Theta: ")
        self.current_theta = QLabel("")
        hlayout.addWidget(phi_label)
        hlayout.addWidget(self.current_phi)
        hlayout.addWidget(theta_label)
        hlayout.addWidget(self.current_theta)
        self.status_label = QLabel("Not Running")
        test_scan_btn = QPushButton("Run Test Scan")
        test_scan_btn.pressed.connect(self.run_test_scan)
        self.stop_test_btn = QPushButton("Stop Scan")
        layout.addWidget(self.status_label)
        layout.addLayout(hlayout)
        layout.addWidget(test_scan_btn)
        layout.addWidget(self.stop_test_btn)
        test_dlg.show()

    def post_visible_setup(self):
        self.total_progress_gb.hide()
        self.cut_progress_gb.hide()
        self.time_remaining_gb.hide()

        CONF.update_widgets_from_settings()

    def connect_signals(self):
        self.save_action.triggered.connect(self.on_save_action_triggered)
        self.load_action.triggered.connect(self.on_load_action_triggered)
        self.export_action.triggered.connect(self.on_export_action_triggered)
        self.view_logs_action.triggered.connect(self.on_view_logs_action_triggered)

        self.exit_action.triggered.connect(self.close)

        self.controls_area.analyzer_controls.analyzerConnected.connect(self.on_analyzer_connected)
        self.controls_area.analyzer_controls.analyzerDisonnected.connect(self.on_analyzer_disconnected)
        self.controls_area.positioner_controls.positionerConnected.connect(self.on_positioner_connected)
        self.controls_area.positioner_controls.positionerDisonnected.connect(self.on_positioner_disconnected)

        self.az_scan_btn.pressed.connect(self.on_az_scan_btn_pressed)
        self.el_scan_btn.pressed.connect(self.on_el_scan_btn_pressed)
        self.full_scan_btn.pressed.connect(self.on_full_scan_btn_pressed)
        self.abort_btn.pressed.connect(self.on_abort_btn_pressed)

    def closeEvent(self, event: QCloseEvent) -> None:
        quit_dlg = QMessageBox.warning(
            self,
            "Are you sure?",
            "Any unsaved data will be lost. Are you sure you want to quit?",
            QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Ok,
        )
        if quit_dlg == QMessageBox.Ok:
            if self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
            return super().closeEvent(event)
        else:
            event.ignore()

    def on_save_action_triggered(self):
        pass

    def on_load_action_triggered(self):
        pass

    def on_export_action_triggered(self):
        pass

    def on_view_logs_action_triggered(self):
        self.log_dialog.show()

    def on_analyzer_connected(self):
        if self.controls_area.positioner_controls.positioner is not None:
            self.set_scan_btns_enabled(True)

        self.set_pol_params()

    def on_analyzer_disconnected(self):
        self.set_scan_btns_enabled(False)

    def on_positioner_connected(self):
        if self.controls_area.analyzer_controls.analyzer is not None:
            self.set_scan_btns_enabled(True)

    def on_positioner_disconnected(self):
        self.set_scan_btns_enabled(False)

    def on_abort_btn_pressed(self) -> None:
        if self.thread.isRunning():
            self.thread.requestInterruption()

    def on_az_scan_btn_pressed(self) -> None:
        start = CONF["az_start"]
        stop = CONF["az_stop"]
        step = CONF["az_step"]
        azs = np.arange(start, stop + step, step)
        els = np.array([self.positioner.elevation])

        self.total_progress_gb.show()
        self.cut_progress_gb.hide()
        self.time_remaining_gb.show()

        self.total_progress_bar.setMaximum(len(azs))
        self.time_remaining_le.setText("00:00:00")

        pols = self.experiment_controls.polarizations
        self.run_scan(azs, els, pols)

    def on_el_scan_btn_pressed(self) -> None:
        pass

    def on_full_scan_btn_pressed(self) -> None:
        pass

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

    def set_scan_btns_enabled(self, state: bool) -> None:
        self.full_scan_btn.setEnabled(state)
        self.az_scan_btn.setEnabled(state)
        self.el_scan_btn.setEnabled(state)

    def set_controls_enabled(self, state: bool) -> None:
        self.experiment_controls.widget.setEnabled(state)
        self.analyzer_controls.widget.setEnabled(state)
        self.positioner_controls.enable_on_jog_completed = state
        self.positioner_controls.widget.setEnabled(state)

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
        params = self.controls_area.analyzer_controls.available_params
        self.controls_area.experiment_controls.update_params(params)

    def run_scan(self, phis: np.ndarray, thetas: np.ndarray, polarizations: list[tuple[str, int, int]]) -> None:
        freq = self.analyzer_controls.frequency
        self.results = ExperimentResult(thetas, phis, [p[0] for p in polarizations], freq)
        self.plot_dock_widget.results = self.results

        self.worker = ExperimentWorker(self.analyzer, self.positioner, phis, thetas, polarizations)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.worker.started.connect(self.on_experiment_started)
        self.worker.dataAcquired.connect(self.results.append)
        self.worker.totalIterCountUpdated.connect(self.on_total_progress_updated)
        self.worker.cutIterCountUpdated.connect(self.on_cut_progress_updated)
        self.worker.timeEstUpdated.connect(self.on_time_est_updated)
        self.worker.finished.connect(self.on_experiment_finished)
        self.worker.finished.connect(self.total_progress_gb.hide)
        self.worker.finished.connect(self.time_remaining_gb.hide)
        self.worker.finished.connect(self.cut_progress_gb.hide)

        self.thread.start()

    def run_test_scan(self):
        timer = QTimer(self)
        timer.setInterval(100)
        self.stop_test_btn.pressed.connect(timer.stop)
        self.status_label.setText("Running")

        thetas = np.arange(-180, 181, 1)
        phis = np.arange(-90, 91, 1)
        P, T = np.meshgrid(np.deg2rad(phis), np.deg2rad(thetas))
        ntwk = np.sinc(T) * np.sinc(P)
        index = iter(range(0, len(thetas) * len(phis)))
        freq = skrf.Frequency(start=1_000_000, stop=3_000_000, npoints=11, unit="Hz")

        self.results = ExperimentResult(thetas, phis, ["Horizontal"], freq)
        self.plot_dock_widget.results = self.results

        def append_data():
            try:
                i = next(index)
            except StopIteration:
                self.status_label.setText("Finished")
                timer.stop()
                return
            p, t = divmod(i, len(thetas))
            self.current_phi.setText(f"{phis[p]:.3g}")
            self.current_theta.setText(f"{thetas[t]:.3g}")
            val = skrf.Network()
            val.frequency = freq.copy()
            val.params = {"polarization": "Horizontal", "phi": phis[p], "theta": thetas[t]}
            val.s = np.repeat(ntwk[t, p], 11).reshape((-1, 1, 1))

            self.results.append(val)

        timer.timeout.connect(append_data)
        timer.start()
