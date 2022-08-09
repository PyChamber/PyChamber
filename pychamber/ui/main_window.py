import time
import webbrowser
from lib2to3.pgen2.token import OP
from typing import List, Optional, Union

import numpy as np
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QIcon, QIntValidator, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QDesktopWidget,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from quantiphy import Quantity

from pychamber import utils
from pychamber.classes.logger import log
from pychamber.classes.polarization import Polarization
from pychamber.classes.settings_manager import SettingsManager
from pychamber.ui import resources_rc

from .freq_spin_box import FrequencySpinBox
from .mplwidget import Mpl3DWidget, MplPolarWidget, MplRectWidget

_SIZE_POLICIES = {
    'min_min': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum),
    'min_pref': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred),
    'min_exp': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding),
    'min_fix': QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed),
    'pref_min': QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum),
    'pref_pref': QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred),
    'exp_min': QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum),
    'exp_pref': QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum),
}

_FONTS = {
    'bold_12': QFont('Roboto', 12, QFont.Bold),
    'bold_14': QFont('Roboto', 14, QFont.Bold),
    'bold_20': QFont('Roboto', 20, QFont.Bold),
    'bold_20_ibm': QFont('IBM 3270', 20, QFont.Bold),
}


class MainWindow(QMainWindow):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.mainWindowLayout = QHBoxLayout()
        self.leftSideLayout = QVBoxLayout()
        self.rightSideLayout = QVBoxLayout()
        self.mainWindowLayout.addLayout(self.leftSideLayout, stretch=1)
        self.mainWindowLayout.addLayout(self.rightSideLayout, stretch=3)
        self.centralwidget.setLayout(self.mainWindowLayout)

        self.setupUi()

        self.setWindowTitle("PyChamber")
        self.setWindowIcon(QIcon(":/logo.png"))

        self.show()
        self.center()

    def setupUi(self) -> None:
        self.setupMenuBar()
        self.setupAnalyzerGroupBox()
        self.setupCalibrationGroupBox()
        self.setupPositionerGroupBox()
        self.setupExperimentGroupBox()
        self.setupTabWidget()

        self.updateSizePolicies()
        self.updateFonts()
        self.updateValidators()
        self.initInputs()
        self.initPlots()

        self.leftSideLayout.addStretch()

        # Convenience methods
        self.update_polar_plot = self.polarPlot.update_plot
        self.update_rect_plot = self.rectPlot.update_plot
        self.update_over_freq_plot = self.overFreqPlot.update_plot
        self.update_3d_plot = self.threeDPlot.update_plot

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @property
    def analyzer_model(self) -> str:
        return self.analyzerModelComboBox.currentText()

    @property
    def analyzer_address(self) -> str:
        return self.analyzerAddressComboBox.currentText()

    @property
    def pol_1(self) -> Optional[Polarization]:
        pol = self.analyzerPol1ComboBox.currentText()
        label = self.analyzerPol1LineEdit.text()
        return Polarization(label, pol) if pol != "" else None

    @property
    def pol_2(self) -> Optional[Polarization]:
        pol = self.analyzerPol2ComboBox.currentText()
        label = self.analyzerPol2LineEdit.text()
        return Polarization(label, pol) if pol != "" else None

    @property
    def analyzer_start_freq(self) -> Optional[Quantity]:
        if (f := self.analyzerStartFreqLineEdit.text()) != "":
            return utils.to_freq(f)
        else:
            return None

    @analyzer_start_freq.setter
    def analyzer_start_freq(self, freq: float) -> None:
        f = Quantity(freq, units='Hz')
        self.analyzerStartFreqLineEdit.setText(f.render())

    @property
    def analyzer_stop_freq(self) -> Optional[Quantity]:
        if (f := self.analyzerStopFreqLineEdit.text()) != "":
            return utils.to_freq(f)
        else:
            return None

    @analyzer_stop_freq.setter
    def analyzer_stop_freq(self, freq: float) -> None:
        f = Quantity(freq, units='Hz')
        self.analyzerStopFreqLineEdit.setText(f.render())

    @property
    def analyzer_freq_step(self) -> Optional[Quantity]:
        if (f := self.analyzerStepFreqLineEdit.text()) != "":
            return utils.to_freq(f)
        else:
            return None

    @analyzer_freq_step.setter
    def analyzer_freq_step(self, freq: float) -> None:
        f = Quantity(freq, units='Hz')
        self.analyzerStepFreqLineEdit.setText(f.render())

    @property
    def analyzer_n_points(self) -> Optional[int]:
        if (n := self.analyzerNPointsLineEdit.text()) != "":
            return int(n)
        else:
            return None

    @analyzer_n_points.setter
    def analyzer_n_points(self, n: int) -> None:
        self.analyzerNPointsLineEdit.setText(str(n))

    @property
    def cal_file_name(self) -> str:
        return self.calibrationFileLineEdit.text()

    @cal_file_name.setter
    def cal_file_name(self, name: str) -> None:
        self.calibrationFileLineEdit.setText(name)

    @property
    def positioner_model(self) -> str:
        return self.positionerModelComboBox.currentText()

    @property
    def positioner_port(self) -> str:
        return self.positionerPortComboBox.currentText()

    @property
    def az_extent_start(self) -> float:
        return self.positionerAzExtentStartSpinBox.value()

    @property
    def az_extent_stop(self) -> float:
        return self.positionerAzExtentStopSpinBox.value()

    @property
    def az_extent_step(self) -> float:
        return self.positionerAzExtentStepSpinBox.value()

    @property
    def el_extent_start(self) -> float:
        return self.positionerElExtentStartSpinBox.value()

    @property
    def el_extent_stop(self) -> float:
        return self.positionerElExtentStopSpinBox.value()

    @property
    def el_extent_step(self) -> float:
        return self.positionerElExtentStepSpinBox.value()

    @property
    def az_jog_step(self) -> float:
        return self.jogAzStepSpinBox.value()

    @property
    def az_jog_to(self) -> Optional[float]:
        try:
            return float(self.jogAzToLineEdit.text())
        except ValueError:
            return None

    @property
    def el_jog_step(self) -> float:
        return self.jogElStepSpinBox.value()

    @property
    def el_jog_to(self) -> Optional[float]:
        try:
            return float(self.jogElToLineEdit.text())
        except ValueError:
            return None

    @property
    def az_pos(self) -> float:
        return float(self.azPositionLineEdit.text())

    @az_pos.setter
    def az_pos(self, pos: Union[float, str]) -> None:
        self.azPositionLineEdit.setText(str(pos))

    @property
    def el_pos(self) -> float:
        return float(self.elPositionLineEdit.text())

    @el_pos.setter
    def el_pos(self, pos: Union[float, str]) -> None:
        self.elPositionLineEdit.setText(str(pos))

    @property
    def total_progress(self) -> int:
        return self.experimentTotalProgressBar.value()

    @total_progress.setter
    def total_progress(self, val: int) -> None:
        self.experimentTotalProgressBar.setValue(val)
        if val == 100:
            self.experimentTotalProgressBar.setFormat("Done!")
        else:
            self.experimentTotalProgressBar.setFormat("%p%")

    @property
    def cut_progress(self) -> int:
        return self.experimentTotalProgressBar.value()

    @cut_progress.setter
    def cut_progress(self, val: int) -> None:
        self.experimentCutProgressBar.setValue(val)

    @property
    def time_remaining(self) -> str:
        return self.experimentTimeRemainingLineEdit.text()

    @time_remaining.setter
    def time_remaining(self, time_: float) -> None:
        if np.isclose(time_, 0):
            self.experimentTimeRemainingLineEdit.setText("")
        else:
            time_str = time.strftime("%H hours %M minutes %S seconds", time.gmtime(time_))
            self.experimentTimeRemainingLineEdit.setText(time_str)

    @property
    def polar_plot_pol(self) -> str:
        return self.polarPlotPolarizationComboBox.currentText()

    @property
    def polar_plot_freq(self) -> Optional[Quantity]:
        if (f := self.polarPlotFreqLineEdit.text()) != "":
            return utils.to_freq(f)
        else:
            return None

    @polar_plot_freq.setter
    def polar_plot_freq(self, freq: Union[str, Quantity]) -> None:
        f = Quantity(freq, units='Hz')
        self.polarPlotFreqLineEdit.setText(f.render())

    @property
    def polar_plot_min(self) -> float:
        return float(self.polarPlotMinSpinBox.value())

    @polar_plot_min.setter
    def polar_plot_min(self, rmin: int) -> None:
        self.polarPlotMinSpinBox.setValue(rmin)

    @property
    def polar_plot_max(self) -> float:
        return float(self.polarPlotMaxSpinBox.value())

    @polar_plot_max.setter
    def polar_plot_max(self, rmax: int) -> None:
        self.polarPlotMaxSpinBox.setValue(rmax)

    @property
    def polar_plot_step(self) -> float:
        return float(self.polarPlotStepSpinBox.value())

    @polar_plot_step.setter
    def polar_plot_step(self, rstep: int) -> None:
        self.polarPlotStepSpinBox.setValue(rstep)

    @property
    def rect_plot_pol(self) -> str:
        return self.rectPlotPolarizationComboBox.currentText()

    @property
    def rect_plot_freq(self) -> Optional[Quantity]:
        if (f := self.rectPlotFreqLineEdit.text()) != "":
            return utils.to_freq(f)
        else:
            return None

    @rect_plot_freq.setter
    def rect_plot_freq(self, freq: Union[str, Quantity]) -> None:
        f = Quantity(freq, units='Hz')
        self.rectPlotFreqLineEdit.setText(f.render())

    @property
    def rect_plot_min(self) -> float:
        return float(self.rectPlotMinSpinBox.value())

    @rect_plot_min.setter
    def rect_plot_min(self, rmin: int) -> None:
        self.rectPlotMinSpinBox.setValue(rmin)

    @property
    def rect_plot_max(self) -> float:
        return float(self.rectPlotMaxSpinBox.value())

    @rect_plot_max.setter
    def rect_plot_max(self, rmax: int) -> None:
        self.rectPlotMaxSpinBox.setValue(rmax)

    @property
    def rect_plot_step(self) -> float:
        return float(self.rectPlotStepSpinBox.value())

    @rect_plot_step.setter
    def rect_plot_step(self, rstep: int) -> None:
        self.rectPlotStepSpinBox.setValue(rstep)

    @property
    def over_freq_plot_pol(self) -> str:
        return self.overFreqPlotPolarizationComboBox.currentText()

    @property
    def over_freq_plot_min(self) -> float:
        return float(self.overFreqPlotMinSpinBox.value())

    @over_freq_plot_min.setter
    def over_freq_plot_min(self, ymin: int) -> None:
        self.overFreqPlotMinSpinBox.setValue(ymin)

    @property
    def over_freq_plot_max(self) -> float:
        return float(self.overFreqPlotMaxSpinBox.value())

    @over_freq_plot_max.setter
    def over_freq_plot_max(self, ymax: int) -> None:
        self.overFreqPlotMaxSpinBox.setValue(ymax)

    @property
    def over_freq_plot_step(self) -> float:
        return float(self.overFreqPlotStepSpinBox.value())

    @over_freq_plot_step.setter
    def over_freq_plot_step(self, ystep: int) -> None:
        self.overFreqPlotStepSpinBox.setValue(ystep)

    @property
    def over_freq_plot_az(self) -> float:
        return self.overFreqPlotAzSpinBox.value()

    @over_freq_plot_az.setter
    def over_freq_plot_az(self, val: float) -> None:
        self.overFreqPlotAzSpinBox.setValue(val)

    @property
    def over_freq_plot_el(self) -> float:
        return self.overFreqPlotElSpinBox.value()

    @over_freq_plot_el.setter
    def over_freq_plot_el(self, val: float) -> None:
        self.overFreqPlotElSpinBox.setValue(val)

    @property
    def three_d_plot_pol(self) -> str:
        return self.threeDPlotPolarizationComboBox.currentText()

    @property
    def three_d_plot_freq(self) -> Optional[Quantity]:
        if (f := self.threeDPlotFreqLineEdit.text()) != "":
            return utils.to_freq(f)
        else:
            return None

    @three_d_plot_freq.setter
    def three_d_plot_freq(self, freq: Union[str, Quantity]) -> None:
        f = Quantity(freq, units='Hz')
        self.threeDPlotFreqLineEdit.setText(f.render())

    def enable_jog(self) -> None:
        self.jogGroupBox.setEnabled(True)

    def disable_jog(self) -> None:
        self.jogGroupBox.setEnabled(False)

    def enable_jog_buttons(self) -> None:
        self.jogAzLeftButton.setEnabled(True)
        self.jogAzZeroButton.setEnabled(True)
        self.jogAzRightButton.setEnabled(True)
        self.jogAzSubmitButton.setEnabled(True)
        self.jogElCWButton.setEnabled(True)
        self.jogElZeroButton.setEnabled(True)
        self.jogElCCWButton.setEnabled(True)
        self.jogElSubmitButton.setEnabled(True)
        self.setZeroButton.setEnabled(True)
        self.returnToZeroButton.setEnabled(True)

    def disable_jog_buttons(self) -> None:
        self.jogAzLeftButton.setEnabled(False)
        self.jogAzZeroButton.setEnabled(False)
        self.jogAzRightButton.setEnabled(False)
        self.jogAzSubmitButton.setEnabled(False)
        self.jogElCWButton.setEnabled(False)
        self.jogElZeroButton.setEnabled(False)
        self.jogElCCWButton.setEnabled(False)
        self.jogElSubmitButton.setEnabled(False)
        self.setZeroButton.setEnabled(False)
        self.returnToZeroButton.setEnabled(False)

    def enable_freq(self) -> None:
        self.analyzerFreqGroupBox.setEnabled(True)

    def disable_freq(self) -> None:
        self.analyzerFreqGroupBox.setEnabled(False)

    def enable_experiment(self) -> None:
        if self.analyzerFreqGroupBox.isEnabled() and self.jogGroupBox.isEnabled():
            self.experimentGroupBox.setEnabled(True)

    def disable_experiment(self) -> None:
        self.experimentGroupBox.setEnabled(False)

    def update_plot_pols(self, pols: List[str]) -> None:
        self.polarPlotPolarizationComboBox.blockSignals(True)
        self.polarPlotFreqLineEdit.blockSignals(True)
        self.rectPlotPolarizationComboBox.blockSignals(True)
        self.rectPlotFreqLineEdit.blockSignals(True)
        self.overFreqPlotPolarizationComboBox.blockSignals(True)

        self.polarPlotPolarizationComboBox.clear()
        self.polarPlotPolarizationComboBox.addItems(pols)
        self.rectPlotPolarizationComboBox.clear()
        self.rectPlotPolarizationComboBox.addItems(pols)
        self.overFreqPlotPolarizationComboBox.clear()
        self.overFreqPlotPolarizationComboBox.addItems(pols)

        self.polarPlotPolarizationComboBox.blockSignals(False)
        self.polarPlotFreqLineEdit.blockSignals(False)
        self.rectPlotPolarizationComboBox.blockSignals(False)
        self.rectPlotFreqLineEdit.blockSignals(False)
        self.overFreqPlotPolarizationComboBox.blockSignals(False)

    def setupMenuBar(self) -> None:
        self.menu = self.menuBar()
        self.file = self.menu.addMenu("File")
        self.save = self.file.addAction("Save")
        self.load = self.file.addAction("Load")
        self.file.addSeparator()
        self.settings = self.file.addAction("Settings")
        self.file.addSeparator()
        self.quit = self.file.addAction("Quit")

        self.tools = self.menu.addMenu("Tools")
        self.python_interpreter = self.tools.addAction("Python Terminal")

        self.help = self.menu.addMenu("Help")
        self.bug = self.help.addAction("Submit a Bug")
        self.help.addSeparator()
        self.about = self.help.addAction("About")
        self.log = self.help.addAction("View Log")

        bug_report_url = "https://github.com/HRG-Lab/PyChamber/issues/new"
        self.bug.triggered.connect(lambda: webbrowser.open(bug_report_url))

    def setupAnalyzerGroupBox(self) -> None:
        self.analyzerGroupBox = QGroupBox("Analyzer", self.centralwidget)
        self.analyzerGroupBoxLayout = QVBoxLayout(self.analyzerGroupBox)

        hlayout = QHBoxLayout()
        self.analyzerModelLabel = QLabel("Model", self.analyzerGroupBox)
        self.analyzerModelComboBox = QComboBox(self.analyzerGroupBox)
        self.analyzerAddressLabel = QLabel("Address", self.analyzerGroupBox)
        self.analyzerAddressComboBox = QComboBox(self.analyzerGroupBox)
        self.analyzerConnectButton = QPushButton("Connect", self.analyzerGroupBox)
        hlayout.addWidget(self.analyzerModelLabel)
        hlayout.addWidget(self.analyzerModelComboBox)
        hlayout.addWidget(self.analyzerAddressLabel)
        hlayout.addWidget(self.analyzerAddressComboBox)
        hlayout.addWidget(self.analyzerConnectButton)
        self.analyzerGroupBoxLayout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.analyzerPol1Label = QLabel("Polarization 1:", self)
        self.analyzerPol1LineEdit = QLineEdit(self)
        self.analyzerPol1LineEdit.setPlaceholderText("Label (e.g. Vertical)")
        self.analyzerPol1ComboBox = QComboBox(self)
        hlayout.addWidget(self.analyzerPol1Label)
        hlayout.addWidget(self.analyzerPol1LineEdit)
        hlayout.addWidget(self.analyzerPol1ComboBox)
        self.analyzerGroupBoxLayout.addLayout(hlayout)
        hlayout = QHBoxLayout()
        self.analyzerPol2Label = QLabel("Polarization 2:", self)
        self.analyzerPol2LineEdit = QLineEdit(self)
        self.analyzerPol2LineEdit.setPlaceholderText("Label")
        self.analyzerPol2ComboBox = QComboBox(self)
        hlayout.addWidget(self.analyzerPol2Label)
        hlayout.addWidget(self.analyzerPol2LineEdit)
        hlayout.addWidget(self.analyzerPol2ComboBox)
        self.analyzerGroupBoxLayout.addLayout(hlayout)

        self.analyzerFreqGroupBox = QGroupBox("Frequency", self.analyzerGroupBox)
        self.analyzerFreqLayout = QGridLayout(self.analyzerFreqGroupBox)

        self.analyzerStartFreqLabel = QLabel("Start", self.analyzerFreqGroupBox)
        self.analyzerStartFreqLineEdit = QLineEdit(self.analyzerFreqGroupBox)
        self.analyzerFreqLayout.addWidget(self.analyzerStartFreqLabel, 0, 0, 1, 1)
        self.analyzerFreqLayout.addWidget(self.analyzerStartFreqLineEdit, 0, 1, 1, 1)

        self.analyzerStopFreqLabel = QLabel("Stop", self.analyzerFreqGroupBox)
        self.analyzerStopFreqLineEdit = QLineEdit(self.analyzerFreqGroupBox)
        self.analyzerFreqLayout.addWidget(self.analyzerStopFreqLabel, 1, 0, 1, 1)
        self.analyzerFreqLayout.addWidget(self.analyzerStopFreqLineEdit, 1, 1, 1, 1)

        self.analyzerStepFreqLabel = QLabel("Step", self.analyzerFreqGroupBox)
        self.analyzerStepFreqLineEdit = QLineEdit(self.analyzerFreqGroupBox)
        self.analyzerFreqLayout.addWidget(self.analyzerStepFreqLabel, 2, 0, 1, 1)
        self.analyzerFreqLayout.addWidget(self.analyzerStepFreqLineEdit, 2, 1, 1, 1)

        self.analyzerNPointsLabel = QLabel("Number of Points", self.analyzerFreqGroupBox)
        self.analyzerNPointsLineEdit = QLineEdit(self.analyzerFreqGroupBox)
        self.analyzerFreqLayout.addWidget(self.analyzerNPointsLabel, 3, 0, 1, 1)
        self.analyzerFreqLayout.addWidget(self.analyzerNPointsLineEdit, 3, 1, 1, 1)

        self.analyzerFreqGroupBox.setEnabled(False)
        self.analyzerGroupBoxLayout.addWidget(self.analyzerFreqGroupBox)

        self.leftSideLayout.addWidget(self.analyzerGroupBox)

    def setupCalibrationGroupBox(self) -> None:
        self.calibrationGroupBox = QGroupBox("Calibration", self.analyzerGroupBox)
        self.calibrationGroupBoxLayout = QVBoxLayout(self.calibrationGroupBox)
        hlayout = QHBoxLayout()
        self.calibrationFileLabel = QLabel("Cal file:", self.calibrationGroupBox)
        self.calibrationFileLineEdit = QLineEdit(self.calibrationGroupBox)
        self.calibrationFileLineEdit.setReadOnly(True)
        self.calibrationFileBrowseButton = QPushButton("Browse", self.calibrationGroupBox)
        hlayout.addWidget(self.calibrationFileLabel)
        hlayout.addWidget(self.calibrationFileLineEdit)
        hlayout.addWidget(self.calibrationFileBrowseButton)
        self.calibrationGroupBoxLayout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.calibrationButton = QPushButton(
            "Generate Cal File", self.calibrationGroupBox
        )
        self.calibrationViewButton = QPushButton(
            "View Cal File", self.calibrationGroupBox
        )
        self.calibrationViewButton.setEnabled(False)
        hlayout.addWidget(self.calibrationButton)
        hlayout.addWidget(self.calibrationViewButton)
        self.calibrationGroupBoxLayout.addLayout(hlayout)

        self.leftSideLayout.addWidget(self.calibrationGroupBox)

    def setupPositionerGroupBox(self) -> None:
        self.positionerGroupBox = QGroupBox("Positioner", self.centralwidget)
        self.positionerGroupBoxLayout = QVBoxLayout(self.positionerGroupBox)

        self.positionerHLayout1 = QHBoxLayout()
        self.positionerModelLabel = QLabel("Model", self.positionerGroupBox)
        self.positionerModelComboBox = QComboBox(self.positionerGroupBox)
        self.positionerHLayout1.addWidget(self.positionerModelLabel)
        self.positionerHLayout1.addWidget(self.positionerModelComboBox)

        self.positionerPortLabel = QLabel("Port", self.positionerGroupBox)
        self.positionerPortComboBox = QComboBox(self.positionerGroupBox)
        self.positionerHLayout1.addWidget(self.positionerPortLabel)
        self.positionerHLayout1.addWidget(self.positionerPortComboBox)

        self.positionerConnectButton = QPushButton("Connect", self.positionerGroupBox)
        self.positionerHLayout1.addWidget(self.positionerConnectButton)
        self.positionerGroupBoxLayout.addLayout(self.positionerHLayout1)

        self.positionerExtentsGroupBox = QGroupBox(self.positionerGroupBox)
        self.positionerExtentsGroupBoxLayout = QHBoxLayout(self.positionerExtentsGroupBox)
        self.setupAzExtentWidgets()
        self.setupElExtentWidgets()
        self.positionerGroupBoxLayout.addWidget(self.positionerExtentsGroupBox)

        self.jogGroupBox = QGroupBox(self.positionerGroupBox)
        self.jogGroupBoxLayout = QVBoxLayout(self.jogGroupBox)
        self.setupJogBox()
        self.positionerGroupBoxLayout.addWidget(self.jogGroupBox)

        self.leftSideLayout.addWidget(self.positionerGroupBox)

    def setupAzExtentWidgets(self) -> None:
        self.positionerAzExtentLayout = QVBoxLayout()
        self.positionerAzExtentLabel = QLabel("Azimuth", self.positionerExtentsGroupBox)
        self.positionerAzExtentLayout.addWidget(self.positionerAzExtentLabel)

        self.positionerAzStartHLayout = QHBoxLayout()
        self.positionerAzExtentStartLabel = QLabel(
            "Start", self.positionerExtentsGroupBox
        )
        self.positionerAzExtentStartSpinBox = QDoubleSpinBox(
            self.positionerExtentsGroupBox
        )
        self.positionerAzStartHLayout.addWidget(self.positionerAzExtentStartLabel)
        self.positionerAzStartHLayout.addWidget(self.positionerAzExtentStartSpinBox)
        self.positionerAzExtentLayout.addLayout(self.positionerAzStartHLayout)

        self.positionerAzStopHLayout = QHBoxLayout()
        self.positionerAzExtentStopLabel = QLabel("Stop", self.positionerExtentsGroupBox)
        self.positionerAzExtentStopSpinBox = QDoubleSpinBox(
            self.positionerExtentsGroupBox
        )
        self.positionerAzStopHLayout.addWidget(self.positionerAzExtentStopLabel)
        self.positionerAzStopHLayout.addWidget(self.positionerAzExtentStopSpinBox)
        self.positionerAzExtentLayout.addLayout(self.positionerAzStopHLayout)

        self.positionerAzStepHLayout = QHBoxLayout()
        self.positionerAzExtentStepLabel = QLabel("Step", self.positionerExtentsGroupBox)
        self.positionerAzExtentStepSpinBox = QDoubleSpinBox(
            self.positionerExtentsGroupBox
        )
        self.positionerAzStepHLayout.addWidget(self.positionerAzExtentStepLabel)
        self.positionerAzStepHLayout.addWidget(self.positionerAzExtentStepSpinBox)
        self.positionerAzExtentLayout.addLayout(self.positionerAzStepHLayout)

        self.positionerExtentsGroupBoxLayout.addLayout(self.positionerAzExtentLayout)

    def setupElExtentWidgets(self) -> None:
        self.positionerElExtentLayout = QVBoxLayout()
        self.positionerElExtentLabel = QLabel("Elevation", self.positionerExtentsGroupBox)
        self.positionerElExtentLayout.addWidget(self.positionerElExtentLabel)

        self.positionerElStartHLayout = QHBoxLayout()
        self.positionerElExtentStartLabel = QLabel(
            "Start", self.positionerExtentsGroupBox
        )
        self.positionerElExtentStartSpinBox = QDoubleSpinBox(
            self.positionerExtentsGroupBox
        )
        self.positionerElStartHLayout.addWidget(self.positionerElExtentStartLabel)
        self.positionerElStartHLayout.addWidget(self.positionerElExtentStartSpinBox)
        self.positionerElExtentLayout.addLayout(self.positionerElStartHLayout)

        self.positionerElStopHLayout = QHBoxLayout()
        self.positionerElExtentStopLabel = QLabel("Stop", self.positionerExtentsGroupBox)
        self.positionerElExtentStopSpinBox = QDoubleSpinBox(
            self.positionerExtentsGroupBox
        )
        self.positionerElStopHLayout.addWidget(self.positionerElExtentStopLabel)
        self.positionerElStopHLayout.addWidget(self.positionerElExtentStopSpinBox)
        self.positionerElExtentLayout.addLayout(self.positionerElStopHLayout)

        self.positionerElStepHLayout = QHBoxLayout()
        self.positionerElExtentStepLabel = QLabel("Step", self.positionerExtentsGroupBox)
        self.positionerElExtentStepSpinBox = QDoubleSpinBox(
            self.positionerExtentsGroupBox
        )
        self.positionerElStepHLayout.addWidget(self.positionerElExtentStepLabel)
        self.positionerElStepHLayout.addWidget(self.positionerElExtentStepSpinBox)
        self.positionerElExtentLayout.addLayout(self.positionerElStepHLayout)

        self.positionerExtentsGroupBoxLayout.addLayout(self.positionerElExtentLayout)

    def setupJogBox(self) -> None:
        self.jogButtonsLayout = QGridLayout()

        self.jogAzLabel = QLabel("Azimuth", self.jogGroupBox)
        self.jogAzStepLabel = QLabel("Step", self.jogGroupBox)
        self.jogAzToLabel = QLabel("Jog Azimuth To", self.jogGroupBox)
        self.jogAzLeftButton = QPushButton(self.jogGroupBox)
        self.jogAzLeftButton.setIcon(QIcon(QPixmap(":/icons/icons/LeftArrow.png")))
        self.jogAzLeftButton.setIconSize(QSize(32, 32))
        self.jogAzZeroButton = QPushButton("0", self.jogGroupBox)
        self.jogAzRightButton = QPushButton(self.jogGroupBox)
        self.jogAzRightButton.setIcon(QIcon(QPixmap(":/icons/icons/RightArrow.png")))
        self.jogAzRightButton.setIconSize(QSize(32, 32))
        self.jogAzSubmitButton = QPushButton(self.jogGroupBox)
        self.jogAzSubmitButton.setIcon(QIcon(QPixmap(":/icons/icons/Check.png")))
        self.jogAzSubmitButton.setIconSize(QSize(32, 32))
        self.jogAzStepSpinBox = QDoubleSpinBox(self.jogGroupBox)
        self.jogAzToLineEdit = QLineEdit(self.jogGroupBox)

        self.jogButtonsLayout.addWidget(self.jogAzLabel, 0, 0, 1, 3)
        self.jogButtonsLayout.addWidget(self.jogAzStepLabel, 0, 3, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzToLabel, 0, 4, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzLeftButton, 1, 0, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzZeroButton, 1, 1, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzRightButton, 1, 2, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzStepSpinBox, 1, 3, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzToLineEdit, 1, 4, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogAzSubmitButton, 1, 5, 1, 1)

        self.jogElLabel = QLabel("Elevation", self.jogGroupBox)
        self.jogElStepLabel = QLabel("Step", self.jogGroupBox)
        self.jogElToLabel = QLabel("Jog Elevation To", self.jogGroupBox)
        self.jogElCWButton = QPushButton("", self.jogGroupBox)
        self.jogElCWButton.setIcon(QIcon(QPixmap(":/icons/icons/DownArrow.png")))
        self.jogElCWButton.setIconSize(QSize(32, 32))
        self.jogElZeroButton = QPushButton("0", self.jogGroupBox)
        self.jogElCCWButton = QPushButton("", self.jogGroupBox)
        self.jogElCCWButton.setIcon(QIcon(QPixmap(":/icons/icons/DownArrow.png")))
        self.jogElCCWButton.setIconSize(QSize(32, 32))
        self.jogElSubmitButton = QPushButton("", self.jogGroupBox)
        self.jogElSubmitButton.setIcon(QIcon(QPixmap(":/icons/icons/Check.png")))
        self.jogElSubmitButton.setIconSize(QSize(32, 32))
        self.jogElStepSpinBox = QDoubleSpinBox(self.jogGroupBox)
        self.jogElToLineEdit = QLineEdit(self.jogGroupBox)

        self.jogButtonsLayout.addWidget(self.jogElLabel, 2, 0, 1, 3)
        self.jogButtonsLayout.addWidget(self.jogElStepLabel, 2, 3, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElToLabel, 2, 4, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElCWButton, 3, 0, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElZeroButton, 3, 1, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElCCWButton, 3, 2, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElStepSpinBox, 3, 3, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElToLineEdit, 3, 4, 1, 1)
        self.jogButtonsLayout.addWidget(self.jogElSubmitButton, 3, 5, 1, 1)

        self.jogGroupBoxLayout.addLayout(self.jogButtonsLayout)

        self.positionerPosLayout = QHBoxLayout()
        self.azPositionLayout = QVBoxLayout()
        self.azPositionLabel = QLabel("Azimuth", self.jogGroupBox)
        self.azPositionLineEdit = QLineEdit(self.jogGroupBox)
        self.azPositionLineEdit.setReadOnly(True)
        self.azPositionLayout.addWidget(self.azPositionLabel)
        self.azPositionLayout.addWidget(self.azPositionLineEdit)

        self.elPositionLayout = QVBoxLayout()
        self.elPositionLabel = QLabel("Elevation", self.jogGroupBox)
        self.elPositionLineEdit = QLineEdit(self.jogGroupBox)
        self.elPositionLineEdit.setReadOnly(True)
        self.elPositionLayout.addWidget(self.elPositionLabel)
        self.elPositionLayout.addWidget(self.elPositionLineEdit)

        self.zeroButtonLayout = QHBoxLayout()
        self.setZeroButton = QPushButton("Set 0,0", self.jogGroupBox)
        self.returnToZeroButton = QPushButton("Return to 0,0", self.jogGroupBox)
        self.zeroButtonLayout.addWidget(self.setZeroButton)
        self.zeroButtonLayout.addWidget(self.returnToZeroButton)

        self.positionerPosLayout.addLayout(self.azPositionLayout)
        self.positionerPosLayout.addLayout(self.elPositionLayout)
        self.jogGroupBoxLayout.addLayout(self.positionerPosLayout)
        self.jogGroupBoxLayout.addLayout(self.zeroButtonLayout)

        self.jogGroupBox.setEnabled(False)

    def setupExperimentGroupBox(self) -> None:
        self.experimentGroupBox = QGroupBox("Experiment", self.centralwidget)
        self.experimentGroupBoxLayout = QHBoxLayout(self.experimentGroupBox)

        self.experimentButtonVLayout = QVBoxLayout()
        self.experimentFullScanButton = QPushButton("Full Scan", self.experimentGroupBox)
        self.experimentAzScanButton = QPushButton("Scan Azimuth", self.experimentGroupBox)
        self.experimentElScanButton = QPushButton(
            "Scan Elevation", self.experimentGroupBox
        )
        self.experimentAbortButton = QPushButton("ABORT", self.experimentGroupBox)
        self.experimentAbortButton.setStyleSheet("background-color: rgb(237, 51, 59)")
        self.experimentButtonVLayout.addWidget(self.experimentFullScanButton)
        self.experimentButtonVLayout.addWidget(self.experimentAzScanButton)
        self.experimentButtonVLayout.addWidget(self.experimentElScanButton)
        self.experimentButtonVLayout.addWidget(self.experimentAbortButton)
        self.experimentAbortButton.setEnabled(False)

        self.experimentProgressVLayout = QVBoxLayout()
        self.experimentTotalProgressLabel = QLabel(
            "Total Progress", self.experimentGroupBox
        )
        self.experimentTotalProgressBar = QProgressBar(self.experimentGroupBox)
        self.experimentProgressVLayout.addWidget(self.experimentTotalProgressLabel)
        self.experimentProgressVLayout.addWidget(self.experimentTotalProgressBar)

        self.experimentCutProgressLabel = QLabel("Cut Progress", self.experimentGroupBox)
        self.experimentCutProgressBar = QProgressBar(self.experimentGroupBox)
        self.experimentProgressVLayout.addWidget(self.experimentCutProgressLabel)
        self.experimentProgressVLayout.addWidget(self.experimentCutProgressBar)

        self.experimentTimeRemainingLabel = QLabel(
            "Time Remaining Estimate", self.experimentGroupBox
        )
        self.experimentTimeRemainingLineEdit = QLineEdit(self.experimentGroupBox)
        self.experimentProgressVLayout.addWidget(self.experimentTimeRemainingLabel)
        self.experimentProgressVLayout.addWidget(self.experimentTimeRemainingLineEdit)

        self.experimentGroupBoxLayout.addLayout(self.experimentButtonVLayout)
        self.experimentGroupBoxLayout.addLayout(self.experimentProgressVLayout)

        self.rightSideLayout.addWidget(self.experimentGroupBox)
        self.experimentGroupBox.setEnabled(False)
        self.experimentCutProgressLabel.hide()
        self.experimentCutProgressBar.hide()

    def setupTabWidget(self) -> None:
        self.tabWidget = QTabWidget(self.centralwidget)

        self.polarPlotTab = QWidget(self.tabWidget)
        self.rectPlotTab = QWidget(self.tabWidget)
        self.overFreqPlotTab = QWidget(self.tabWidget)
        self.threeDPlotTab = QWidget(self.tabWidget)

        self.tabWidget.addTab(self.polarPlotTab, "Polar Plot")
        self.tabWidget.addTab(self.rectPlotTab, "Rectangular Plot")
        self.tabWidget.addTab(self.overFreqPlotTab, "Over Frequency Plot")
        self.tabWidget.addTab(self.threeDPlotTab, "3D Plot")

        self.setupPolarPlotTab()
        self.setupRectPlotTab()
        self.setupOverFreqPlotTab()
        self.setup3DPlotTab()

        self.rightSideLayout.addWidget(self.tabWidget)

    def setupPolarPlotTab(self) -> None:
        tab = self.polarPlotTab
        self.polarPlotTabLayout = QVBoxLayout(tab)

        self.polarPlotSettingsHLayout = QHBoxLayout()
        self.polarPlotPolarizationLabel = QLabel("Polarization", tab)
        self.polarPlotPolarizationComboBox = QComboBox(tab)
        self.polarPlotPolarizationComboBox.addItems(['1', '2'])
        self.polarPlotFreqLabel = QLabel("Frequency", tab)
        self.polarPlotFreqLineEdit = QLineEdit(tab)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.polarPlotAutoScaleButton = QPushButton("Auto Scale", tab)
        self.polarPlotMinLabel = QLabel("Min", tab)
        self.polarPlotMinSpinBox = QSpinBox(tab)
        self.polarPlotMaxLabel = QLabel("Max", tab)
        self.polarPlotMaxSpinBox = QSpinBox(tab)
        self.polarPlotStepLabel = QLabel("dB/div", tab)
        self.polarPlotStepSpinBox = QSpinBox(tab)

        self.polarPlotSettingsHLayout.addWidget(self.polarPlotPolarizationLabel)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotPolarizationComboBox)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotFreqLabel)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotFreqLineEdit)
        self.polarPlotSettingsHLayout.addItem(spacer)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotAutoScaleButton)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotMinLabel)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotMinSpinBox)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotMaxLabel)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotMaxSpinBox)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotStepLabel)
        self.polarPlotSettingsHLayout.addWidget(self.polarPlotStepSpinBox)
        self.polarPlotTabLayout.addLayout(self.polarPlotSettingsHLayout)

        self.polarPlot = MplPolarWidget('tab:blue', tab)
        self.polarPlotTabLayout.addWidget(self.polarPlot)

    def setupRectPlotTab(self) -> None:
        tab = self.rectPlotTab
        self.rectPlotLayout = QVBoxLayout(tab)

        self.rectPlotSettingsHLayout = QHBoxLayout()
        self.rectPlotPolarizationLabel = QLabel("Polarization", tab)
        self.rectPlotPolarizationComboBox = QComboBox(tab)
        self.rectPlotPolarizationComboBox.addItems(['1', '2'])
        self.rectPlotFreqLabel = QLabel("Frequency", tab)
        self.rectPlotFreqLineEdit = QLineEdit(tab)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.rectPlotAutoScaleButton = QPushButton("Auto Scale", tab)
        self.rectPlotMinLabel = QLabel("Min", tab)
        self.rectPlotMinSpinBox = QSpinBox(tab)
        self.rectPlotMaxLabel = QLabel("Max", tab)
        self.rectPlotMaxSpinBox = QSpinBox(tab)
        self.rectPlotStepLabel = QLabel("dB/div", tab)
        self.rectPlotStepSpinBox = QSpinBox(tab)

        self.rectPlotSettingsHLayout.addWidget(self.rectPlotPolarizationLabel)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotPolarizationComboBox)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotFreqLabel)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotFreqLineEdit)
        self.rectPlotSettingsHLayout.addItem(spacer)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotAutoScaleButton)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotMinLabel)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotMinSpinBox)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotMaxLabel)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotMaxSpinBox)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotStepLabel)
        self.rectPlotSettingsHLayout.addWidget(self.rectPlotStepSpinBox)
        self.rectPlotLayout.addLayout(self.rectPlotSettingsHLayout)

        self.rectPlot = MplRectWidget('tab:blue', tab)
        self.rectPlotLayout.addWidget(self.rectPlot)

    def setupOverFreqPlotTab(self) -> None:
        tab = self.overFreqPlotTab
        self.overFreqPlotTabLayout = QVBoxLayout(tab)

        self.overFreqPlotSettingsHLayout1 = QHBoxLayout()
        self.overFreqPlotPolarizationLabel = QLabel("Polarization", tab)
        self.overFreqPlotPolarizationComboBox = QComboBox(tab)
        self.overFreqPlotPolarizationComboBox.addItems(['1', '2'])
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.overFreqPlotAutoScaleButton = QPushButton("Auto Scale", tab)
        self.overFreqPlotMinLabel = QLabel("Min", tab)
        self.overFreqPlotMinSpinBox = QSpinBox(tab)
        self.overFreqPlotMaxLabel = QLabel("Max", tab)
        self.overFreqPlotMaxSpinBox = QSpinBox(tab)
        self.overFreqPlotStepLabel = QLabel("dB/div", tab)
        self.overFreqPlotStepSpinBox = QSpinBox(tab)

        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotPolarizationLabel)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotPolarizationComboBox)
        self.overFreqPlotSettingsHLayout1.addItem(spacer)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotAutoScaleButton)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotMinLabel)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotMinSpinBox)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotMaxLabel)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotMaxSpinBox)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotStepLabel)
        self.overFreqPlotSettingsHLayout1.addWidget(self.overFreqPlotStepSpinBox)

        self.overFreqPlotSettingsHLayout2 = QHBoxLayout()
        self.overFreqPlotAzLabel = QLabel("Azimuth", tab)
        self.overFreqPlotAzSpinBox = QDoubleSpinBox(tab)
        self.overFreqPlotElLabel = QLabel("Elevation", tab)
        self.overFreqPlotElSpinBox = QDoubleSpinBox(tab)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.overFreqPlotSettingsHLayout2.addWidget(self.overFreqPlotAzLabel)
        self.overFreqPlotSettingsHLayout2.addWidget(self.overFreqPlotAzSpinBox)
        self.overFreqPlotSettingsHLayout2.addWidget(self.overFreqPlotElLabel)
        self.overFreqPlotSettingsHLayout2.addWidget(self.overFreqPlotElSpinBox)
        self.overFreqPlotSettingsHLayout2.addItem(spacer)

        self.overFreqPlotTabLayout.addLayout(self.overFreqPlotSettingsHLayout1)
        self.overFreqPlotTabLayout.addLayout(self.overFreqPlotSettingsHLayout2)

        self.overFreqPlot = MplRectWidget('tab:blue', tab)
        self.overFreqPlotTabLayout.addWidget(self.overFreqPlot)

    def setup3DPlotTab(self) -> None:
        tab = self.threeDPlotTab
        self.threeDPlotLayout = QVBoxLayout(tab)

        self.threeDPlotPolarizationLabel = QLabel("Polarization", tab)
        self.threeDPlotPolarizationComboBox = QComboBox(tab)
        self.threeDPlotPolarizationComboBox.addItems(['1', '2'])
        self.threeDPlotFreqLabel = QLabel("Frequency", tab)
        self.threeDPlotFreqLineEdit = QLineEdit(tab)
        self.threeDPlotRefreshPlotButton = QPushButton("Refresh Plot", tab)

        self.threeDPlotSettingsHLayout = QHBoxLayout()
        self.threeDPlotSettingsHLayout.addWidget(self.threeDPlotPolarizationLabel)
        self.threeDPlotSettingsHLayout.addWidget(self.threeDPlotPolarizationComboBox)
        self.threeDPlotSettingsHLayout.addWidget(self.threeDPlotFreqLabel)
        self.threeDPlotSettingsHLayout.addWidget(self.threeDPlotFreqLineEdit)
        self.threeDPlotSettingsHLayout.addWidget(self.threeDPlotRefreshPlotButton)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.threeDPlotSettingsHLayout.addItem(spacer)

        self.threeDPlotLayout.addLayout(self.threeDPlotSettingsHLayout)

        self.threeDPlot = Mpl3DWidget(tab)
        self.threeDPlotLayout.addWidget(self.threeDPlot)

    def updateSizePolicies(self) -> None:
        self.analyzerModelLabel.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.analyzerModelComboBox.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerAddressLabel.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.analyzerAddressComboBox.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerConnectButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.analyzerPol1Label.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.analyzerPol1ComboBox.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerPol2Label.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.analyzerPol2ComboBox.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerFreqGroupBox.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.analyzerStartFreqLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.analyzerStopFreqLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.analyzerStepFreqLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.analyzerNPointsLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.analyzerStartFreqLineEdit.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerStopFreqLineEdit.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerStepFreqLineEdit.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.analyzerNPointsLineEdit.setSizePolicy(_SIZE_POLICIES['exp_pref'])

        self.positionerModelLabel.setSizePolicy(_SIZE_POLICIES["min_pref"])
        self.positionerModelComboBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerPortLabel.setSizePolicy(_SIZE_POLICIES["min_pref"])
        self.positionerPortComboBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerConnectButton.setSizePolicy(_SIZE_POLICIES["min_pref"])

        self.positionerAzExtentStartSpinBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerAzExtentStopSpinBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerAzExtentStepSpinBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerElExtentStartSpinBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerElExtentStopSpinBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])
        self.positionerElExtentStepSpinBox.setSizePolicy(_SIZE_POLICIES["exp_pref"])

        self.jogAzLabel.setSizePolicy(_SIZE_POLICIES['pref_min'])
        self.jogAzStepLabel.setSizePolicy(_SIZE_POLICIES['pref_min'])
        self.jogAzToLabel.setSizePolicy(_SIZE_POLICIES['pref_min'])
        self.jogAzLeftButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogAzZeroButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogAzRightButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogAzStepSpinBox.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogAzToLineEdit.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.jogAzSubmitButton.setSizePolicy(_SIZE_POLICIES['min_pref'])

        self.jogElLabel.setSizePolicy(_SIZE_POLICIES['pref_min'])
        self.jogElStepLabel.setSizePolicy(_SIZE_POLICIES['pref_min'])
        self.jogElToLabel.setSizePolicy(_SIZE_POLICIES['pref_min'])
        self.jogElCWButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogElZeroButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogElCCWButton.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogElStepSpinBox.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.jogElToLineEdit.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.jogElSubmitButton.setSizePolicy(_SIZE_POLICIES['min_pref'])

        self.azPositionLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.azPositionLineEdit.setSizePolicy(_SIZE_POLICIES['min_pref'])
        self.elPositionLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.elPositionLineEdit.setSizePolicy(_SIZE_POLICIES['min_pref'])

        self.experimentFullScanButton.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.experimentAzScanButton.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.experimentElScanButton.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.experimentAbortButton.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.experimentTotalProgressLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.experimentTotalProgressBar.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.experimentCutProgressLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.experimentCutProgressBar.setSizePolicy(_SIZE_POLICIES['exp_pref'])
        self.experimentTimeRemainingLabel.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.experimentTimeRemainingLineEdit.setSizePolicy(_SIZE_POLICIES['exp_pref'])

        self.polarPlotFreqLineEdit.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.polarPlotFreqLineEdit.setMinimumWidth(100)

        self.rectPlotFreqLineEdit.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.rectPlotFreqLineEdit.setMinimumWidth(100)

        self.threeDPlotFreqLineEdit.setSizePolicy(_SIZE_POLICIES['pref_pref'])
        self.threeDPlotFreqLineEdit.setMinimumWidth(100)

    def updateFonts(self) -> None:
        self.positionerAzExtentLabel.setFont(_FONTS["bold_14"])
        self.positionerAzExtentLabel.setAlignment(Qt.AlignHCenter)
        self.positionerElExtentLabel.setFont(_FONTS["bold_14"])
        self.positionerElExtentLabel.setAlignment(Qt.AlignHCenter)

        self.jogAzLabel.setFont(_FONTS["bold_12"])
        self.jogAzLabel.setAlignment(Qt.AlignHCenter)
        self.jogAzStepLabel.setFont(_FONTS["bold_12"])
        self.jogAzStepLabel.setAlignment(Qt.AlignHCenter)
        self.jogAzToLabel.setFont(_FONTS["bold_12"])
        self.jogAzToLabel.setAlignment(Qt.AlignHCenter)
        self.jogAzZeroButton.setFont(_FONTS["bold_20"])
        self.jogElLabel.setFont(_FONTS["bold_12"])
        self.jogElLabel.setAlignment(Qt.AlignHCenter)
        self.jogElStepLabel.setFont(_FONTS["bold_12"])
        self.jogElStepLabel.setAlignment(Qt.AlignHCenter)
        self.jogElToLabel.setFont(_FONTS["bold_12"])
        self.jogElToLabel.setAlignment(Qt.AlignHCenter)
        self.jogElZeroButton.setFont(_FONTS["bold_20"])

        self.azPositionLabel.setFont(_FONTS["bold_12"])
        self.azPositionLabel.setAlignment(Qt.AlignHCenter)
        self.azPositionLineEdit.setFont(_FONTS["bold_20_ibm"])
        self.elPositionLabel.setFont(_FONTS["bold_12"])
        self.elPositionLabel.setAlignment(Qt.AlignHCenter)
        self.elPositionLineEdit.setFont(_FONTS["bold_20_ibm"])

        self.experimentFullScanButton.setFont(_FONTS["bold_12"])
        self.experimentAzScanButton.setFont(_FONTS["bold_12"])
        self.experimentElScanButton.setFont(_FONTS["bold_12"])
        self.experimentAbortButton.setFont(_FONTS["bold_12"])

        self.experimentTotalProgressLabel.setFont(_FONTS["bold_12"])
        self.experimentTotalProgressLabel.setAlignment(Qt.AlignHCenter)
        self.experimentCutProgressLabel.setFont(_FONTS["bold_12"])
        self.experimentCutProgressLabel.setAlignment(Qt.AlignHCenter)
        self.experimentTimeRemainingLabel.setFont(_FONTS["bold_12"])
        self.experimentTimeRemainingLabel.setAlignment(Qt.AlignHCenter)

    def updateValidators(self) -> None:
        self.jogAzToLineEdit.setValidator(QDoubleValidator(-360.0, 360.0, 2))
        self.jogElToLineEdit.setValidator(QDoubleValidator(-360.0, 360.0, 2))

        self.analyzerNPointsLineEdit.setValidator(QIntValidator())

    def updateFromSettings(self, settings: SettingsManager) -> None:
        self.analyzerModelComboBox.setCurrentText(settings["analyzer-model"])
        self.analyzerAddressComboBox.setCurrentText(settings["analyzer-addr"])
        self.positionerModelComboBox.setCurrentText(settings["positioner-model"])
        self.positionerPortComboBox.setCurrentText(settings["positioner-port"])

        self.analyzerPol1LineEdit.setText(settings["pol1-label"])
        self.analyzerPol1ComboBox.setCurrentText(settings["pol1-param"])
        self.analyzerPol2LineEdit.setText(settings["pol2-label"])
        self.analyzerPol2ComboBox.setCurrentText(settings["pol2-param"])

        self.positionerAzExtentStartSpinBox.setValue(float(settings["az-start"]))
        self.positionerAzExtentStopSpinBox.setValue(float(settings["az-stop"]))
        self.positionerAzExtentStepSpinBox.setValue(float(settings["az-step"]))
        self.positionerElExtentStartSpinBox.setValue(float(settings["el-start"]))
        self.positionerElExtentStopSpinBox.setValue(float(settings["el-stop"]))
        self.positionerElExtentStepSpinBox.setValue(float(settings["el-step"]))

    def initInputs(self) -> None:
        self.positionerAzExtentStartSpinBox.setMinimum(-180.0)
        self.positionerAzExtentStartSpinBox.setMaximum(180.0)
        self.positionerAzExtentStartSpinBox.setSingleStep(1.0)
        self.positionerAzExtentStartSpinBox.setDecimals(2)
        self.positionerAzExtentStartSpinBox.setValue(-90.0)

        self.positionerAzExtentStopSpinBox.setMinimum(-180.0)
        self.positionerAzExtentStopSpinBox.setMaximum(180.0)
        self.positionerAzExtentStopSpinBox.setSingleStep(1.0)
        self.positionerAzExtentStopSpinBox.setDecimals(2)
        self.positionerAzExtentStopSpinBox.setValue(90.0)

        self.positionerAzExtentStepSpinBox.setMinimum(0.0)
        self.positionerAzExtentStepSpinBox.setMaximum(360.0)
        self.positionerAzExtentStepSpinBox.setSingleStep(1.0)
        self.positionerAzExtentStepSpinBox.setDecimals(2)
        self.positionerAzExtentStepSpinBox.setValue(5.0)

        self.positionerElExtentStartSpinBox.setMinimum(-180.0)
        self.positionerElExtentStartSpinBox.setMaximum(180.0)
        self.positionerElExtentStartSpinBox.setSingleStep(1.0)
        self.positionerElExtentStartSpinBox.setDecimals(2)
        self.positionerElExtentStartSpinBox.setValue(-90.0)

        self.positionerElExtentStopSpinBox.setMinimum(-180.0)
        self.positionerElExtentStopSpinBox.setMaximum(180.0)
        self.positionerElExtentStopSpinBox.setSingleStep(1.0)
        self.positionerElExtentStopSpinBox.setDecimals(2)
        self.positionerElExtentStopSpinBox.setValue(90.0)

        self.positionerElExtentStepSpinBox.setMinimum(0.0)
        self.positionerElExtentStepSpinBox.setMaximum(360.0)
        self.positionerElExtentStepSpinBox.setSingleStep(1.0)
        self.positionerElExtentStepSpinBox.setDecimals(2)
        self.positionerElExtentStepSpinBox.setValue(5.0)

        self.jogAzStepSpinBox.setMinimum(0.0)
        self.jogAzStepSpinBox.setMaximum(180.0)
        self.jogAzStepSpinBox.setSingleStep(0.25)
        self.jogAzStepSpinBox.setDecimals(2)
        self.jogAzStepSpinBox.setValue(0.0)

        self.jogElStepSpinBox.setMinimum(0.0)
        self.jogElStepSpinBox.setMaximum(180.0)
        self.jogElStepSpinBox.setSingleStep(0.25)
        self.jogElStepSpinBox.setDecimals(2)
        self.jogElStepSpinBox.setValue(0.0)

        self.jogAzToLineEdit.setPlaceholderText("0.0")
        self.jogElToLineEdit.setPlaceholderText("0.0")

        self.polarPlotMinSpinBox.setMinimum(-100)
        self.polarPlotMinSpinBox.setMaximum(100)
        self.polarPlotMinSpinBox.setSingleStep(5)
        self.polarPlotMinSpinBox.setValue(-30)

        self.polarPlotMaxSpinBox.setMinimum(-100)
        self.polarPlotMaxSpinBox.setMaximum(100)
        self.polarPlotMaxSpinBox.setSingleStep(5)
        self.polarPlotMaxSpinBox.setValue(0)

        self.polarPlotStepSpinBox.setMinimum(1)
        self.polarPlotStepSpinBox.setMaximum(100)
        self.polarPlotStepSpinBox.setSingleStep(10)
        self.polarPlotStepSpinBox.setValue(10)

        self.rectPlotMinSpinBox.setMinimum(-100)
        self.rectPlotMinSpinBox.setMaximum(100)
        self.rectPlotMinSpinBox.setSingleStep(5)
        self.rectPlotMinSpinBox.setValue(-30)

        self.rectPlotMaxSpinBox.setMinimum(-100)
        self.rectPlotMaxSpinBox.setMaximum(100)
        self.rectPlotMaxSpinBox.setSingleStep(5)
        self.rectPlotMaxSpinBox.setValue(0)

        self.rectPlotStepSpinBox.setMinimum(1)
        self.rectPlotStepSpinBox.setMaximum(100)
        self.rectPlotStepSpinBox.setSingleStep(10)
        self.rectPlotStepSpinBox.setValue(10)

        self.overFreqPlotMinSpinBox.setMinimum(-100)
        self.overFreqPlotMinSpinBox.setMaximum(100)
        self.overFreqPlotMinSpinBox.setSingleStep(5)
        self.overFreqPlotMinSpinBox.setValue(-30)

        self.overFreqPlotMaxSpinBox.setMinimum(-100)
        self.overFreqPlotMaxSpinBox.setMaximum(100)
        self.overFreqPlotMaxSpinBox.setSingleStep(5)
        self.overFreqPlotMaxSpinBox.setValue(0)

        self.overFreqPlotStepSpinBox.setMinimum(1)
        self.overFreqPlotStepSpinBox.setMaximum(100)
        self.overFreqPlotStepSpinBox.setSingleStep(10)
        self.overFreqPlotStepSpinBox.setValue(10)

    def initPlots(self) -> None:
        self.polarPlot.set_scale(
            min=self.polar_plot_min, max=self.polar_plot_max, step=self.polar_plot_step
        )
        self.polarPlotMinSpinBox.valueChanged.connect(self.polarPlot.set_scale_min)
        self.polarPlotMaxSpinBox.valueChanged.connect(self.polarPlot.set_scale_max)
        self.polarPlotStepSpinBox.valueChanged.connect(self.polarPlot.set_scale_step)

        self.rectPlot.set_xtitle("Frequency")
        self.rectPlot.set_ytitle("Gain [dB]")
        self.rectPlot.set_scale(
            min=self.rect_plot_min, max=self.rect_plot_max, step=self.rect_plot_step
        )
        self.rectPlotMinSpinBox.valueChanged.connect(self.rectPlot.set_scale_min)
        self.rectPlotMaxSpinBox.valueChanged.connect(self.rectPlot.set_scale_max)
        self.rectPlotStepSpinBox.valueChanged.connect(self.rectPlot.set_scale_step)

        self.overFreqPlot.set_xtitle("Frequency")
        self.overFreqPlot.set_ytitle("Gain [dB]")
        self.overFreqPlot.set_scale(
            min=self.over_freq_plot_min,
            max=self.over_freq_plot_max,
            step=self.over_freq_plot_step,
        )
        self.overFreqPlotMinSpinBox.valueChanged.connect(self.overFreqPlot.set_scale_min)
        self.overFreqPlotMaxSpinBox.valueChanged.connect(self.overFreqPlot.set_scale_max)
        self.overFreqPlotStepSpinBox.valueChanged.connect(
            self.overFreqPlot.set_scale_step
        )
