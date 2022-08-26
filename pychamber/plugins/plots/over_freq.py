import numpy as np
import skrf
from matplotlib.ticker import EngFormatter
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)

from pychamber.logger import log
from pychamber.widgets import MplRectWidget, PlotLimits

from .pychamber_plot import PlotControls, PyChamberPlot


class OverFreqPlot(PyChamberPlot):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def init_controls(self, **kwargs) -> None:
        freqs: np.ndarray = kwargs.get('frequencies')
        self.plot.xmin = freqs.min()
        self.plot.xmax = freqs.max()

        azimuths: np.ndarray = kwargs.get('azimuths')
        if len(azimuths) > 1:
            self.az_spinbox.setRange(azimuths.min(), azimuths.max())
            self.az_spinbox.setSingleStep(azimuths[1] - azimuths[0])

        elevations: np.ndarray = kwargs.get('elevations')
        if len(elevations) > 1:
            self.el_spinbox.setRange(elevations.min(), elevations.max())
            self.el_spinbox.setSingleStep(elevations[1] - elevations[0])

    def post_visible_setup(self) -> None:
        self.plot.set_xlabel("Frequency [Hz]")
        self.plot.set_ylabel("Power [dB]")
        self.plot.ax.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        self.plot.xmin = 0
        self.plot.xmax = int(1e9)

    def set_polarization_model(self, model: QStringListModel) -> None:
        self.pol_combobox.setModel(model)

    def reset(self) -> None:
        self.plot.reset_plot()
        self.min_spinbox.setValue(self.plot.ymin)
        self.max_spinbox.setValue(self.plot.ymax)
        self.step_spinbox.setValue(self.plot.ystep)

    def _connect_signals(self) -> None:
        self.pol_combobox.currentTextChanged.connect(self._send_controls_state)
        self.az_spinbox.valueChanged.connect(self._send_controls_state)
        self.el_spinbox.valueChanged.connect(self._send_controls_state)

        self.min_spinbox.valueChanged.connect(self._on_plot_min_changed)
        self.max_spinbox.valueChanged.connect(self._on_plot_max_changed)
        self.step_spinbox.valueChanged.connect(self._on_plot_step_changed)

        self.autoscale_chkbox.stateChanged.connect(self._on_autoscale_toggle_changed)
        self.autoscale_btn.clicked.connect(self.plot.autoscale_plot)
        self.plot.autoscaled.connect(self._on_autoscaled)

    def _send_controls_state(self) -> None:
        log.debug("Controls updated. Sending...")
        pol = self.pol_combobox.currentText()
        az = self.az_spinbox.value()
        el = self.el_spinbox.value()

        ctrl = PlotControls(polarization=pol, azimuth=az, elevation=el)
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

    def _on_autoscale_toggle_changed(self, val: bool) -> None:
        self.plot.autoscale = val

    def _on_autoscaled(self, lims: PlotLimits) -> None:
        self.min_spinbox.blockSignals(True)
        self.max_spinbox.blockSignals(True)
        self.step_spinbox.blockSignals(True)
        self.min_spinbox.setValue(int(lims.min_))
        self.max_spinbox.setValue(int(lims.max_))
        self.step_spinbox.setValue(int(lims.step))
        self.min_spinbox.blockSignals(False)
        self.max_spinbox.blockSignals(False)
        self.step_spinbox.blockSignals(False)

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        log.debug("Got new data. Updating...")
        pol = self.pol_combobox.currentText()
        az = self.az_spinbox.value()
        el = self.el_spinbox.value()

        if (
            ntwk.params['polarization'] != pol
            or ntwk.params['azimuth'] != az
            or ntwk.params['elevation'] != el
        ):
            return

        freq = ntwk.frequency.f
        mags = ntwk.s_db

        log.debug(f"Plotting {freq=}, {mags=}")

        self.plot.update_plot(freq, mags)

    def plot_new_data(self, data: skrf.NetworkSet) -> None:
        assert len(data) <= 1
        data = data[0]  # extract from the set
        freqs = data.frequency.f
        mags = data.s_db
        self.plot.plot_new_data(xdata=freqs, ydata=mags)

    def autoscale(self) -> None:
        self.plot.autoscale_plot()

    def _add_widgets(self) -> None:
        layout = QVBoxLayout(self)

        hlayout = QHBoxLayout()

        pol_label = QLabel("Polarization", self)
        hlayout.addWidget(pol_label)

        self.pol_combobox = QComboBox(self)
        hlayout.addWidget(self.pol_combobox)

        az_label = QLabel("Azimuth", self)
        hlayout.addWidget(az_label)

        self.az_spinbox = QDoubleSpinBox(self)
        hlayout.addWidget(self.az_spinbox)

        el_label = QLabel("Elevation", self)
        hlayout.addWidget(el_label)

        self.el_spinbox = QDoubleSpinBox(self)
        hlayout.addWidget(self.el_spinbox)

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

        self.autoscale_chkbox = QCheckBox(self)
        hlayout.addWidget(self.autoscale_chkbox)

        self.autoscale_btn = QPushButton("Auto Scale", self)
        hlayout.addWidget(self.autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.plot = MplRectWidget(self)
        layout.addWidget(self.plot)
