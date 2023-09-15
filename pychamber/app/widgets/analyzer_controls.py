from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import skrf

import functools
import itertools
from operator import setitem

import pyvisa
from qtpy.QtCore import QThreadPool, Signal
from qtpy.QtWidgets import QMessageBox, QWidget
from skrf.vi import vna

from pychamber.app.logger import LOG
from pychamber.app.task_runner import TaskRunner
from pychamber.app.ui.analyzer_widget import Ui_AnalyzerWidget
from pychamber.settings import CONF


class AnalyzerControls(QWidget, Ui_AnalyzerWidget):
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
        super().__init__(parent)

        self.analyzer: vna.VNA | None = None

        LOG.debug("Setting up UI")
        self.setupUi(self)

        LOG.debug("Registering widgets with settings")
        widget_map = {
            # TODO: Make settings handle CategoryComboBox maybe?
            "analyzer_address": (self.address_cb, "", str),
        }
        CONF.register_widgets(widget_map)

    def connect_signals(self) -> None:
        LOG.debug("Connecting signals")
        self.connect_btn.clicked.connect(self.on_connect_btn_clicked)
        self.disconnect_btn.clicked.connect(self.on_disconnect_btn_clicked)

        self.model_cb.currentTextChanged.connect(functools.partial(setitem, CONF, "analyzer_model"))
        self.address_cb.currentTextChanged.connect(functools.partial(setitem, CONF, "analyzer_address"))

        self.freq_start_le.editingFinished.connect(self.on_freq_start_changed)
        self.freq_stop_le.editingFinished.connect(self.on_freq_stop_changed)
        self.freq_step_le.editingFinished.connect(self.on_freq_step_changed)
        self.freq_n_points_le.editingFinished.connect(self.on_freq_n_points_changed)
        self.if_bw_le.editingFinished.connect(self.on_if_bw_changed)
        self.avg_toggle.toggled.connect(lambda state: self.on_avg_toggle_changed(state))
        self.n_avgs_sb.valueChanged.connect(lambda n: self.on_n_avgs_changed(n))

    def postvisible_setup(self) -> None:
        self.disconnect_btn.hide()
        self.freq_gb.setEnabled(False)

        LOG.debug("Populating model combobox")
        self.add_models()

        # This function calls sleep making start-up SLOW
        # So we move it into a thread to allow the GUI to be shown
        # as early as possible
        def get_addrs():
            backend = CONF["visalib"]
            LOG.debug(f"VISA backend: {backend}")
            rm = pyvisa.ResourceManager(backend)
            available = rm.list_resources()
            rm.close()
            return list(available)

        addr_updater = TaskRunner(get_addrs)
        addr_updater.signals.gotResult.connect(self.address_cb.addItems)
        QThreadPool.globalInstance().start(addr_updater)

    def on_connect_btn_clicked(self) -> None:
        LOG.info("Attempting to connect to analyzer")
        if self.model_cb.currentText() == "":
            QMessageBox.information(self, "No Model Specified", "Must select a model before attempting to connect")
            return
        if self.address_cb.currentText() == "":
            QMessageBox.information(self, "No Address Specified", "Must select an address before attempting to connect")
            return

        try:
            model = self.model_cb.currentData()
            address = self.address_cb.currentText()
            self.analyzer = model(address, backend=CONF["visalib"])
        except Exception as e:
            LOG.error(f"Failed to connect to analyzer: {e}")
            QMessageBox.critical(self, "Connection Error", "Failed to connect to analyzer")
            return
        self.analyzer._resource.timeout = 30_000  # 30 Seconds

        self.connect_btn.hide()
        self.disconnect_btn.show()
        self.model_cb.setEnabled(False)
        self.address_cb.setEnabled(False)
        self.freq_gb.setEnabled(True)
        to_block = [*self.freq_gb.children(), self.if_bw_le, self.avg_toggle, self.n_avgs_sb]
        for widget in to_block:
            widget.blockSignals(True)
        self.init_widgets()
        for widget in to_block:
            widget.blockSignals(False)
        self.analyzerConnected.emit()

    def on_disconnect_btn_clicked(self) -> None:
        LOG.info("Disconnecting analyzer")
        self.analyzer = None
        self.connect_btn.hide()
        self.disconnect_btn.show()
        self.freq_gb.setEnabled(False)
        self.model_cb.setEnabled(True)
        self.address_cb.setEnabled(True)
        self.analyzerDisonnected.emit()

    def on_freq_start_changed(self) -> None:
        freq = self.freq_start_le.text()
        LOG.debug(f"Changing frequency start: {freq}")
        self.analyzer.ch1.freq_start = freq

    def on_freq_stop_changed(self) -> None:
        freq = self.freq_stop_le.text()
        LOG.debug(f"Changing frequency stop: {freq}")
        self.analyzer.ch1.freq_stop = freq

    def on_freq_step_changed(self) -> None:
        freq = self.freq_step_le.text()
        LOG.debug(f"Changing frequency step: {freq}")
        self.analyzer.ch1.freq_step = freq
        npoints = self.analyzer.ch1.npoints
        self.freq_n_points_le.setText(str(npoints))

    def on_freq_n_points_changed(self) -> None:
        npoints = int(self.freq_n_points_le.text())
        LOG.debug(f"Changing frequency points: {npoints}")
        self.analyzer.ch1.npoints = npoints
        step = self.analyzer.ch1.freq_step
        self.freq_step_le.setText(str(step))

    def on_if_bw_changed(self) -> None:
        freq = self.if_bw_le.text()
        LOG.debug(f"Changing IF bandwidth: {freq}")
        self.analyzer.ch1.if_bandwidth = freq

    def on_avg_toggle_changed(self, state: bool) -> None:
        LOG.debug(f"Toggling averaging: {state}")
        self.analyzer.ch1.averaging_on = state

    def on_n_avgs_changed(self, n: int) -> None:
        LOG.debug(f"Changing number of averages: {n}")
        self.analyzer.ch1.averaging_count = n

    @property
    def available_analyzer_models(self) -> dict:
        return self._analyzer_constructor_fns

    @property
    def available_addresses(self) -> list[str]:
        backend = CONF["visalib"]
        LOG.debug(f"VISA backend: {backend}")
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
            self.model_cb.add_parent(manufacturer)
            for model, fn in models.items():
                self.model_cb.add_child(model, fn)

        self.model_cb.setCurrentIndex(1)  # index 0 will be a category which we don't want to be selectable

    def init_widgets(self) -> None:
        # TODO: For scikit-rf. Figure out how to make ch1 default
        freq_start = self.analyzer.ch1.freq_start
        freq_stop = self.analyzer.ch1.freq_stop
        freq_step = self.analyzer.ch1.freq_step
        npoints = self.analyzer.ch1.npoints
        if_bw = self.analyzer.ch1.if_bandwidth
        avg_on = self.analyzer.ch1.averaging_on

        to_block = [
            self.freq_start_le,
            self.freq_stop_le,
            self.freq_step_le,
            self.freq_n_points_le,
            self.if_bw_le,
            self.avg_toggle,
            self.n_avgs_sb,
        ]

        for widget in to_block:
            widget.blockSignals(True)

        self.freq_start_le.setText(str(freq_start))
        self.freq_stop_le.setText(str(freq_stop))
        self.freq_step_le.setText(str(freq_step))
        self.freq_n_points_le.setText(str(npoints))
        self.if_bw_le.setText(str(if_bw))
        self.avg_toggle.setChecked(avg_on)

        if avg_on:
            self.avg_toggle.handle_position = 1
            n_avgs = self.analyzer.ch1.averaging_count
            self.n_avgs_sb.setValue(n_avgs)

        for widget in to_block:
            widget.blockSignals(False)
