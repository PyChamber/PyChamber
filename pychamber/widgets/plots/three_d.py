import skrf
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

from pychamber.logger import log
from pychamber.ui import size_policy
from pychamber.widgets import FrequencyLineEdit

from .mpl_widget import Mpl3DWidget
from .pychamber_plot import PlotControls, PyChamberPlot


class ThreeDPlot(PyChamberPlot):
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

        ctrl = PlotControls(polarization=pol, frequency=freq)
        self.controls_changed.emit(ctrl)

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        pass
        # log.debug("Got new data. Updating...")
        # pol = self.pol_combobox.currentText()
        # freq = self.freq_lineedit.text()
        # if ntwk.params['polarization'] != pol:
        #     return

        # send to MplWidget

    def _add_widgets(self) -> None:
        layout = QVBoxLayout(self)

        hlayout = QHBoxLayout()
        self.pol_label = QLabel("Polarization", self)
        hlayout.addWidget(self.pol_label)

        self.pol_combobox = QComboBox(self)
        self.pol_combobox.addItems(['1', '2'])
        hlayout.addWidget(self.pol_combobox)

        self.freq_label = QLabel("Frequency", self)
        hlayout.addWidget(self.freq_label)

        self.freq_lineedit = FrequencyLineEdit(self)
        self.freq_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.freq_lineedit.setMinimumWidth(100)
        hlayout.addWidget(self.freq_lineedit)

        self.refresh_btn = QPushButton("Refresh Plot", self)
        hlayout.addWidget(self.refresh_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.plot = Mpl3DWidget(self)
        layout.addWidget(self.plot)
