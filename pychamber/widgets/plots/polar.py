import numpy as np
import skrf
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)

from pychamber.logger import log
from pychamber.ui import size_policy
from pychamber.widgets import FrequencyLineEdit

from ..freq_spin_box import FrequencySpinBox
from .mpl_widget import MplPolarWidget
from .pychamber_plot import PlotControls, PyChamberPlot


class PolarPlot(PyChamberPlot):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def init_from_experiment(self, **kwargs) -> None:
        freqs = kwargs.get('frequencies')
        self.freq_spinbox.setRange(freqs.min(), freqs.max())
        self.freq_spinbox.setSingleStep(freqs[1] - freqs[0])

    def set_polarization_model(self, model: QStringListModel) -> None:
        self.pol_combobox.setModel(model)

    def reset(self) -> None:
        self.plot.reset_plot()
        self.min_spinbox.setValue(self.plot.rmin)
        self.max_spinbox.setValue(self.plot.rmax)
        self.step_spinbox.setValue(self.plot.rstep)

    def _connect_signals(self) -> None:
        self.pol_combobox.currentTextChanged.connect(self._send_controls_state)
        self.freq_spinbox.editingFinished.connect(self._send_controls_state)

        self.min_spinbox.valueChanged.connect(self._on_plot_min_changed)
        self.max_spinbox.valueChanged.connect(self._on_plot_max_changed)
        self.step_spinbox.valueChanged.connect(self._on_plot_step_changed)

    def _send_controls_state(self) -> None:
        log.debug("Controls updated. Sending...")
        pol = self.pol_combobox.currentText()
        freq = self.freq_spinbox.text()

        ctrl = PlotControls(polarization=pol, frequency=freq, elevation=0.0)
        self.new_data_requested.emit(ctrl)

    def _on_plot_min_changed(self, val: int) -> None:
        if val >= self.max_spinbox.value():
            return

        self.plot.rmin = val

    def _on_plot_max_changed(self, val: int) -> None:
        if val <= self.min_spinbox.value():
            return

        self.plot.rmax = val

    def _on_plot_step_changed(self, val: int) -> None:
        self.plot.rstep = val

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        log.debug("Got new data. Updating...")
        pol = self.pol_combobox.currentText()
        freq = self.freq_spinbox.text()
        if ntwk.params['polarization'] != pol:
            return

        theta = np.deg2rad(float(ntwk.params['azimuth']))
        r = ntwk[freq].s_db  # type: ignore

        log.debug(f"Updating polar plot with {theta=} {r=}")
        self.plot.update_plot(theta, r)

    def _add_widgets(self) -> None:
        layout = QVBoxLayout(self)

        hlayout = QHBoxLayout()

        pol_label = QLabel("Polarization", self)
        hlayout.addWidget(pol_label)

        self.pol_combobox = QComboBox(self)
        hlayout.addWidget(self.pol_combobox)

        freq_label = QLabel("Frequency", self)
        hlayout.addWidget(freq_label)

        self.freq_spinbox = FrequencySpinBox(self)
        self.freq_spinbox.setSizePolicy(size_policy["PREF_PREF"])
        self.freq_spinbox.setMinimumWidth(100)
        hlayout.addWidget(self.freq_spinbox)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        min_label = QLabel("Min", self)
        hlayout.addWidget(min_label)

        self.min_spinbox = QSpinBox(self)
        self.min_spinbox.setRange(-100, 100)
        self.min_spinbox.setSingleStep(5)
        hlayout.addWidget(self.min_spinbox)

        max_label = QLabel("Max", self)
        hlayout.addWidget(max_label)

        self.max_spinbox = QSpinBox(self)
        self.max_spinbox.setRange(-100, 100)
        self.max_spinbox.setSingleStep(5)
        hlayout.addWidget(self.max_spinbox)

        step_label = QLabel("dB/div", self)
        hlayout.addWidget(step_label)

        self.step_spinbox = QSpinBox(self)
        self.step_spinbox.setRange(1, 100)
        self.step_spinbox.setSingleStep(5)
        hlayout.addWidget(self.step_spinbox)

        self.autoscale_btn = QPushButton("Auto Scale", self)
        hlayout.addWidget(self.autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.plot = MplPolarWidget(self)
        layout.addWidget(self.plot)
