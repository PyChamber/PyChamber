from __future__ import annotations
from cgitb import text

from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    import os
    from typing import Optional
    from pychamber.main_window import MainWindow


import cloudpickle as pickle
from matplotlib.ticker import EngFormatter
import pandas as pd
import skrf
from PyQt5.QtCore import pyqtSignal, QSize, QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QTableView,
    QMessageBox,
    QFileDialog,
    QHBoxLayout,
    QPlainTextEdit,
    QWizard,
    QWizardPage,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)

from pychamber.logger import log
from pychamber.plugins import PyChamberPanelPlugin, AnalyzerPlugin
from pychamber.widgets import MplRectWidget


class CalibrationPlugin(PyChamberPanelPlugin):
    NAME = "calibration"

    cal_file_loaded = pyqtSignal()

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)

        self.setObjectName('calibration')
        self.setLayout(QVBoxLayout())

        self.analyzer: Optional[AnalyzerPlugin] = None
        self.cal_file = None

    def _setup(self) -> None:
        self._add_widgets()
        self._connect_signals()

        self.analyzer = cast(AnalyzerPlugin, self.main.get_plugin("analyzer"))

    def _connect_signals(self) -> None:
        self.cal_btn.clicked.connect(self._on_cal_btn_clicked)
        self.cal_file_browse_btn.clicked.connect(self._on_cal_file_browse_btn_clicked)
        self.cal_view_btn.clicked.connect(self._on_cal_view_btn_clicked)
        self.cal_file_loaded.connect(lambda: self.cal_view_btn.setEnabled(True))

    def _on_cal_btn_clicked(self) -> None:
        if not self.analyzer.is_connected():
            QMessageBox.critical(
                self,
                "Analyzer not connected",
                "You must connect to an analyzer before performing calibration",
            )
            return

        wizard = CalibrationWizard(self)
        wizard.cal_saved.connect(lambda fname: self.cal_file_lineedit.setText(fname))
        wizard.cal_saved.connect(lambda: setattr(self, "cal_file", wizard.cal))
        wizard.cal_saved.connect(self.cal_file_loaded.emit)
        wizard.show()

    def _on_cal_view_btn_clicked(self) -> None:
        log.debug("Starting calibration view")
        self.view = CalViewWindow(self.cal_file)
        self.view.show()

    def _on_cal_file_browse_btn_clicked(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            try:
                self.load_cal_file(file_name)
            except Exception as e:
                log.error(f"{e=}")
                QMessageBox.critical(
                    self,
                    "Invalid Calibration File",
                    ("The specified file is not a valid calibration file."),
                )
                return

        self.cal_file_loaded.emit()

    def load_cal_file(self, fname: str) -> None:
        with open(fname, "rb") as ff:
            self.cal_file = pickle.load(ff)

        self.cal_file_lineedit.setText(fname)

    def _add_widgets(self) -> None:
        log.debug("Creating Calibration widget...")
        self.groupbox = QGroupBox("Calibration", self)
        self.layout().addWidget(self.groupbox)

        layout = QVBoxLayout(self.groupbox)

        hlayout = QHBoxLayout()
        cal_file_label = QLabel("Cal file:", self.groupbox)
        hlayout.addWidget(cal_file_label)

        self.cal_file_lineedit = QLineEdit(self.groupbox)
        self.cal_file_lineedit.setReadOnly(True)
        hlayout.addWidget(self.cal_file_lineedit)

        self.cal_file_browse_btn = QPushButton("Browse", self.groupbox)
        hlayout.addWidget(self.cal_file_browse_btn)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.cal_btn = QPushButton("Calibration Wizard", self.groupbox)
        hlayout.addWidget(self.cal_btn)

        self.cal_view_btn = QPushButton("View Calibration", self.groupbox)
        self.cal_view_btn.setEnabled(False)
        hlayout.addWidget(self.cal_view_btn)

        layout.addLayout(hlayout)


class CalibrationWizard(QWizard):
    cal_saved = pyqtSignal(str)

    def __init__(self, parent: CalibrationPlugin) -> None:
        super().__init__(parent)

        self.ref_ntwk: Optional[skrf.Network] = None
        self.pol1_ntwk: Optional[skrf.Network] = None
        self.pol2_ntwk: Optional[skrf.Network] = None
        self.loss1_ntwk: Optional[skrf.Network] = None
        self.loss2_ntwk: Optional[skrf.Network] = None
        self.cal_notes: str = ""
        self.cal = None

        self.setWindowTitle("Calibration Wizard")
        log.debug("Adding intro page")
        self.addPage(IntroPage(self))
        log.debug("Adding setup page")
        self.addPage(SetupPage(self))
        log.debug("Adding notes page")
        self.addPage(NotesPage(self))
        log.debug("Adding ref antenna page")
        self.addPage(ReferenceAntennaPage(self))
        log.debug("Adding calibration page")
        self.addPage(CalibrationPage(parent.analyzer, parent=self))

    def sizeHint(self) -> QSize:
        return QSize(800, 800)


class IntroPage(QWizardPage):
    def __init__(self, parent: None) -> None:
        super().__init__(parent)

        self.setTitle("Introduction")
        label = QLabel(
            "This wizard will walk you through the procedure for"
            " generating a calibration file to offset losses. This"
            " is only one way to do a chamber calibration, but it"
            " is the only one supported at this time.\n\n"
            "This type of calibration works by measuring the response of an antenna"
            " with known characteristics and measuring the difference"
            " between the manufacturer specified gain and what is actually"
            " received. That difference is a determination of the loss in the"
            " system over frequency."
        )
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addStretch()
        self.setLayout(layout)


class SetupPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setTitle("Setup")
        label = QLabel(
            "First, set up your instrument with the proper configuration"
            " (e.g. frequencies, power level, IF bandwidth, etc.)."
            " Next, align your antennas as accurately as possible so they"
            " are pointing at each other perfectly. A laser is helpful here."
            " The more accurate your setup, the better your calibration"
        )
        label.setWordWrap(True)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class NotesPage(QWizardPage):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setTitle("Notes")

        layout = QVBoxLayout()

        label = QLabel(
            "Here, you can record some notes detailing the setup."
            " These are optional, but it is highly recommended to take"
            " detailed notes on the setup. These notes will be stored"
            " in the calibration file. Good things to include:"
            "<ul>"
            "<li>Cables used</li>"
            "<li>Connectors used</li>"
            "<li>What ports were used for what</li>"
            "<li>Other equipment present (e.g. amplifiers)</li>"
            "<li>Links to any relevant datasheets</li>"
            "</ul>"
        )
        label.setWordWrap(True)

        layout.addWidget(label)
        layout.addSpacing(10)

        notes_text_edit = QPlainTextEdit(self)
        notes_text_edit.setPlaceholderText("Notes...")
        notes_text_edit.textChanged.connect(
            lambda: setattr(self.wizard(), "cal_notes", notes_text_edit.toPlainText())
        )

        layout.addWidget(notes_text_edit)
        self.setLayout(layout)


class ReferenceAntennaPage(QWizardPage):
    ref_ntwk_loaded = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setTitle("Reference Antenna")

        layout = QVBoxLayout()

        label = QLabel(
            "First, load the file containing the gain information"
            " of the reference antenna. This must be a csv file of"
            " form:\n\n"
            "frequency [GHz],magnitude [dB]\n"
            "frequency [GHz],magnitude [dB]\n"
            "...\n"
            "frequency [GHz],magnitude [dB]"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addSpacing(10)

        hlayout = QHBoxLayout()

        ref_ant_label = QLabel("Reference Antenna Gain File")
        hlayout.addWidget(ref_ant_label)

        self.ref_ant_file_label = QLabel()
        hlayout.addWidget(self.ref_ant_file_label)

        self.ref_ant_browse_btn = QPushButton("Browse")
        hlayout.addWidget(self.ref_ant_browse_btn)

        layout.addLayout(hlayout)

        self.ref_plot = MplRectWidget(self)
        self.ref_plot.set_xlabel("Frequency [Hz]")
        self.ref_plot.set_ylabel("Magnitude [dB]")
        self.ref_plot.ax.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        layout.addWidget(self.ref_plot)

        self.setLayout(layout)

        self._connect_signals()

    def isComplete(self) -> bool:
        return self.wizard().ref_ntwk is not None

    def _connect_signals(self) -> None:
        self.ref_ant_browse_btn.clicked.connect(self._on_ref_ant_browse_btn_clicked)
        self.ref_ntwk_loaded.connect(self._on_ref_ntwk_loaded)

    def _on_ref_ant_browse_btn_clicked(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            try:
                self.load_file(file_name)
            except Exception as e:
                log.error(f"{e=}")
                QMessageBox.critical(
                    self,
                    "Invalid Reference File",
                    (
                        "The specified file is not a valid reference antenna file."
                        " The file must be a csv file of the form\n\n"
                        "frequency [GHz],magnitude [dB]\n"
                        "frequency [GHz],magnitude [dB]\n"
                        "...\n"
                        "frequency [GHz],magnitude [dB]"
                    ),
                )
                return

        self.ref_ant_file_label.setText(file_name)

    def _on_ref_ntwk_loaded(self) -> None:
        freqs = self.wizard().ref_ntwk.frequency.f
        mags = self.wizard().ref_ntwk.s_db

        self.ref_plot.xmin = freqs.min()
        self.ref_plot.xmax = freqs.max()
        self.ref_plot.ystep = round((mags.max() - mags.min()) / 5, 1)
        self.ref_plot.plot_new_data(freqs, mags)
        self.ref_plot.autoscale_plot()

        self.completeChanged.emit()

    def load_file(self, path: os.PathLike) -> None:
        log.debug(f"Loading {path}")
        with open(path, 'r') as csvfile:
            data = pd.read_csv(csvfile, header=None)
        freqs = data.iloc[:, 0].to_numpy()
        freqs = freqs * 1e9
        mags = data.iloc[:, 1].to_numpy()
        # scikit-rf assumes values are linear, so we convert from to dB
        mags = 10 ** (mags / 20)

        f = skrf.Frequency.from_f(freqs, unit='hz')
        self.wizard().ref_ntwk = skrf.Network(frequency=f, s=mags.reshape(-1, 1, 1))
        self.ref_ntwk_loaded.emit()


class CalibrationPage(QWizardPage):
    def __init__(self, analyzer: AnalyzerPlugin, parent=None) -> None:
        super().__init__(parent)

        self.analyzer = analyzer
        self.setTitle("Calibration")
        self._setup()

    def _setup(self) -> None:
        self._add_widgets()
        self._connect_signals()

    def _add_widgets(self) -> None:
        layout = QVBoxLayout()

        label = QLabel(
            "Now we'll capture the data and combine it with"
            " the information from the reference gain file"
            " to determine the loss of the system."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addSpacing(10)

        hlayout = QHBoxLayout()

        pol1_label = QLabel("Polarization 1:", self)
        hlayout.addWidget(pol1_label)

        self.pol1_lineedit = QLineEdit(self)
        self.pol1_lineedit.setPlaceholderText("Label (e.g. Vertical)")
        hlayout.addWidget(self.pol1_lineedit)

        self.pol1_combobox = QComboBox(self)
        hlayout.addWidget(self.pol1_combobox)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()

        pol2_label = QLabel("Polarization 2:", self)
        hlayout.addWidget(pol2_label)

        self.pol2_lineedit = QLineEdit(self)
        self.pol2_lineedit.setPlaceholderText("Label")
        hlayout.addWidget(self.pol2_lineedit)

        self.pol2_combobox = QComboBox(self)
        hlayout.addWidget(self.pol2_combobox)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()

        self.plot = MplRectWidget(self)
        self.plot.set_title("Loss Over Frequency")
        self.plot.set_xlabel("Frequency [Hz]")
        self.plot.set_ylabel("Magnitude [dB]")
        self.plot.ax.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        hlayout.addWidget(self.plot)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()

        self.measure_btn = QPushButton("Measure", self)
        hlayout.addWidget(self.measure_btn)

        self.save_btn = QPushButton("Save", self)
        hlayout.addWidget(self.save_btn)

        layout.addLayout(hlayout)
        self.setLayout(layout)

        self.pol1_combobox.addItems(self.analyzer.sparams)
        self.pol2_combobox.addItems(self.analyzer.sparams)

    def _connect_signals(self) -> None:
        self.measure_btn.clicked.connect(self._on_measure_btn_clicked)
        self.save_btn.clicked.connect(self._on_save_btn_clicked)

    def _on_measure_btn_clicked(self) -> None:
        msmnt1_param = self.pol1_combobox.currentText()
        msmnt1_name = f"CAL_{msmnt1_param}"
        msmnt2_param = self.pol2_combobox.currentText()
        msmnt2_name = f"CAL_{msmnt2_param}"

        self.analyzer.create_measurement(msmnt1_name, msmnt1_param)
        self.analyzer.create_measurement(msmnt2_name, msmnt2_param)

        params = {"polarization": self.pol1_lineedit.text()}
        ntwk = self.analyzer.get_data(msmnt1_name)
        ntwk.params = params
        self.wizard().pol1_ntwk = ntwk

        params = {"polarization": self.pol2_lineedit.text()}
        ntwk = self.analyzer.get_data(msmnt2_name)
        ntwk.params = params
        self.wizard().pol2_ntwk = ntwk

        log.debug(f"{self.wizard().pol1_ntwk}")
        log.debug(f"{self.wizard().pol2_ntwk}")

        self.analyzer.delete_measurement(msmnt1_name)
        self.analyzer.delete_measurement(msmnt2_name)

        self._calc_loss()

    def _calc_loss(self) -> None:
        ref = self.wizard().ref_ntwk
        ntwk1 = self.wizard().pol1_ntwk
        ntwk2 = self.wizard().pol2_ntwk

        if len(ref) != len(ntwk1):
            ref.interpolate_self(ntwk1.frequency)

        self.wizard().loss1_ntwk = ntwk1 / ref
        self.wizard().loss2_ntwk = ntwk2 / ref

        freqs = self.wizard().loss1_ntwk.frequency.f
        mags1 = self.wizard().loss1_ntwk.s_db.reshape((-1,))
        mags2 = self.wizard().loss2_ntwk.s_db.reshape((-1,))

        mags_min = min(mags1.min(), mags2.min())
        mags_max = max(mags1.max(), mags2.max())

        self.plot.plot_new_data(freqs, mags1)
        self.plot.add_plot(freqs, mags2)
        self.plot.ax.legend([self.pol1_lineedit.text(), self.pol2_lineedit.text()])
        self.plot.redraw_plot()

        self.plot.xmin = freqs.min()
        self.plot.xmax = freqs.max()
        self.plot.ymin = mags_min
        self.plot.ymax = mags_max
        self.plot.ystep = round((mags_max - mags_min) / 5, 1)

    def _on_save_btn_clicked(self) -> None:
        loss1 = self.wizard().loss1_ntwk
        loss2 = self.wizard().loss2_ntwk
        cal = {"notes": self.wizard().cal_notes, "pol1": loss1, "pol2": loss2}

        save_name, _ = QFileDialog.getSaveFileName()
        if save_name != "":
            try:
                with open(save_name, "wb") as ff:
                    ff.write(pickle.dumps(cal))
            except Exception as e:
                log.error(f"{e=}")
                QMessageBox.critical(
                    self, "Save Failure", "An error occurred while saving the calibration"
                )

        self.wizard().cal = cal
        self.wizard().cal_saved.emit(save_name)


class CalViewWindow(QWidget):
    def __init__(self, cal, parent=None) -> None:
        super().__init__(parent)
        self.cal = cal

        self._add_widgets()

    def sizeHint(self) -> QSize:
        return QSize(600, 600)

    def _add_widgets(self) -> None:
        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        textedit = QPlainTextEdit()
        textedit.setPlainText(self.cal["notes"])
        textedit.setReadOnly(True)
        tab_widget.addTab(textedit, "Notes")

        table = QTableView()
        table.setModel(CalTableModel(self.cal))
        tab_widget.addTab(table, "Table")

        self.plot = MplRectWidget()
        self.plot.set_title("Loss Over Frequency")
        self.plot.set_xlabel("Frequency [Hz]")
        self.plot.set_ylabel("Magnitude [dB]")
        self.plot.ax.xaxis.set_major_formatter(EngFormatter(unit='Hz'))

        pol1 = self.cal["pol1"]
        pol2 = self.cal["pol2"]
        freqs = pol1.frequency.f.reshape((-1,))
        mags1 = pol1.s_db.reshape((-1,))
        mags2 = pol2.s_db.reshape((-1,))

        mags_min = min(mags1.min(), mags2.min())
        mags_max = max(mags1.max(), mags2.max())

        pol1_label = pol1.params["polarization"]
        pol2_label = pol2.params["polarization"]
        self.plot.plot_new_data(freqs, mags1)
        self.plot.add_plot(freqs, mags2)
        self.plot.ax.legend([pol1_label, pol2_label])
        self.plot.redraw_plot()

        self.plot.xmin = freqs.min()
        self.plot.xmax = freqs.max()
        self.plot.ymin = mags_min
        self.plot.ymax = mags_max
        self.plot.ystep = round((mags_max - mags_min) / 5, 1)
        tab_widget.addTab(self.plot, "Plot")

        layout.addWidget(tab_widget)
        self.setLayout(layout)


class CalTableModel(QAbstractTableModel):
    # https://stackoverflow.com/questions/71076164/fastest-way-to-fill-or-read-from-a-qtablewidget-in-pyqt5
    def __init__(self, cal_file, parent=None):
        super().__init__(parent)
        pol1 = cal_file["pol1"]
        pol1_label = pol1.params["polarization"]
        pol2 = cal_file["pol2"]
        pol2_label = pol2.params["polarization"]

        self.table_data = pd.DataFrame(
            data={
                pol1_label + " frequency": pol1.frequency.f.reshape((-1,)),
                pol1_label + " loss": pol1.s_db.reshape((-1,)),
                pol2_label + " frequency": pol2.frequency.f.reshape((-1,)),
                pol2_label + " loss": pol2.s_db.reshape((-1,)),
            }
        )

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self.table_data.shape[0]

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return self.table_data.shape[1]

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.DisplayRole:
            return str(round(self.table_data.loc[index.row()][index.column()], 3))

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self.table_data.columns[section])
