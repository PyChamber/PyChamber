import skrf
from PyQt5.QtWidgets import (
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

from .mpl_widget import MplRectWidget
from .pychamber_plot import PlotControls, PyChamberPlot


class OverFreqPlot(PyChamberPlot):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def update(self) -> None:
        pass

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

        # send to MplWidget

    def _add_widgets(self) -> None:
        layout = QVBoxLayout(self)

        hlayout = QHBoxLayout()

        pol_label = QLabel("Polarization", self)
        hlayout.addWidget(pol_label)

        self.pol_combobox = QComboBox(self)
        self.pol_combobox.addItems(['1', '2'])
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

        self.autoscale_btn = QPushButton("Auto Scale", self)
        hlayout.addWidget(self.autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.plot = MplRectWidget(self)
        layout.addWidget(self.plot)
