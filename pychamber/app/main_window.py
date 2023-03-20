from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychamber.positioner import Postioner

import numpy as np
import skrf
from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox

from pychamber.app.objects import ExperimentWorker
from pychamber.app.ui.mainwindow import Ui_MainWindow
from pychamber.app.widgets import LogDialog
from pychamber.settings import CONF


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.log_dialog = LogDialog()

        self.setupUi(self)
        self.connect_signals()
        self.post_visible_setup()

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
        self.controls_area.analyzer_controls.analyzerConnected.connect(
            lambda: self.controls_area.experiment_controls.update_params(self.analyzer.available_params)
        )
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

        self.set_pol_params(self.analyzer.available_params)

    def on_analyzer_disconnected(self):
        self.set_scan_btns_enabled(False)

    def on_positioner_connected(self):
        if self.controls_area.analyzer_controls.analyzer is not None:
            self.set_scan_btns_enabled(True)

    def on_positioner_disconnected(self):
        self.set_scan_btns_enabled(False)

    def on_abort_btn_pressed(self) -> None:
        # FIXME: How to do...
        pass

    def on_az_scan_btn_pressed(self) -> None:
        start = CONF["az_start"]
        stop = CONF["az_stop"]
        step = CONF["az_step"]
        azs = np.arange(start, stop + step, step)
        els = np.array([self.positioner.elevation])
        self.run_scan(azs, els)

    def on_el_scan_btn_pressed(self) -> None:
        pass

    def on_full_scan_btn_pressed(self) -> None:
        pass

    def set_scan_btns_enabled(self, state: bool) -> None:
        self.full_scan_btn.setEnabled(state)
        self.az_scan_btn.setEnabled(state)
        self.el_scan_btn.setEnabled(state)

    @property
    def analyzer(self) -> skrf.vi.VNA | None:
        return self.controls_area.analyzer_controls.analyzer

    @property
    def positioner(self) -> Postioner | None:
        return self.controls_area.positioner_controls.positioner

    def run_scan(self, azimuths: np.ndarray, elevations: np.ndarray) -> None:
        self.thread = QThread()
        self.worker = ExperimentWorker(self.analyzer, self.positioner, azimuths, elevations, self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.dataAcquired.connect(lambda ntwk: print(ntwk))
        self.worker.totalIterCountUpdated.connect(self.on_total_progress_updated)
        self.worker.cutIterCountUpdated.connect(self.on_cut_progress_updated)
        self.worker.avgIterTimeUpdated.connect(self.on_avg_iter_time_updated)

        self.thread.start()
