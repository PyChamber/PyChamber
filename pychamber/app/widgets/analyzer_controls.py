from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import skrf

import functools
import itertools
from operator import setitem

import pyvisa
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QMessageBox, QWidget
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
            "PNA": vna.keysight.PNA,
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

        self.widget.freq_start_le.editingFinished.connect(self.on_freq_start_changed)
        self.widget.freq_stop_le.editingFinished.connect(self.on_freq_stop_changed)
        self.widget.freq_step_le.editingFinished.connect(self.on_freq_step_changed)
        self.widget.freq_n_points_le.editingFinished.connect(self.on_freq_n_points_changed)
        self.widget.if_bw_le.editingFinished.connect(self.on_if_bw_changed)
        self.widget.avg_toggle.toggled.connect(lambda state: self.on_avg_toggle_changed(state))
        self.widget.n_avgs_sb.valueChanged.connect(lambda n: self.on_n_avgs_changed(n))

    def postvisible_setup(self) -> None:
        widget_map = {
            # TODO: Make settings handle CategoryComboBox maybe?
            "analyzer_address": (self.widget.address_cb, "", str),
            "visalib": (None, "@py", str),
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
            self.analyzer = model(address, backend=CONF["visalib"])
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", "Failed to connect to analyzer")
            print(e)
            return

        self.widget.connect_btn.hide()
        self.widget.disconnect_btn.show()
        self.widget.freq_gb.setEnabled(True)
        for widget in self.widget.freq_gb.children():
            widget.blockSignals(True)
        self.init_widgets()
        for widget in self.widget.freq_gb.children():
            widget.blockSignals(False)
        self.analyzerConnected.emit()

    def on_disconnect_btn_clicked(self) -> None:
        self.analyzer = None
        self.widget.connect_btn.hide()
        self.widget.disconnect_btn.show()
        self.widget.freq_gb.setEnabled(False)
        self.analyzerDisonnected.emit()

    def on_freq_start_changed(self) -> None:
        freq = self.widget.freq_start_le.text()
        self.analyzer.ch1.freq_start = freq

    def on_freq_stop_changed(self) -> None:
        freq = self.widget.freq_stop_le.text()
        self.analyzer.ch1.freq_stop = freq

    def on_freq_step_changed(self) -> None:
        freq = self.widget.freq_step_le.text()
        self.analyzer.ch1.freq_step = freq

    def on_freq_n_points_changed(self) -> None:
        npoints = int(self.widget.freq_n_points_le.text())
        self.analyzer.ch1.npoints = npoints

    def on_if_bw_changed(self) -> None:
        freq = self.widget.if_bw_le.text()
        self.analyzer.ch1.if_bandwidth = freq

    def on_avg_toggle_changed(self, state: bool) -> None:
        self.analyzer.ch1.averaging_on = state

    def on_n_avgs_changed(self, n: int) -> None:
        self.analyzer.ch1.averaging_count = n

    @property
    def available_analyzer_models(self) -> dict:
        return self._analyzer_constructor_fns

    @property
    def available_addresses(self) -> list[str]:
        backend = CONF["visalib"]
        rm = pyvisa.ResourceManager(backend)
        available = rm.list_resources()
        rm.close()
        return list(available)

    @property
    def available_params(self) -> list[tuple[int, int]]:
        port_nums = list(range(1, self.analyzer.nports + 1))
        return list(itertools.product(port_nums, repeat=2))

    @property
    def frequency(self) -> skrf.Frequency:
        return self.analyzer.ch1.frequency

    def add_models(self) -> None:
        for manufacturer, models in self.available_analyzer_models.items():
            self.widget.model_cb.add_parent(manufacturer)
            for model, fn in models.items():
                self.widget.model_cb.add_child(model, fn)

        self.widget.model_cb.setCurrentIndex(1)  # index 0 will be a category which we don't want to be selectable

    def init_widgets(self) -> None:
        # TODO: For scikit-rf. Figure out how to make ch1 default
        freq_start = self.analyzer.ch1.freq_start
        freq_stop = self.analyzer.ch1.freq_stop
        freq_step = self.analyzer.ch1.freq_step
        npoints = self.analyzer.ch1.npoints
        if_bw = self.analyzer.ch1.if_bandwidth
        avg_on = self.analyzer.ch1.averaging_on

        to_block = [
            self.widget.freq_start_le,
            self.widget.freq_stop_le,
            self.widget.freq_step_le,
            self.widget.freq_n_points_le,
            self.widget.if_bw_le,
            self.widget.avg_toggle,
            self.widget.n_avgs_sb,
        ]

        for widget in to_block:
            widget.blockSignals(True)

        self.widget.freq_start_le.setText(str(freq_start))
        self.widget.freq_stop_le.setText(str(freq_stop))
        self.widget.freq_step_le.setText(str(freq_step))
        self.widget.freq_n_points_le.setText(str(npoints))
        self.widget.if_bw_le.setText(str(if_bw))
        self.widget.avg_toggle.setChecked(avg_on)

        if avg_on:
            self.widget.avg_toggle.handle_position = 1
            n_avgs = self.analyzer.ch1.averaging_count
            self.widget.n_avgs_sb.setValue(n_avgs)

        for widget in to_block:
            widget.blockSignals(False)
