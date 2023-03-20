import qtawesome as qta
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QWidget
from serial.tools import list_ports

from pychamber import positioner
from pychamber.app.ui.positioner_widget import Ui_PositionerWidget

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

        self.positioner: positioner.Postioner | None = None

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

    def postvisible_setup(self) -> None:
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
            model_name = self.widget.model_cb.currentText()
            address = self.widget.address_cb.currentText()
            self.positioner = positioner.connect(model_name, address)
        except Exception:
            QMessageBox.critical(self, "Connection Error", "Failed to connect to to positioner")
            return

        self.model_widget = self.positioner.widget
        if self.model_widget is not None:
            self.widget.controls_layout.addWidget(self.model_widget)

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

    def set_enabled(self, enable: bool) -> None:
        self.widget.az_gb.setEnabled(enable)
        self.widget.el_gb.setEnabled(enable)
        self.widget.set_origin_btn.setEnabled(enable)
        self.widget.return_to_origin_btn.setEnabled(enable)
        self.recalculateSize()

    def add_models(self):
        for manufacturer, models in positioner.available_models().items():
            self.widget.model_cb.add_parent(manufacturer)
            for model, fn in models.items():
                self.widget.model_cb.add_child(model, fn)

        self.widget.model_cb.setCurrentIndex(1)  # index 0 will be a category which we don't want to be selectable
