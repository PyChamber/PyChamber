"""Plugin to interact with a network analyzer.

Internally, this uses scikit-rf's vi module to interact with instruments.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Type, Union
    from pychamber.main_window import MainWindow

import itertools

import numpy as np
import pyvisa
import skrf
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from quantiphy import Quantity
from skrf.vi import vna

from pychamber.logger import LOG
from pychamber.polarization import Polarization
from pychamber.settings import SETTINGS
from pychamber.ui import size_policy, font
from pychamber.widgets import CollapsibleSection, FrequencyLineEdit

from .base import PyChamberPanelPlugin


class AnalyzerPlugin(PyChamberPanelPlugin):
    """A plugin to manage a network analyzer.

    Attributes:
        analyzer_connected: Signal raised when an analyzer has been succesfully connected
    """

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
        "Keysight PNA": vna.keysight.PNA,
    }
    """Mapping of user-friendly model names and their scikit-rf specific classes."""

    # Signals
    analyzer_connected = pyqtSignal()

    def __init__(self, main_window: MainWindow) -> None:
        """Instantiate the plugin.

        Arguments:
            parent: the PyChamber main window
        """
        assert self.NAME is not None
        PyChamberPanelPlugin.__init__(self, main_window=main_window)
        self.section = CollapsibleSection(title=self.NAME.capitalize(), parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.section)
        self.setLayout(layout)

        self.setObjectName(self.NAME)

        self._analyzer: Optional[vna.VNA] = None

        self.start_freq: Optional[Quantity] = None
        self.stop_freq: Optional[Quantity] = None
        self.freq_step: Optional[Quantity] = None
        self.n_points: Optional[int] = None

    def _setup(self) -> None:
        LOG.debug("Creating Analyzer widget...")
        self._add_widgets()

    def _post_visible_setup(self) -> None:
        LOG.debug("Post-visible setup")
        self._init_inputs()
        self._connect_signals()

    def _add_widgets(self) -> None:
        layout = QVBoxLayout()

        hlayout = QHBoxLayout()
        model_label = QLabel("Model", self.section)
        hlayout.addWidget(model_label)

        self.model_combobox = QComboBox(self.section)
        hlayout.addWidget(self.model_combobox)

        address_label = QLabel("Address", self.section)
        hlayout.addWidget(address_label)

        self.address_combobox = QComboBox(self.section)
        hlayout.addWidget(self.address_combobox)

        self.connect_btn = QPushButton("Connect", self.section)
        self.connect_btn.setSizePolicy(size_policy["PREF_PREF"])
        hlayout.addWidget(self.connect_btn)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        pol1_label = QLabel("Polarization 1:", self.section)
        hlayout.addWidget(pol1_label)

        self.pol1_lineedit = QLineEdit(self.section)
        self.pol1_lineedit.setPlaceholderText("Label (e.g. Vertical)")
        hlayout.addWidget(self.pol1_lineedit)

        self.pol1_combobox = QComboBox(self.section)
        hlayout.addWidget(self.pol1_combobox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        pol2_label = QLabel("Polarization 2:", self.section)
        hlayout.addWidget(pol2_label)

        self.pol2_lineedit = QLineEdit(self.section)
        self.pol2_lineedit.setPlaceholderText("Label")
        hlayout.addWidget(self.pol2_lineedit)

        self.pol2_combobox = QComboBox(self.section)
        hlayout.addWidget(self.pol2_combobox)

        layout.addLayout(hlayout)

        self.freq_groupbox = QGroupBox("Frequency", self.section)
        self.freq_groupbox.setFont(font["BOLD_12"])
        freq_layout = QFormLayout(self.freq_groupbox)
        freq_layout.setLabelAlignment(Qt.AlignRight)

        self.start_freq_lineedit = FrequencyLineEdit(self.freq_groupbox)
        self.start_freq_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        freq_layout.addRow("Start", self.start_freq_lineedit)

        self.stop_freq_lineedit = FrequencyLineEdit(self.freq_groupbox)
        freq_layout.addRow("Stop", self.stop_freq_lineedit)

        self.freq_step_lineedit = FrequencyLineEdit(self.freq_groupbox)
        freq_layout.addRow("Step", self.freq_step_lineedit)

        self.n_points_lineedit = QLineEdit(self.freq_groupbox)
        self.n_points_lineedit.setValidator(QIntValidator(self.n_points_lineedit))
        freq_layout.addRow("Number of points", self.n_points_lineedit)

        layout.addWidget(self.freq_groupbox)
        self.freq_groupbox.setEnabled(False)

        self.section.set_content_layout(layout)

    def _init_inputs(self) -> None:
        LOG.debug("Populating models...")
        self.model_combobox.clear()
        self.model_combobox.addItems(list(self.model.keys()))

        LOG.debug("Populating addresses...")
        self.address_combobox.clear()
        # If we can't find the library, default to pyvisa-py
        try:
            LOG.debug(f"Trying to populate addrs from {SETTINGS['analyzer/backend']}")
            addrs = vna.available(backend=SETTINGS["analyzer/backend"])
        except pyvisa.errors.LibraryError:
            LOG.debug("Failed. Reverting to default")
            addrs = vna.available()

        self.address_combobox.addItems(addrs)

        LOG.debug("Updating inputs from settings...")
        self.model_combobox.setCurrentText(SETTINGS['analyzer/model'])
        self.address_combobox.setCurrentText(SETTINGS['analyzer/addr'])

    def _connect_signals(self) -> None:
        LOG.debug("Connecting signals...")

        self.model_combobox.currentTextChanged.connect(
            lambda val: SETTINGS.setval("analyzer/model", val)
        )
        self.address_combobox.currentTextChanged.connect(
            lambda val: SETTINGS.setval("analyzer/addr", val)
        )
        self.connect_btn.clicked.connect(self._on_connect_clicked)

        self.pol1_lineedit.textChanged.connect(
            lambda text: SETTINGS.setval("analyzer/pol1-label", text)
        )
        self.pol1_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("analyzer/pol1-param", text)
        )
        self.pol2_lineedit.textChanged.connect(
            lambda text: SETTINGS.setval("analyzer/pol2-label", text)
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
        self._update_freqs()

    def _on_stop_freq_editing_finished(self) -> None:
        self.set_stop_freq(self.stop_freq)  # type: ignore
        self._update_freqs()

    def _on_freq_step_editing_finished(self) -> None:
        self.set_freq_step(self.freq_step)  # type: ignore
        self._update_freqs()

    def _on_n_points_editing_finished(self) -> None:
        self.set_n_points(self.n_points)  # type: ignore
        self._update_freqs()

    def _on_connect_clicked(self) -> None:
        model = self.model_combobox.currentText()
        addr = self.address_combobox.currentText()

        self.connect(model, addr)

    def _update_freqs(self) -> None:
        assert self._analyzer is not None
        freq = self._analyzer.frequency()

        start = Quantity(freq.start, units='Hz').render()
        self.start_freq_lineedit.setText(start)
        stop = Quantity(freq.stop, units='Hz').render()
        self.stop_freq_lineedit.setText(stop)
        step = Quantity(freq.step, units='Hz').render()
        self.freq_step_lineedit.setText(step)
        npoints = freq.npoints
        self.n_points_lineedit.setText(str(npoints))

    def _user_settings(self) -> List[Tuple[str, str, Type]]:
        def backend_browse(text: str) -> None:
            if text == "Browse...":
                backend_path, _ = QFileDialog.getOpenFileName()
                if backend_path != "":
                    last_idx = backend.count()
                    backend.insertItem(last_idx, backend_path)
                    backend.setCurrentIndex(last_idx)

        backend = QComboBox()
        backend.addItems(["Browse...", "pyvisa-py", "IVI"])

        current_backend = SETTINGS['analyzer/backend']
        if current_backend != "":
            idx = backend.findText(current_backend)
            if idx != -1:
                backend.setCurrentIndex(idx)
            else:
                backend.addItem(current_backend)
                backend.setCurrentIndex(backend.count() - 1)

        backend.textActivated.connect(backend_browse)
        backend.currentTextChanged.connect(
            lambda text: SETTINGS.setval("analyzer/backend", text)
        )

        settings = [("backend", "VISA Backend", backend)]
        return settings

    # ========== API ==========
    def connect(self, model: str, addr: str) -> None:
        """Connect to the analyzer.

        Arguments:
            model: the model name
            addr: the VISA address of the instrument
        """
        # TODO: The QMessageBoxes should be moved out of this to allow this to
        # be called from an interpreter
        if model == "":
            QMessageBox.warning(self, "Invalid model", "Must specify model")
            return

        if addr == "":
            QMessageBox.warning(self, "Invalid address", "Must specify address")
            return

        LOG.debug(f"Connecting to analyzer {model} at {addr}")
        try:
            self._analyzer = self.model[model](addr, backend=SETTINGS['analyzer/backend'])
        except pyvisa.errors.LibraryError:
            self._analyzer = self.model[model](addr)
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connect to analyzer: {e}"
            )
            return

        LOG.debug("Updating current analyzer frequency settings")
        try:
            self.start_freq_lineedit.setText(str(self._analyzer.start_freq()))
            self.stop_freq_lineedit.setText(str(self._analyzer.stop_freq()))
            self.n_points_lineedit.setText(str(self._analyzer.npoints()))
            self.freq_step_lineedit.setText(str(self._analyzer.freq_step()))
            ports = self._analyzer.ports
        except pyvisa.errors.VisaIOError as e:
            LOG.error(f"Error communicating with the analyzer: {e}")
            QMessageBox.critical(
                self,
                "Communication Error",
                "Error connecting to analyzer.\nDo you have the right port?",
            )
            self._analyzer = None
            return

        msmts = itertools.product(ports, repeat=2)
        params = ["OFF"] + [f"S{a}{b}" for a, b in msmts]
        self.pol1_combobox.blockSignals(True)
        self.pol1_lineedit.blockSignals(True)
        self.pol2_combobox.blockSignals(True)
        self.pol2_lineedit.blockSignals(True)
        self.pol1_combobox.addItems(params)
        LOG.debug(f"{params=}")
        LOG.debug(f"setting pol1_combobox to {SETTINGS['analyzer/pol1-param']}")
        self.pol1_combobox.setCurrentText(SETTINGS['analyzer/pol1-param'])
        self.pol1_lineedit.setText(SETTINGS["analyzer/pol1-label"])
        self.pol2_combobox.addItems(params)
        LOG.debug(f"setting pol2_combobox to {SETTINGS['analyzer/pol2-param']}")
        self.pol2_combobox.setCurrentText(SETTINGS['analyzer/pol2-param'])
        self.pol2_lineedit.setText(SETTINGS["analyzer/pol2-label"])
        self.pol1_combobox.blockSignals(False)
        self.pol1_lineedit.blockSignals(False)
        self.pol2_combobox.blockSignals(False)
        self.pol2_lineedit.blockSignals(False)
        LOG.info("Connected")
        self.analyzer_connected.emit()

    def analyzer(self) -> vna.VNA:
        """Get the analyzer instance.

        Returns:
            the analyzer instance

        Raises:
            RuntimeError: if no analyzer is connected
        """
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected")

        return self._analyzer

    @property
    def sparams(self) -> List[str]:
        """The parameters in the dropdowns."""
        return [self.pol1_combobox.itemText(i) for i in range(self.pol1_combobox.count())]

    def is_connected(self) -> bool:
        """Check if an analyzer is connected."""
        return self._analyzer is not None

    def polarizations(self) -> List[Polarization]:
        """Get the polarizations as a list."""
        pols = []
        pol1_param = self.pol1_combobox.currentText()
        if pol1_param != "OFF":
            pol1_label = self.pol1_lineedit.text()
            if pol1_label == "":
                pol1_label = "Polarization 1"

            pols.append(Polarization(pol1_label, pol1_param))

        pol2_param = self.pol2_combobox.currentText()
        if pol2_param != "OFF":
            pol2_label = self.pol2_lineedit.text()
            if pol2_label == "":
                pol2_label = "Polarization 2"

            pols.append(Polarization(pol2_label, pol2_param))

        return pols

    def pol_name(self, pol: int) -> str:
        """Get the name (label) of a polarization.

        Arguments:
            pol: which polarizatoin (1, 2)
        """
        if pol == 1:
            return self.pol1_lineedit.text()
        elif pol == 2:
            return self.pol2_lineedit.text()
        else:
            raise ValueError("There are only two polarizations. Pass 1 or 2.")

    def frequencies(self) -> np.ndarray:
        """Get the array of frequencies of the current setitings of the analyzer."""
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        return self._analyzer.frequency().f

    def set_start_freq(self, f: Union[float, Quantity]) -> None:
        """Set the analyzer start frequency.

        Arguments:
            f: the start frequency

        Raises:
            RuntimeError: if no analyzer is connected
        """
        LOG.debug(f"Setting start freq to {f}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        if isinstance(f, Quantity):
            f = f.real

        self._analyzer.set_start_freq(f)

    def set_stop_freq(self, f: Union[float, Quantity]) -> None:
        """Set the analyzer stop frequency.

        Arguments:
            f: the start frequency

        Raises:
            RuntimeError: if no analyzer is connected
        """
        LOG.debug(f"Setting stop freq to {f}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        if isinstance(f, Quantity):
            f = f.real

        self._analyzer.set_stop_freq(f)

    def set_freq_step(self, f: Union[float, Quantity]) -> None:
        """Set the frequency step.

        Arguments:
            f: the frequency step

        Raises:
            RuntimeError: if no analyzer is connected
        """
        LOG.debug(f"Setting freq step to {f}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        if isinstance(f, Quantity):
            f = f.real

        self._analyzer.set_freq_step(f.real)
        # TODO: Move GUI code out of the API
        self.n_points_lineedit.setText(str(self._analyzer.npoints()))

    def set_n_points(self, n: int) -> None:
        """Set the number of frequency points.

        Arguments:
            n: the number of points

        Raises:
            RuntimeError: if no analyzer is connected
        """
        LOG.debug(f"Setting n points to {n}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.set_npoints(n)
        # TODO: Move GUI code out of the API
        self.freq_step_lineedit.setText(str(self._analyzer.freq_step()))

    def set_enabled(self, enable: bool) -> None:
        """Enable/Disable the plugin.

        Arguments:
            enable: True to enable, False to disable
        """
        self.freq_groupbox.setEnabled(enable)

    def get_data(self, measurement_name: str) -> skrf.Network:
        """Get the data from an existing measurement.

        Arguments:
            measurement_name: name of the measurement to grab data from

        Raises:
            RuntimeError: if no analyzer is connected
        """
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        return self._analyzer.get_measurement(measurement_name)

    def create_measurement(self, name: str, param: str) -> None:
        """Create a new measurement.

        Arguments:
            name: the name of the new measurement
            param: the measurement parameter (e.g. S21)

        Raises:
            RuntimeError: if no analyzer is connected
        """
        LOG.debug(f"Creating measurement {name}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.create_measurement(name, param)

    def delete_measurement(self, name: str) -> None:
        """Delete a measurement.

        Arguments:
            name: the name of the measurement to delete

        Raises:
            RuntimeError: if no analyzer is connected
        """
        LOG.debug(f"Deleting measurement {name}")
        if self._analyzer is None:
            raise RuntimeError("Analyzer not connected.")

        self._analyzer.delete_measurement(name)
