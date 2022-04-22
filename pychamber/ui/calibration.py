import itertools
import logging
from typing import List, Optional

import cloudpickle as pickle
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)
from skrf import network
from skrf.vi import vna

from pychamber.ui.mplwidget import MplRectWidget
from pychamber.ui.pop_ups import MsgLevel, PopUpMessage

_FONTS = {'header': QFont('Roboto', 12, QFont.Bold)}

log = logging.getLogger(__name__)


class IntroPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.intro_text = QLabel(self)
        self.intro_text.setWordWrap(True)
        self.layout().addWidget(self.intro_text)

    def initializePage(self) -> None:
        self.setTitle("Introduction")
        self.intro_text.setText(
            """
            <html>
            <p>This wizard will walk you through the procedure for
            generating a calibration file to offset losses. This
            is only one way to do a chamber calibration, but it
            is the only one supported at this time.</p>
            </html>
            """
        )


class SetupPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.text = QLabel(self)
        self.text.setWordWrap(True)
        self.layout().addWidget(self.text)

    def initializePage(self) -> None:
        self.setTitle("Setup")
        self.text.setText(
            """
            <html>
            <p>First, set up your instrument with the proper configuration
            (e.g. frequencies, power level, IF bandwidth, etc.).

            Next, set up your horns so they are facing each other 
            and as aligned as possible (a laser is helpful). The 
            more precise this alignment, the better your calibration.</p>
            </html>
            """
        )


class NotesPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.text = QLabel(self)
        self.text.setWordWrap(True)
        self.layout().addWidget(self.text)

        self.layout().addItem(QSpacerItem(1, 10))

        self.notesTextEdit = QPlainTextEdit(self)
        self.registerField("notes", self.notesTextEdit)
        self.layout().addWidget(self.notesTextEdit)

    def initializePage(self) -> None:
        self.setTitle("Notes")
        self.notesTextEdit.setPlaceholderText("Notes...")
        self.text.setText(
            """
            <html>
            <p>Here, you can record some notes detailing the setup. 
            These are optional, but it is highly recommended to take
            detailed notes on the setup. These notes will be stored 
            in the calibration file. Good things to include:<p>

            <ul>
            <li>Cables used</li>
            <li>Connectors used</li>
            <li>What ports were used for what</li>
            <li>Other equipment present (e.g. amplifiers)</li>
            <li>Links to any relevant datasheets</li>
            </ul>

            <p><b>Note:</b> Frequency information is already stored as a 
            part of the calibration data. No need to record it.</p>
            </html>
            """
        )
        self.text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.notesTextEdit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)


