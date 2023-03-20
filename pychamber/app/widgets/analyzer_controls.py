import functools
import itertools
from operator import setitem

import pyvisa
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QWidget
from skrf.vi import vna

from pychamber.app.ui.analyzer_widget import Ui_AnalyzerWidget
from pychamber.settings import CONF

from .collapsible_widget import CollapsibleWidget


class AnalyzerWidget(QWidget, Ui_AnalyzerWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setupUi(self)


class AnalyzerControls(CollapsibleWidget):
    # _analyzer_constructur_fns is defined as
    # {
    #     '<manufacturer>': {
    #         '<model>': <scikit-rf vi.vna constructor function>
    #     }
    # }
    # Doing it this way allows the model dropdown to be categorized by
    # manufacturer to make it easier for users to find their VNA.
    _analyzer_constructor_fns = {
        "Keysight": {
            "PNA": vna.PNA,
        },
    }

    analyzerConnected = Signal()
    analyzerDisonnected = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, name="Analyzer")

        self.analyzer: vna.VNA | None = None

        self.setupUi()
        self.postvisible_setup()
        self.connect_signals()

    def setupUi(self) -> None:
        self.widget: AnalyzerWidget = AnalyzerWidget(self)
        self.addWidget(self.widget)
        self.recalculateSize()

    def connect_signals(self) -> None:
        self.widget.connect_btn.clicked.connect(self.on_connect_btn_clicked)
        self.widget.disconnect_btn.clicked.connect(self.on_disconnect_btn_clicked)

        self.widget.model_cb.currentTextChanged.connect(functools.partial(setitem, CONF, "analyzer_model"))
        self.widget.address_cb.currentTextChanged.connect(functools.partial(setitem, CONF, "analyzer_address"))

    def postvisible_setup(self) -> None:
        widget_map = {
            # TODO: Make settings handle CategoryComboBox maybe?
            "analyzer_address": (self.widget.address_cb, "", str),
        }
        CONF.register_widgets(widget_map)

        self.widget.disconnect_btn.hide()
        self.widget.freq_gb.setEnabled(False)

        self.add_models()
        self.widget.address_cb.addItems(self.available_addresses)

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
            self.analyzer = model(address)
        except Exception:
            QMessageBox.critical(self, "Connection Error", "Failed to connect to analyzer")
            return

        self.widget.connect_btn.hide()
        self.widget.disconnect_btn.show()
        self.widget.frequency_gb.setEnabled(True)
        self.analyzerConnected.emit()

    def on_disconnect_btn_clicked(self) -> None:
        self.analyzer.close()
        self.widget.connect_btn.hide()
        self.widget.disconnect_btn.show()
        self.widget.frequency_gb.setEnabled(False)
        self.analyzerDisonnected.emit()

    @property
    def available_analyzer_models(self) -> dict:
        return self._analyzer_constructor_fns

    @property
    def available_addresses(self) -> list[str]:
        backend = "@py"
        rm = pyvisa.ResourceManager(backend)
        available = rm.list_resources()
        rm.close()
        return list(available)

    @property
    def available_params(self) -> list[tuple[int, int]]:
        # TODO: Update to nports when new vi implementation is merged
        port_nums = list(range(1, self.analyzer.NPORTS + 1))
        return itertools.product(port_nums, repeat=2)

    def add_models(self) -> None:
        for manufacturer, models in self.available_analyzer_models.items():
            self.widget.model_cb.add_parent(manufacturer)
            for model, fn in models.items():
                self.widget.model_cb.add_child(model, fn)

        self.widget.model_cb.setCurrentIndex(1)  # index 0 will be a category which we don't want to be selectable
