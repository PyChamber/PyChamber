import functools
from operator import setitem

import qtawesome as qta
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMessageBox, QWidget
from serial.tools import list_ports

from pychamber import positioner
from pychamber.app.ui.positioner_widget import Ui_PositionerWidget
from pychamber.settings import CONF

from . import CollapsibleWidget


class PositionerWidget(QWidget, Ui_PositionerWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)


class PositionerControls(CollapsibleWidget):
    positionerConnected = Signal()
    positionerDisonnected = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, name="Positioner")

        self.jog_thread = QThread(None)
        self.positioner: positioner.Postioner | None = None
        self.enable_on_jog_completed = False

        self.setupUi()
        self.postvisible_setup()
        self.connect_signals()

    def setupUi(self) -> None:
        self.widget = PositionerWidget(self)

        left_icon = qta.icon("fa5s.arrow-left")
        self.widget.az_left_btn.setIcon(left_icon)
        right_icon = qta.icon("fa5s.arrow-right")
        self.widget.az_right_btn.setIcon(right_icon)
        ccw_icon = qta.icon("ph.arrow-counter-clockwise-bold")
        self.widget.el_ccw_btn.setIcon(ccw_icon)
        cw_icon = qta.icon("ph.arrow-clockwise-bold")
        self.widget.el_cw_btn.setIcon(cw_icon)
        check_icon = qta.icon("fa5s.check")
        self.widget.az_jog_to_btn.setIcon(check_icon)
        self.widget.el_jog_to_btn.setIcon(check_icon)

        self.addWidget(self.widget)
        self.recalculateSize()

    def connect_signals(self) -> None:
        self.widget.connect_btn.clicked.connect(self.on_connect_btn_clicked)
        self.widget.disconnect_btn.clicked.connect(self.on_disconnect_btn_clicked)

        self.widget.az_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_az_step"))
        self.widget.az_jog_to_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_az_to"))
        self.widget.el_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_el_step"))
        self.widget.el_jog_to_dsb.valueChanged.connect(functools.partial(setitem, CONF, "jog_el_to"))

        self.widget.az_left_btn.pressed.connect(self.on_az_left_btn_pressed)
        self.widget.az_zero_btn.pressed.connect(self.on_az_zero_btn_pressed)
        self.widget.az_right_btn.pressed.connect(self.on_az_right_btn_pressed)
        self.widget.el_ccw_btn.pressed.connect(self.on_el_ccw_btn_pressed)
        self.widget.el_zero_btn.pressed.connect(self.on_el_zero_btn_pressed)
        self.widget.el_cw_btn.pressed.connect(self.on_el_cw_btn_pressed)

        self.widget.az_jog_to_btn.pressed.connect(self.on_az_jog_to_btn_pressed)
        self.widget.el_jog_to_btn.pressed.connect(self.on_el_jog_to_btn_pressed)

        self.widget.set_origin_btn.pressed.connect(self.on_set_zero_btn_pressed)
        self.widget.return_to_origin_btn.pressed.connect(self.on_return_to_origin_pressed)

    def postvisible_setup(self) -> None:
        widget_map = {
            "jog_az_step": (self.widget.az_step_dsb, 0, float),
            "jog_az_to": (self.widget.az_jog_to_dsb, 0, float),
            "jog_el_step": (self.widget.el_step_dsb, 0, float),
            "jog_el_to": (self.widget.el_jog_to_dsb, 0, float),
        }
        CONF.register_widgets(widget_map)

        self.set_enabled(False)
        self.widget.disconnect_btn.hide()

        self.add_models()

        self.widget.address_cb.clear()
        ports = [p.device for p in list_ports.comports()]
        self.widget.address_cb.addItems(ports)

    def on_connect_btn_clicked(self) -> None:
        if self.widget.model_cb.currentText() == "":
            QMessageBox.information(self, "No Model Specified", "Must select a model before attempting to connect")
            return
        if self.widget.address_cb.currentText() == "":
            QMessageBox.information(self, "No Address Specified", "Must select an address before attempting to connect")
            return

        try:
            model = self.widget.model_cb.currentData()
            address = self.widget.address_cb.currentText()
            self.positioner = model(address)
        except Exception:
            QMessageBox.critical(self, "Connection Error", "Failed to connect to to positioner")
            return

        # FIXME: This is an issue with CollapsibleSection
        # self.model_widget = self.positioner.create_widget(None)
        # if self.model_widget is not None:
        #     print(self.model_widget.sizeHint())
        #     self.addWidget(self.model_widget)

        self.positioner.jogStarted.connect(self.on_jog_started)
        self.positioner.jogCompleted.connect(self.on_jog_completed)

        self.widget.current_az_lcd_num.display(self.positioner.azimuth)
        self.widget.current_el_lcd_num.display(self.positioner.elevation)

        self.widget.connect_btn.hide()
        self.widget.disconnect_btn.show()
        self.set_enabled(True)
        self.positionerConnected.emit()

    def on_disconnect_btn_clicked(self) -> None:
        self.positioner = None
        self.widget.connect_btn.show()
        self.widget.disconnect_btn.hide()
        self.set_enabled(False)
        self.positionerDisonnected.emit()

    def on_az_left_btn_pressed(self) -> None:
        angle = self.widget.az_step_dsb.value()
        jog_fn = functools.partial(self.positioner.move_az_relative, -angle)
        self.run_jog_thread(jog_fn)

    def on_az_zero_btn_pressed(self) -> None:
        jog_fn = functools.partial(self.positioner.move_az_absolute, 0)
        self.run_jog_thread(jog_fn)

    def on_az_right_btn_pressed(self) -> None:
        angle = self.widget.az_step_dsb.value()
        jog_fn = functools.partial(self.positioner.move_az_relative, angle)
        self.run_jog_thread(jog_fn)

    def on_el_ccw_btn_pressed(self) -> None:
        angle = self.widget.el_step_dsb.value()
        jog_fn = functools.partial(self.positioner.move_el_relative, -angle)
        self.run_jog_thread(jog_fn)

    def on_el_zero_btn_pressed(self) -> None:
        jog_fn = functools.partial(self.positioner.move_el_absolute, 0)
        self.run_jog_thread(jog_fn)

    def on_el_cw_btn_pressed(self) -> None:
        angle = self.widget.el_step_dsb.value()
        jog_fn = functools.partial(self.positioner.move_el_relative, angle)
        self.run_jog_thread(jog_fn)

    def on_az_jog_to_btn_pressed(self) -> None:
        target = self.widget.az_jog_to_dsb.value()
        jog_fn = functools.partial(self.positioner.move_az_absolute, target)
        self.run_jog_thread(jog_fn)

    def on_el_jog_to_btn_pressed(self) -> None:
        target = self.widget.el_jog_to_dsb.value()
        jog_fn = functools.partial(self.positioner.move_el_absolute, target)
        self.run_jog_thread(jog_fn)

    def on_set_zero_btn_pressed(self) -> None:
        self.positioner.zero_all()
        self.widget.current_az_lcd_num.display(0.0)
        self.widget.current_el_lcd_num.display(0.0)

    def on_return_to_origin_pressed(self) -> None:
        pass  # FIXME: Thread shenaningans

    def on_jog_started(self) -> None:
        self.setEnabled(False)

    def on_jog_completed(self) -> None:
        az = self.positioner.azimuth
        el = self.positioner.elevation
        self.widget.current_az_lcd_num.display(az)
        self.widget.current_el_lcd_num.display(el)
        self.setEnabled(True and self.enable_on_jog_completed)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.jog_thread.quit()
        self.jog_thread.wait()
        super().closeEvent(event)

    def set_enabled(self, enable: bool) -> None:
        self.widget.az_gb.setEnabled(enable)
        self.widget.el_gb.setEnabled(enable)
        self.widget.set_origin_btn.setEnabled(enable)
        self.widget.return_to_origin_btn.setEnabled(enable)

    def add_models(self):
        for manufacturer, models in positioner.available_models().items():
            self.widget.model_cb.add_parent(manufacturer)
            for model, fn in models.items():
                self.widget.model_cb.add_child(model, fn)

        self.widget.model_cb.setCurrentIndex(1)  # index 0 will be a category which we don't want to be selectable

    def run_jog_thread(self, jog_fn: callable) -> None:
        self.jog_thread.run = jog_fn
        self.jog_thread.start()
