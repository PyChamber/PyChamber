from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional
    from pychamber.main_window import MainWindow

import itertools

import numpy as np
import pyvisa
import skrf
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from quantiphy import Quantity
from skrf.vi import vna

from pychamber.logger import log
from pychamber.polarization import Polarization
from pychamber.settings import SETTINGS
from pychamber.widgets import FrequencyLineEdit

from .base import PyChamberPanelPlugin


class AnalyzerPlugin(PyChamberPanelPlugin):
    NAME = "analyzer"
    CONFIG = {
        "backend": "",
        "model": "",
        "addr": "",
        "pol1-label": "",
        "pol1-param": "",
        "pol2-label": "",
        "pol2-param": "",
    }

    model = {
        "Keysight PNA": vna.PNA,
    }

    # Signals
    analyzer_connected = pyqtSignal()

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)

        self.setObjectName("analyzer")
        self.setLayout(QVBoxLayout())

        self._analyzer: Optional[vna.VNA] = None

        self.start_freq: Optional[Quantity] = None
        self.stop_freq: Optional[Quantity] = None
        self.freq_step: Optional[Quantity] = None
        self.n_points: Optional[int] = None

    def _setup(self) -> None:
        log.debug("Creating Analyzer widget...")
        self._add_widgets()

    def _post_visible_setup(self) -> None:
        log.debug("Post-visible setup")
        self._init_inputs()
        self._connect_signals()

    def _add_widgets(self) -> None:
        self.groupbox = QGroupBox("Analyzer", self)
        self.layout().addWidget(self.groupbox)

        layout = QVBoxLayout(self.groupbox)

        hlayout = QHBoxLayout()
        model_label = QLabel("Model", self.groupbox)
        hlayout.addWidget(model_label)

        self.model_combobox = QComboBox(self.groupbox)
        hlayout.addWidget(self.model_combobox)

        address_label = QLabel("Address", self.groupbox)
        hlayout.addWidget(address_label)

        self.address_combobox = QComboBox(self.groupbox)
        hlayout.addWidget(self.address_combobox)

        self.connect_btn = QPushButton("Connect", self.groupbox)
        hlayout.addWidget(self.connect_btn)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        pol1_label = QLabel("Polarization 1:", self.groupbox)
        hlayout.addWidget(pol1_label)

        self.pol1_lineedit = QLineEdit(self.groupbox)
        self.pol1_lineedit.setPlaceholderText("Label (e.g. Vertical)")
        hlayout.addWidget(self.pol1_lineedit)

        self.pol1_combobox = QComboBox(self.groupbox)
        hlayout.addWidget(self.pol1_combobox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        pol2_label = QLabel("Polarization 2:", self.groupbox)
        hlayout.addWidget(pol2_label)

        self.pol2_lineedit = QLineEdit(self.groupbox)
        self.pol2_lineedit.setPlaceholderText("Label")
        hlayout.addWidget(self.pol2_lineedit)

        self.pol2_combobox = QComboBox(self.groupbox)
        hlayout.addWidget(self.pol2_combobox)

        layout.addLayout(hlayout)

        self.freq_groupbox = QGroupBox("Frequency", self.groupbox)
        freq_layout = QGridLayout(self.freq_groupbox)

        start_freq_label = QLabel("Start", self.freq_groupbox)
        freq_layout.addWidget(start_freq_label, 0, 0, 1, 1)

        self.start_freq_lineedit = FrequencyLineEdit(self.freq_groupbox)
        freq_layout.addWidget(self.start_freq_lineedit, 0, 1, 1, 1)

        stop_freq_label = QLabel("Stop", self.freq_groupbox)
        freq_layout.addWidget(stop_freq_label, 1, 0, 1, 1)

        self.stop_freq_lineedit = FrequencyLineEdit(self.freq_groupbox)
        freq_layout.addWidget(self.stop_freq_lineedit, 1, 1, 1, 1)

        step_freq_label = QLabel("Step", self.freq_groupbox)
        freq_layout.addWidget(step_freq_label, 2, 0, 1, 1)

        self.freq_step_lineedit = FrequencyLineEdit(self.freq_groupbox)
        freq_layout.addWidget(self.freq_step_lineedit, 2, 1, 1, 1)

        n_points_label = QLabel("Number of Points", self.freq_groupbox)
        freq_layout.addWidget(n_points_label, 3, 0, 1, 1)

        self.n_points_lineedit = QLineEdit(self.freq_groupbox)
        self.n_points_lineedit.setValidator(QIntValidator(self.n_points_lineedit))
        freq_layout.addWidget(self.n_points_lineedit, 3, 1, 1, 1)

        layout.addWidget(self.freq_groupbox)
        self.freq_groupbox.setEnabled(False)

    def _init_inputs(self) -> None:
        log.debug("Populating models...")
        self.model_combobox.clear()
        self.model_combobox.addItems(list(self.model.keys()))

        log.debug("Populating addresses...")
        self.address_combobox.clear()
        # If we can't find the library, default to pyvisa-py
        try:
            addrs = vna.VNA.available(backend=SETTINGS["analyzer/backend"])
        except pyvisa.errors.LibraryError:
            addrs = vna.VNA.available()

        self.address_combobox.addItems(addrs)

        log.debug("Updating inputs from settings...")
        self.model_combobox.setCurrentText(SETTINGS['analyzer/model'])
        self.address_combobox.setCurrentText(SETTINGS['analyzer/addr'])
        self.pol1_lineedit.setText(SETTINGS["analyzer/pol1-label"])
        self.pol1_combobox.setCurrentText(SETTINGS["analyzer/pol1-param"])
        self.pol2_lineedit.setText(SETTINGS["analyzer/pol2-label"])
        self.pol2_combobox.setCurrentText(SETTINGS["analyzer/pol2-param"])

    def _connect_signals(self) -> None:
        log.debug("Connecting signals...")

        self.model_combobox.currentTextChanged.connect(
            lambda val: SETTINGS.setval("analyzer/model", val)
        )
        self.address_combobox.currentTextChanged.connect(
            lambda val: SETTINGS.setval("analyzer/addr", val)
        )
        self.connect_btn.clicked.connect(self._on_connect_clicked)

        self.pol1_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("analzyer/pol1-param", text)
        )
        self.pol2_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("analyzer/pol2-param", text)
        )

        self.start_freq_lineedit.textChanged.connect(self._on_start_freq_changed)
        self.stop_freq_lineedit.textChanged.connect(self._on_stop_freq_changed)
        self.freq_step_lineedit.textChanged.connect(self._on_freq_step_changed)
        self.n_points_lineedit.textChanged.connect(self._on_n_points_changed)

        self.start_freq_lineedit.editingFinished.connect(
            self._on_start_freq_editing_finished
        )
        self.stop_freq_lineedit.editingFinished.connect(
            self._on_stop_freq_editing_finished
        )
        self.freq_step_lineedit.editingFinished.connect(
            self._on_freq_step_editing_finished
        )
        self.n_points_lineedit.editingFinished.connect(self._on_n_points_editing_finished)

        self.analyzer_connected.connect(lambda: self.set_enabled(True))

    def _on_start_freq_changed(self, text: str) -> None:
        if self.start_freq_lineedit.hasAcceptableInput():
            self.start_freq = Quantity(text)
        else:
            self.start_freq = None

    def _on_stop_freq_changed(self, text: str) -> None:
        if self.stop_freq_lineedit.hasAcceptableInput():
            self.stop_freq = Quantity(text)
        else:
            self.stop_freq = None

    def _on_freq_step_changed(self, text: str) -> None:
        if self.freq_step_lineedit.hasAcceptableInput():
            self.freq_step = Quantity(text)
        else:
            self.freq_step = None

    def _on_n_points_changed(self, text: str) -> None:
        if self.n_points_lineedit.hasAcceptableInput():
            self.n_points = int(text)
        else:
            self.n_points = None

    # editingFinished is only emitted if the input is acceptable, so these
    # class variables should never be None, hence the type: ignores
    def _on_start_freq_editing_finished(self) -> None:
        self.set_start_freq(self.start_freq)  # type: ignore

    def _on_stop_freq_editing_finished(self) -> None:
        self.set_stop_freq(self.stop_freq)  # type: ignore

    def _on_freq_step_editing_finished(self) -> None:
        self.set_freq_step(self.freq_step)  # type: ignore

    def _on_n_points_editing_finished(self) -> None:
        self.set_n_points(self.n_points)  # type: ignore

    def _on_connect_clicked(self) -> None:
        model = self.model_combobox.currentText()
        addr = self.address_combobox.currentText()

        self.connect(model, addr)

    # ========== API ==========
    def connect(self, model: str, addr: str) -> None:
        if model == "":
            QMessageBox.warning(self, "Invalid model", "Must specify model")
            return

        if addr == "":
            QMessageBox.warning(self, "Invalid address", "Must specify address")
            return

        log.debug(f"Connecting to analyzer {model} at {addr}")
        try:
            self._analyzer = self.model[model](addr, backend=SETTINGS['backend'])
        except pyvisa.errors.LibraryError:
            self._analyzer = self.model[model](addr)
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connect to analyzer: {e}"
            )
            return

        log.debug("Updating current analyzer frequency settings")
        try:
            self.start_freq_lineedit.setText(str(self._analyzer.start_freq()))
            self.stop_freq_lineedit.setText(str(self._analyzer.stop_freq()))
            self.n_points_lineedit.setText(str(self._analyzer.npoints()))
            self.freq_step_lineedit.setText(str(self._analyzer.freq_step()))
            ports = self._analyzer.ports
        except pyvisa.errors.VisaIOError as e:
            log.error(f"Error communicating with the analyzer: {e}")
            QMessageBox.critical(
                self,
                "Communication Error",
                "Error connecting to analyzer.\nDo you have the right port?",
            )
            self._analyzer = None
            return

        ports = [f"S{''.join(p)}" for p in itertools.permutations(ports, 2)] + [
            f"S{p}{p}" for p in ports
        ]
        self.pol1_combobox.blockSignals(True)
        self.pol2_combobox.blockSignals(True)
        self.pol1_combobox.addItems(ports)
        self.pol1_combobox.setCurrentText(SETTINGS['pol1-param'])
        self.pol2_combobox.addItems(ports)
        self.pol2_combobox.setCurrentText(SETTINGS['pol2-param'])
        self.pol1_combobox.blockSignals(False)
        self.pol2_combobox.blockSignals(False)
        log.info("Connected")
        self.analyzer_connected.emit()

    def analyzer(self) -> vna.VNA:
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected")

        return self._analyzer

    def polarizations(self) -> List[Polarization]:
        pols = []
        pol1_param = self.pol1_combobox.currentText()
        if pol1_param != "":
            pol1_label = self.pol1_lineedit.text()
            if pol1_label == "":
                pol1_label = "Polarization 1"

            pols.append(Polarization(pol1_label, pol1_param))

        pol2_param = self.pol2_combobox.currentText()
        if pol2_param != "":
            pol2_label = self.pol2_lineedit.text()
            if pol2_label == "":
                pol2_label = "Polarization 2"

            pols.append(Polarization(pol2_label, pol2_param))

        return pols

    def frequencies(self) -> np.ndarray:
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        return self._analyzer.frequency().f

    def set_start_freq(self, f: Quantity) -> None:
        log.debug(f"Setting start freq to {f}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.set_start_freq(f.real)

    def set_stop_freq(self, f: Quantity) -> None:
        log.debug(f"Setting stop freq to {f}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.set_stop_freq(f.real)

    def set_freq_step(self, f: Quantity) -> None:
        log.debug(f"Setting freq step to {f}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.set_freq_step(f.real)
        self.n_points_lineedit.setText(str(self._analyzer.npoints()))

    def set_n_points(self, n: int) -> None:
        log.debug(f"Setting n points to {n}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.set_npoints(n)
        self.freq_step_lineedit.setText(str(self._analyzer.freq_step()))

    def set_enabled(self, enable: bool) -> None:
        self.freq_groupbox.setEnabled(enable)

    def get_data(self, measurement_name: str) -> skrf.Network:
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        log.debug(f"Setting active measurement to {measurement_name}")
        self._analyzer.set_active_measurement(measurement_name)
        log.debug("Getting data")
        return self._analyzer.get_active_trace()

    def create_measurement(self, name: str, param: str) -> None:
        log.debug(f"Creating measurement {name}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.create_measurement(name, param)

    def delete_measurement(self, name: str) -> None:
        log.debug(f"Deleting measurement {name}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.delete_measurement(name)
