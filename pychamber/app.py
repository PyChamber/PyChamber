import logging
import sys
import time
from enum import Enum, auto
from typing import Optional, Tuple

import numpy as np
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QPlainTextEdit

from pychamber import utils
from pychamber.ui.mainWindow import Ui_MainWindow

log = logging.getLogger(__name__)


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super(QPlainTextEditLogger, self).__init__()

        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def write(self, m):
        pass


class MsgLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class PopUpMessage(QMessageBox):
    def __init__(self, msg: str, level: MsgLevel = MsgLevel.INFO) -> None:
        super(PopUpMessage, self).__init__(parent=None)
        if level == MsgLevel.INFO:
            self.setIcon(QMessageBox.Information)
            self.setWindowTitle("PyChamber - Information")
        elif level == MsgLevel.WARNING:
            self.setIcon(QMessageBox.Warning)
            self.setWindowTitle("PyChamber - Warning")
        elif level == MsgLevel.ERROR:
            self.setIcon(QMessageBox.Critical)
            self.setWindowTitle("PyChamber - Error")

        self.setText(msg)
        self.exec_()


class ClearDataWarning(QMessageBox):
    def __init__(self, msg: str) -> None:
        super(ClearDataWarning, self).__init__(parent=None)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Cancel)
        self.setText(msg)

    def warn(self) -> bool:
        ret = self.exec_()
        if ret == QMessageBox.Yes:
            return True
        else:
            return False


class WhichPol(QMessageBox):
    def __init__(self) -> None:
        super(WhichPol, self).__init__()
        self.addButton("1", QMessageBox.NoRole)
        self.addButton("2", QMessageBox.YesRole)
        self.setText("Which Polarization?")

    @classmethod
    def ask(cls) -> int:
        instance = WhichPol()
        ret = instance.exec_()
        if ret == QMessageBox.No:
            return 0
        else:
            return 1


