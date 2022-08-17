from matplotlib.ticker import FuncFormatter
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

from ..freq_spin_box import FrequencySpinBox
from .mpl_widget import MplRectWidget
from .pychamber_plot import PlotControls, PyChamberPlot


class RectangularPlot(PyChamberPlot):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def init_from_experiment(self, **kwargs) -> None:
        azimuths = np.deg2rad(kwargs.get('azimuths', np.arange(-180, 180, 1)))
        freqs = kwargs.get('frequencies')
        self.freq_spinbox.setRange(freqs.min(), freqs.max())
        self.freq_spinbox.setSingleStep(freqs[1] - freqs[0])
        log.debug(f"Setting xlimits to {azimuths}")
        self.plot.xmin = azimuths.min()
        self.plot.xmax = azimuths.max()

    def set_polarization_model(self, model: QStringListModel) -> None:
        self.pol_combobox.setModel(model)

    def reset(self) -> None:
        self.plot.reset_plot()
        self.min_spinbox.setValue(self.plot.ymin)
        self.max_spinbox.setValue(self.plot.ymax)
        self.step_spinbox.setValue(self.plot.ystep)

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

        self.plot.ymin = val

    def _on_plot_max_changed(self, val: int) -> None:
        if val <= self.min_spinbox.value():
            return

        self.plot.ymax = val

    def _on_plot_step_changed(self, val: int) -> None:
        self.plot.ystep = val

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        log.debug("Got new data. Updating...")
        pol = self.pol_combobox.currentText()
        freq = self.freq_spinbox.text()
        if ntwk.params['polarization'] != pol:
            return

        theta = np.deg2rad(float(ntwk.params['azimuth']))
        mag = ntwk[freq].s_db  # type: ignore

        self.plot.update_plot(theta, mag)

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

        self.plot = MplRectWidget(self)
        self.plot.ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos: f"{np.rad2deg(x):.0f}")
        )
        layout.addWidget(self.plot)