class CalibrationPage(QWizardPage):
    ref_data: Optional[network.Network] = None
    cal_data_pol1: Optional[network.Network] = None
    cal_data_pol2: Optional[network.Network] = None

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Reference gain file:"))
        self.refHornFNameLabel = QLabel("", self)
        self.refHornBrowseButton = QPushButton("Browse", self)
        hlayout.addWidget(self.refHornFNameLabel)
        hlayout.addWidget(self.refHornBrowseButton)
        self.layout().addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.pol1Label = QLabel("Polarization 1:", self)
        self.pol1LineEdit = QLineEdit(self)
        self.pol1ComboBox = QComboBox(self)
        hlayout.addWidget(self.pol1Label)
        hlayout.addWidget(self.pol1LineEdit)
        hlayout.addWidget(self.pol1ComboBox)
        self.layout().addLayout(hlayout)
        hlayout = QHBoxLayout()
        self.pol2Label = QLabel("Polarization 2:", self)
        self.pol2LineEdit = QLineEdit(self)
        self.pol2ComboBox = QComboBox(self)
        hlayout.addWidget(self.pol2Label)
        hlayout.addWidget(self.pol2LineEdit)
        hlayout.addWidget(self.pol2ComboBox)
        self.layout().addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.plot = MplRectWidget('tab:blue', self)
        hlayout.addWidget(self.plot)
        self.layout().addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.measureButton = QPushButton("Measure", self)
        self.saveButton = QPushButton("Save", self)
        hlayout.addWidget(self.measureButton)
        hlayout.addWidget(self.saveButton)
        self.layout().addLayout(hlayout)

    @property
    def pol_1(self) -> Optional[List[int]]:
        pol = self.pol1ComboBox.currentText()
        return [int(pol[1]), int(pol[2])] if pol != "" else None

    @property
    def pol_2(self) -> Optional[List[int]]:
        pol = self.pol2ComboBox.currentText()
        return [int(pol[1]), int(pol[2])] if pol != "" else None

    def initializePage(self) -> None:
        self.setTitle("Calibration")
        self.refHornBrowseButton.pressed.connect(self.load_ref_file)
        self.measureButton.pressed.connect(self.capture_data)

        self.pol1LineEdit.setPlaceholderText("Label (e.g. Vertical)")
        self.pol2LineEdit.setPlaceholderText("Label")

        self.plot.set_xtitle('Frequency')
        self.plot.set_ytitle('Loss [dB]')
        self.plot.refresh_plot()

        if self.wizard().analyzer:
            ports = self.wizard().analyzer.ports
            ports = [f"S{''.join(p)}" for p in itertools.permutations(ports, 2)]
            self.pol1ComboBox.clear()
            self.pol2ComboBox.clear()
            self.pol1ComboBox.addItems([""] + ports)
            self.pol2ComboBox.addItems([""] + ports)

        self.saveButton.setEnabled(False)

    def load_ref_file(self) -> None:
        # TODO: Accept numpy / csv / ...others?
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            self.ref_data = network.Network(file_name)
            self.refHornFNameLabel.setText(file_name)

    def capture_data(self) -> None:
        if self.wizard().analyzer is None:
            PopUpMessage("Not connected to analyzer", MsgLevel.ERROR)
            return
        if self.pol_1 is not None:
            self.cal_data_pol1 = self.wizard().analyzer.get_snp_network(self.pol_1)
            if self.ref_data is not None:
                if len(self.cal_data_pol1) != len(self.ref_data):
                    self.ref_data = self.ref_data.interpolate(self.ntwk.frequency)  # type: ignore
                self.cal_data_pol1 = self.cal_data_pol1 - self.ref_data

            freq = self.cal_data_pol1.frequency.f.reshape(-1, 1)
            indx = [x - 1 for x in self.pol_1]
            mags = self.cal_data_pol1.s[:, indx[0], indx[1]].reshape(-1, 1)
            self.plot.update_plot(freq, mags)

        if self.pol_2 is not None:
            self.cal_data_pol2 = self.wizard().analyzer.get_snp_network(self.pol_2)
            if self.ref_data is not None:
                if len(self.cal_data_pol2) != len(self.ref_data):
                    self.ref_data = self.ref_data.interpolate(self.ntwk.frequency)  # type: ignore
                self.cal_data_pol2 = self.cal_data_pol2 - self.ref_data

            if self.pol_1 is None:
                freq = self.cal_data_pol2.frequency.f.reshape(-1, 1)
                indx = [x - 1 for x in self.pol_2]
                mags = self.cal_data_pol2.s[:, indx[0], indx[1]].reshape(-1, 1)
                self.plot.update_plot(freq, mags)

        if self.cal_data_pol1 is not None or self.cal_data_pol2 is not None:
            self.saveButton.setEnabled(True)

    def save_data(self) -> None:
        if not self.cal_data:
            return
        file_name, _ = QFileDialog.getSaveFileName()
        if file_name != "":
            to_save = {'Notes': self.field("notes"), 'Data': {}}
            if self.cal_data_pol1 is not None:
                pol1_name = self.pol1LineEdit.text()
                if pol1_name == "":
                    pol1_name = "Polarization 1"
                to_save['Data'][pol1_name] = self.cal_data_pol1
            if self.cal_data_pol2 is not None:
                pol2_name = self.pol2LineEdit.text()
                if pol2_name == "":
                    pol2_name = "Polarization 2"
                to_save['Data'][pol2_name] = self.cal_data_pol2
            with open(file_name, 'wb') as f:
                pickle.dump(to_save, f)


class CalibrationDialog(QWizard):
    def __init__(self, analyzer: Optional[vna.VNA], parent=None) -> None:
        super().__init__(parent)

        self.analyzer = analyzer
        self.setWindowTitle("Calibration Wizard")
        self.setOption(QWizard.NoBackButtonOnStartPage)
        self.addPage(IntroPage(self))
        self.addPage(SetupPage(self))
        self.addPage(NotesPage(self))
        self.addPage(CalibrationPage(self))

        self.currentIdChanged.connect(self.adjustSize)


class CalibrationViewDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Calibration")
        self.setLayout(QVBoxLayout())

        self.setup()

    def setup(self) -> None:
        self.tabs = QTabWidget(self)
        self.plot_tab = QWidget(self.tabs)
        self.plot_tab.setLayout(QVBoxLayout())
        self.table_tab = QWidget(self.tabs)
        self.table_tab.setLayout(QVBoxLayout())
        self.tabs.addTab(self.plot_tab, "Plot")
        self.tabs.addTab(self.table_tab, "Table")
        self.layout().addWidget(self.tabs)

        self.plot = MplRectWidget('tab:blue', self)
        self.plot_tab.layout().addWidget(self.plot)
        self.table = QTableWidget(self)
        self.table_tab.layout().addWidget(self.table)

        self.init_plot()

    def init_plot(self) -> None:
        self.plot.set_xtitle('Frequency')
        self.plot.set_ytitle('Loss [dB]')
        self.plot.canvas.draw()

    def init_table(self) -> None:
        pass
