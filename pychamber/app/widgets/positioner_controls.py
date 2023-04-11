from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import functools
from operator import setitem

import qtawesome as qta
from qtpy.QtCore import QEventLoop, QThread, QTimer, Signal
from qtpy.QtGui import QCloseEvent
from qtpy.QtWidgets import QMessageBox, QWidget
from serial.tools import list_ports

from pychamber import positioner
from pychamber.app.logger import LOG
from pychamber.app.ui.positioner_widget import Ui_PositionerWidget
from pychamber.settings import CONF


class PositionerControls(QWidget, Ui_PositionerWidget):
    positionerConnected = Signal()
    positionerDisonnected = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.jog_thread = QThread(None)
        self.positioner: positioner.Positioner | None = None
        self.enable_on_jog_completed = True

        LOG.debug("Setting up UI")
        self.setupUi(self)

        LOG.debug("Registering widgets with settings")
        widget_map = {
            "jog_phi_step": (self.phi_step_dsb, 0, float),
            "jog_phi_to": (self.phi_jog_to_dsb, 0, float),
            "jog_theta_step": (self.theta_step_dsb, 0, float),
            "jog_theta_to": (self.theta_jog_to_dsb, 0, float),
        }
        CONF.register_widgets(widget_map)


    # This is gross...but idk what else to do to get the collapsible widgets to
    # work with dynamic content...will try to fix later
    def sizeHint(self):
        size = super().sizeHint()
        size.setHeight(size.height() + 150)
        return size

    def connect_signals(self) -> None:
        LOG.debug("Connecting signals")
        self.connect_btn.clicked.connect(self.on_connect_btn_clicked)
        self.disconnect_btn.clicked.connect(self.on_disconnect_btn_clicked)

        self.phi_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_phi_step"))
        self.phi_jog_to_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_phi_to"))
        self.theta_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_theta_step"))
        self.theta_jog_to_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_theta_to"))

        self.phi_minus_btn.pressed.connect(self.on_phi_minus_btn_pressed)
        self.phi_zero_btn.pressed.connect(self.on_phi_zero_btn_pressed)
        self.phi_plus_btn.pressed.connect(self.on_phi_plus_btn_pressed)
        self.theta_minus_btn.pressed.connect(self.on_theta_minus_btn_pressed)
        self.theta_zero_btn.pressed.connect(self.on_theta_zero_btn_pressed)
        self.theta_plus_btn.pressed.connect(self.on_theta_plus_btn_pressed)

        self.phi_jog_to_btn.pressed.connect(self.on_phi_jog_to_btn_pressed)
        self.theta_jog_to_btn.pressed.connect(self.on_theta_jog_to_btn_pressed)

        self.set_origin_btn.pressed.connect(self.on_set_zero_btn_pressed)
        self.return_to_origin_btn.pressed.connect(self.on_return_to_origin_pressed)

    def postvisible_setup(self) -> None:
        minus_icon = qta.icon("fa5s.minus")
        plus_icon = qta.icon("fa5s.plus")
        check_icon = qta.icon("fa5s.check")
        self.phi_minus_btn.setIcon(minus_icon)
        self.phi_plus_btn.setIcon(plus_icon)
        self.theta_minus_btn.setIcon(minus_icon)
        self.theta_plus_btn.setIcon(plus_icon)
        self.phi_jog_to_btn.setIcon(check_icon)
        self.theta_jog_to_btn.setIcon(check_icon)

        self.set_enabled(False)
        self.disconnect_btn.hide()

        LOG.debug("Populating model combobox")
        self.add_models()

        self.address_cb.clear()
        ports = [p.device for p in list_ports.comports()]
        self.address_cb.addItems(ports)

    def on_connect_btn_clicked(self) -> None:
        LOG.debug("Attempting to connect to positioner")
        if self.model_cb.currentText() == "":
            QMessageBox.information(self, "No Model Specified", "Must select a model before attempting to connect")
            return
        if self.address_cb.currentText() == "" and self.model_cb.currentText() != "Example Positioner":
            QMessageBox.information(self, "No Address Specified", "Must select an address before attempting to connect")
            return

        try:
            model = self.model_cb.currentData()
            address = self.address_cb.currentText()
            self.positioner = model(address)
        except Exception as e:
            LOG.error(str(e))
            QMessageBox.critical(self, "Connection Error", "Failed to connect to to positioner")
            return

        self.model_widget = self.positioner.create_widget()
        if self.model_widget is not None:
            self.controls_widget.layout().insertWidget(self.controls_widget.layout().count() - 1, self.model_widget)

        self.positioner.jogStarted.connect(self.on_jog_started)
        self.positioner.jogCompleted.connect(self.on_jog_completed)

        self.current_phi_lcd_num.display(self.positioner.phi)
        self.current_theta_lcd_num.display(self.positioner.theta)

        self.connect_btn.hide()
        self.disconnect_btn.show()
        self.set_enabled(True)
        self.model_cb.setEnabled(False)
        self.address_cb.setEnabled(False)
        self.positionerConnected.emit()

    def on_disconnect_btn_clicked(self) -> None:
        LOG.info("Disconnecting from positioner")
        self.positioner = None
        self.connect_btn.show()
        self.disconnect_btn.hide()
        self.model_cb.setEnabled(True)
        self.address_cb.setEnabled(True)
        self.set_enabled(False)
        if self.model_widget is not None:
            self.model_widget.setParent(None)
            del self.model_widget
        self.positionerDisonnected.emit()

    def on_phi_minus_btn_pressed(self) -> None:
        angle = self.phi_step_dsb.value()
        LOG.debug(f"Jogging phi -{angle}")
        jog_fn = functools.partial(self.positioner.move_phi_relative, -angle)
        self.run_jog_thread(jog_fn)

    def on_phi_zero_btn_pressed(self) -> None:
        LOG.debug("Jogging phi to zero")
        jog_fn = functools.partial(self.positioner.move_phi_absolute, 0)
        self.run_jog_thread(jog_fn)

    def on_phi_plus_btn_pressed(self) -> None:
        angle = self.phi_step_dsb.value()
        LOG.debug(f"Jogging phi +{angle}")
        jog_fn = functools.partial(self.positioner.move_phi_relative, angle)
        self.run_jog_thread(jog_fn)

    def on_theta_minus_btn_pressed(self) -> None:
        angle = self.theta_step_dsb.value()
        LOG.debug(f"Jogging theta -{angle}")
        jog_fn = functools.partial(self.positioner.move_theta_relative, -angle)
        self.run_jog_thread(jog_fn)

    def on_theta_zero_btn_pressed(self) -> None:
        LOG.debug("Jogging theta to zero")
        jog_fn = functools.partial(self.positioner.move_theta_absolute, 0)
        self.run_jog_thread(jog_fn)

    def on_theta_plus_btn_pressed(self) -> None:
        angle = self.theta_step_dsb.value()
        LOG.debug(f"Jogging theta +{angle}")
        jog_fn = functools.partial(self.positioner.move_theta_relative, angle)
        self.run_jog_thread(jog_fn)

    def on_phi_jog_to_btn_pressed(self) -> None:
        target = self.phi_jog_to_dsb.value()
        LOG.debug(f"Jogging phi to {target}")
        jog_fn = functools.partial(self.positioner.move_phi_absolute, target)
        self.run_jog_thread(jog_fn)

    def on_theta_jog_to_btn_pressed(self) -> None:
        target = self.theta_jog_to_dsb.value()
        LOG.debug(f"Jogging theta to {target}")
        jog_fn = functools.partial(self.positioner.move_theta_absolute, target)
        self.run_jog_thread(jog_fn)

    def on_set_zero_btn_pressed(self) -> None:
        LOG.debug("Setting origin")
        self.positioner.zero_all()
        self.current_phi_lcd_num.display(0.0)
        self.current_theta_lcd_num.display(0.0)

    def on_return_to_origin_pressed(self) -> None:
        LOG.debug("Returning to origin")
        jog_phi_zero_fn = functools.partial(self.positioner.move_phi_absolute, 0)
        jog_theta_zero_fn = functools.partial(self.positioner.move_theta_absolute, 0)
        # Need to enable and disable on our own because
        # _wait_for runs its own event loop
        self.enable_on_jog_completed = False
        self.set_enabled(False)
        self._wait_for(
            jog_phi_zero_fn,
            self.positioner.jogCompleted,
            timeout=None,
        )
        self._wait_for(
            jog_theta_zero_fn,
            self.positioner.jogCompleted,
            timeout=None,
        )
        self.enable_on_jog_completed = True
        self.set_enabled(True)

    def on_jog_started(self) -> None:
        LOG.debug("Jog starting")
        self.set_enabled(False)

    def on_jog_completed(self) -> None:
        LOG.debug("Jog completed")
        phi = self.positioner.phi
        theta = self.positioner.theta
        self.current_phi_lcd_num.display(phi)
        self.current_theta_lcd_num.display(theta)
        self.set_enabled(self.enable_on_jog_completed)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.jog_thread.quit()
        self.jog_thread.wait()
        super().closeEvent(event)

    def set_enabled(self, enable: bool) -> None:
        self.phi_gb.setEnabled(enable)
        self.theta_gb.setEnabled(enable)
        self.set_origin_btn.setEnabled(enable)
        self.return_to_origin_btn.setEnabled(enable)

    def add_models(self):
        LOG.debug("Adding positioner models")
        for manufacturer, models in positioner.available_models().items():
            self.model_cb.add_parent(manufacturer)
            for model, fn in models.items():
                self.model_cb.add_child(model, fn)

        self.model_cb.setCurrentIndex(1)  # index 0 will be a category which we don't want to be selectable

    def run_jog_thread(self, jog_fn: Callable) -> None:
        self.jog_thread.run = jog_fn
        self.jog_thread.start()

    def _wait_for(self, fn: Callable, signal, timeout: int | None = 5000) -> None:
        event_loop = QEventLoop()
        signal.connect(event_loop.quit)
        QTimer.singleShot(0, fn)

        if timeout is not None:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(event_loop.quit)
            timer.start()

        event_loop.exec()
