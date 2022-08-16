import skrf
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

from .mpl_widget import MplRectWidget
from .pychamber_plot import PlotControls, PyChamberPlot


class RectangularPlot(PyChamberPlot):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def update(self) -> None:
        pass

    def _connect_signals(self) -> None:
        self.pol_combobox.currentTextChanged.connect(self._send_controls_state)
        self.freq_lineedit.editingFinished.connect(self._send_controls_state)

    def _send_controls_state(self) -> None:
        log.debug("Controls updated. Sending...")
        pol = self.pol_combobox.currentText()
        freq = self.freq_lineedit.text()

        ctrl = PlotControls(polarization=pol, frequency=freq, elevation=0.0)
        self.controls_changed.emit(ctrl)

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        log.debug("Got new data. Updating...")
        pol = self.pol_combobox.currentText()
        # freq = self.freq_lineedit.text()
        if ntwk.params['polarization'] != pol:
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

        freq_label = QLabel("Frequency", self)
        hlayout.addWidget(freq_label)

        self.freq_lineedit = FrequencyLineEdit(self)
        self.freq_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.freq_lineedit.setMinimumWidth(100)
        hlayout.addWidget(self.freq_lineedit)

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
        self.step_spinbox.setSingleStep(10)
        hlayout.addWidget(self.step_spinbox)

        self.autoscale_btn = QPushButton("Auto Scale", self)
        hlayout.addWidget(self.autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.plot = MplRectWidget('tab:blue', self)
        layout.addWidget(self.plot)