class AppUI(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super(AppUI, self).__init__(parent)

        self.setupUi(self)

        log_handler = QPlainTextEditLogger(self.logTab)
        log_handler.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
        logging.getLogger('pychamber').addHandler(log_handler)
        logging.getLogger('pychamber').setLevel(logging.INFO)
        self.logGrid.addWidget(log_handler.widget)

        self.set_validators()

        self.init_az_extent_plot()
        self.init_el_extent_plot()
        self.cutProgressLabel.hide()
        self.cutProgressBar.hide()

        self.azStartSpinBox.valueChanged.connect(self.update_az_extent_plot)
        self.azStopSpinBox.valueChanged.connect(self.update_az_extent_plot)
        self.azStepSpinBox.valueChanged.connect(self.update_az_extent_plot)
        self.elStartSpinBox.valueChanged.connect(self.update_el_extent_plot)
        self.elStopSpinBox.valueChanged.connect(self.update_el_extent_plot)
        self.elStepSpinBox.valueChanged.connect(self.update_el_extent_plot)

    @property
    def start_freq(self) -> Optional[float]:
        if (f := self.startFreqLineEdit.text()) != "":
            return self.extract_freq(f)
        else:
            return None

    @start_freq.setter
    def start_freq(self, freq: float) -> None:
        self.startFreqLineEdit.setText(str(freq))

    @property
    def stop_freq(self) -> Optional[float]:
        if (f := self.stopFreqLineEdit.text()) != "":
            return self.extract_freq(f)
        else:
            return None

    @stop_freq.setter
    def stop_freq(self, freq: float) -> None:
        self.stopFreqLineEdit.setText(str(freq))

    @property
    def step_freq(self) -> Optional[float]:
        if (f := self.startFreqLineEdit.text()) != "":
            return self.extract_freq(f)
        else:
            return None

    @step_freq.setter
    def step_freq(self, freq: float) -> None:
        self.stepFreqLineEdit.setText(str(freq))

    @property
    def npoints(self) -> Optional[int]:
        if (n := self.nPointsLineEdit.text()) != "":
            try:
                return int(n)
            except ValueError as e:
                PopUpMessage("Invalid input. Must be an integer.")
                log.info(f"{e}")
                return None
        else:
            return None

    @npoints.setter
    def npoints(self, n: int) -> None:
        self.nPointsLineEdit.setText(str(n))

    @property
    def over_freq_scale_min(self) -> float:
        return self.overFreqMinSpinBox.value()

    @property
    def over_freq_scale_max(self) -> float:
        return self.overFreqMaxSpinBox.value()

    @property
    def over_freq_scale_step(self) -> float:
        return self.overFreqDbPerSpinBox.value()

    @property
    def over_freq_pol(self) -> int:
        return self.overFreqPolComboBox.currentIndex()

    @property
    def polar_plot_scale_min(self) -> float:
        return self.dataPolarMinSpinBox.value()

    @property
    def polar_plot_scale_max(self) -> float:
        return self.dataPolarMaxSpinBox.value()

    @property
    def polar_plot_scale_step(self) -> float:
        return self.dataPolarDbPerSpinBox.value()

    @property
    def polar_plot_freq(self) -> str:
        return self.dataPolarFreqSpinBox.cleanText() + self.dataPolarFreqSpinBox.suffix()

    @property
    def polar_plot_pol(self) -> int:
        return self.dataPolarPolComboBox.currentIndex()

    @property
    def analyzer_model(self) -> str:
        return self.analyzerModelComboBox.currentText()

    @property
    def analyzer_port(self) -> str:
        return self.analyzerPortComboBox.currentText()

    @property
    def positioner_model(self) -> str:
        return self.positionerModelComboBox.currentText()

    @property
    def positioner_port(self) -> str:
        return self.positionerPortComboBox.currentText()

    @property
    def el_start(self) -> float:
        return self.elStartSpinBox.value()

    @property
    def el_stop(self) -> float:
        return self.elStopSpinBox.value()

    @property
    def el_step(self) -> float:
        return self.elStepSpinBox.value()

    @property
    def az_start(self) -> float:
        return self.azStartSpinBox.value()

    @property
    def az_stop(self) -> float:
        return self.azStopSpinBox.value()

    @property
    def az_step(self) -> float:
        return self.azStepSpinBox.value()

    @property
    def pol_1(self) -> Optional[Tuple[str, str]]:
        pol = self.pol1ComboBox.text()
        return (pol[1], pol[2]) if pol != "" else None

    @property
    def pol_2(self) -> Optional[Tuple[str, str]]:
        pol = self.pol2ComboBox.text()
        return (pol[1], pol[2]) if pol != "" else None

    @property
    def el_jog_to(self) -> Optional[float]:
        try:
            return float(self.elJogToLineEdit.text())
        except ValueError:
            return None

    @property
    def el_jog_step(self) -> float:
        return self.elJogStepSpinBox.value()

    @property
    def az_jog_to(self) -> Optional[float]:
        try:
            return float(self.azJogToLineEdit.text())
        except ValueError:
            return None

    @property
    def az_jog_step(self) -> float:
        return self.azJogStepSpinBox.value()

    @property
    def az_pos(self) -> float:
        return float(self.azPosLineEdit.text())

    @az_pos.setter
    def az_pos(self, pos: float) -> None:
        self.azPosLineEdit.setText(str(pos))

    @property
    def el_pos(self) -> float:
        return float(self.elPosLineEdit.text())

    @el_pos.setter
    def el_pos(self, pos: float) -> None:
        self.elPosLineEdit.setText(str(pos))

    def closeEvent(self, event) -> None:
        resp = ClearDataWarning(
            ("Are you sure you want to quit?\n" "(Any unsaved data will be LOST)")
        ).warn()
        if resp:
            event.accept()
        else:
            event.ignore()

    def enable_jog(self) -> None:
        self.jogGroupBox.setEnabled(True)

    def disable_jog(self) -> None:
        self.jogGroupBox.setEnabled(False)

    def enable_jog_buttons(self) -> None:
        self.azJogLeftButton.setEnabled(True)
        self.azJogZeroButton.setEnabled(True)
        self.azJogRightButton.setEnabled(True)
        self.azJogToSubmitButton.setEnabled(True)
        self.elJogUpButton.setEnabled(True)
        self.elJogZeroButton.setEnabled(True)
        self.elJogDownButton.setEnabled(True)
        self.elJogToSubmitButton.setEnabled(True)

    def disable_jog_buttons(self) -> None:
        self.azJogLeftButton.setEnabled(False)
        self.azJogZeroButton.setEnabled(False)
        self.azJogRightButton.setEnabled(False)
        self.azJogToSubmitButton.setEnabled(False)
        self.elJogUpButton.setEnabled(False)
        self.elJogZeroButton.setEnabled(False)
        self.elJogDownButton.setEnabled(False)
        self.elJogToSubmitButton.setEnabled(False)

    def enable_freq(self) -> None:
        self.frequencyGroupBox.setEnabled(True)

    def disable_freq(self) -> None:
        self.frequencyGroupBox.setEnabled(False)

    def enable_experiement(self) -> None:
        if self.frequencyGroupBox.isEnabled() and self.jogGroupBox.isEnabled():
            self.experimentGroupBox.setEnabled(True)

    def disable_experiment(self) -> None:
        self.experimentGroupBox.setEnabled(False)

    def extract_freq(self, input: str) -> Optional[float]:
        try:
            return utils.parse_freq_str(input)
        except ValueError as e:
            PopUpMessage(
                (
                    "Invalid frequency string.\n"
                    "Valid format: #[.][#][ ][k|M|G][Hz].\n"
                    "(Bracketed items are optional)"
                )
            )
            log.warning(str(e))
            return None

    def set_validators(self) -> None:
        self.azJogToLineEdit.setValidator(QDoubleValidator(-360.0, 360.0, 2))
        self.elJogToLineEdit.setValidator(QDoubleValidator(-360.0, 360.0, 2))

        self.nPointsLineEdit.setValidator(QIntValidator())

    def init_az_extent_plot(self) -> None:
        log.debug("Initializing Azimuth Plot")
        self.az_extent_ax = self.azExtentMplWidget.canvas.fig.add_subplot(
            projection='polar'
        )
        self.update_az_extent_plot()

    def init_el_extent_plot(self) -> None:
        log.debug("Initializing Elevation Plot")
        self.el_extent_ax = self.elExtentMplWidget.canvas.fig.add_subplot(
            projection='polar'
        )
        self.update_el_extent_plot()

    def update_az_extent_plot(self) -> None:
        start = np.deg2rad(self.azStartSpinBox.value())
        stop = np.deg2rad(self.azStopSpinBox.value())
        step = np.deg2rad(self.azStepSpinBox.value())

        self.overFreqAzSpinBox.setMinimum(start)
        self.overFreqAzSpinBox.setMaximum(stop)
        self.overFreqAzSpinBox.setSingleStep(step)

        thetas = np.arange(start, stop + np.deg2rad(1), step)
        rs = [0, 1] * len(thetas)
        thetas = np.repeat(thetas, 2)
        self.az_extent_ax.clear()
        self.az_extent_ax.plot(thetas, rs, color='tab:cyan', lw=0.5)
        self.az_extent_ax.grid(False)
        self.az_extent_ax.set_rticks([])
        self.az_extent_ax.set_xticklabels([])
        self.az_extent_ax.set_theta_zero_location('N')
        self.az_extent_ax.set_thetagrids(np.arange(0.0, 360.0, 30.0))
        self.azExtentMplWidget.canvas.draw()

    def update_el_extent_plot(self) -> None:
        start = np.deg2rad(self.elStartSpinBox.value())
        stop = np.deg2rad(self.elStopSpinBox.value())
        step = np.deg2rad(self.elStepSpinBox.value())

        self.overFreqElSpinBox.setMinimum(start)
        self.overFreqElSpinBox.setMaximum(stop)
        self.overFreqElSpinBox.setSingleStep(step)

        thetas = np.arange(start, stop + np.deg2rad(1), step)
        rs = [0, 1] * len(thetas)
        thetas = np.repeat(thetas, 2)
        self.el_extent_ax.clear()
        self.el_extent_ax.plot(thetas, rs, color='tab:orange', lw=0.5)
        self.el_extent_ax.grid(False)
        self.el_extent_ax.set_rticks([])
        self.el_extent_ax.set_xticklabels([])
        self.el_extent_ax.set_theta_zero_location('N')
        self.el_extent_ax.set_thetagrids(np.arange(0.0, 360.0, 30.0))
        self.elExtentMplWidget.canvas.draw()

    def reset_progress(self) -> None:
        self.progressBar.setValue(0)

    def update_progress(self, progress: int) -> None:
        if progress == 100:
            self.progressBar.setValue(100)
            self.progressBar.setFormat("Done!")
        else:
            self.progressBar.setValue(progress)
            self.progressBar.setFormat("%p%")

    def reset_cut_progress(self) -> None:
        self.cutProgressBar.setValue(0)

    def update_cut_progress(self, progress: int) -> None:
        self.cutProgressBar.setValue(progress)

    def reset_time_remaining(self) -> None:
        self.timeRemainingLineEdit.setText("")

    def update_time_remaining(self, time_remaining: float) -> None:
        if np.isclose(time_remaining, 0):
            self.timeRemainingLineEdit.setText("")
        else:
            time_str = time.strftime(
                "%H hours %M minutes %S seconds", time.gmtime(time_remaining)
            )
            self.timeRemainingLineEdit.setText(time_str)


def run():
    from pychamber.controller import PyChamberCtrl

    app = QApplication(sys.argv)
    view = AppUI()
    view.show()

    PyChamberCtrl(view=view)

    sys.exit(app.exec_())
