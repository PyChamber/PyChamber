import functools
from operator import setitem
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget

from pychamber.app.ui.experiment_widget import Ui_ExperimentWidget
from pychamber.calibration import Calibration
from pychamber.settings import CONF

from .cal_view_dialog import CalViewDialog
from .cal_wizard import CalWizard
from .collapsible_widget import CollapsibleWidget


class ExperimentWidget(QWidget, Ui_ExperimentWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)


class ExperimentControls(CollapsibleWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, name="Experiment")

        self.setupUi()
        self.postvisible_setup()
        self.connect_signals()

    def setupUi(self) -> None:
        self.widget = ExperimentWidget(self)
        self.addWidget(self.widget)
        self.recalculateSize()

    def connect_signals(self) -> None:
        self.widget.az_start_dsb.valueChanged.connect(functools.partial(setitem, CONF, "az_start"))
        self.widget.az_stop_dsb.valueChanged.connect(functools.partial(setitem, CONF, "az_stop"))
        self.widget.az_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "az_step"))
        self.widget.el_start_dsb.valueChanged.connect(functools.partial(setitem, CONF, "el_start"))
        self.widget.el_stop_dsb.valueChanged.connect(functools.partial(setitem, CONF, "el_stop"))
        self.widget.el_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "el_step"))
        self.widget.cal_file_browse_btn.pressed.connect(self.on_cal_browse_btn_pressed)
        self.widget.cal_wizard_btn.pressed.connect(self.run_cal_wizard)
        self.widget.view_cal_btn.pressed.connect(self.view_cal)

    def postvisible_setup(self) -> None:
        widget_map = {
            "az_start": (self.widget.az_start_dsb, 0, float),
            "az_stop": (self.widget.az_stop_dsb, 90, float),
            "az_step": (self.widget.az_step_dsb, 1, float),
            "el_start": (self.widget.el_start_dsb, 0, float),
            "el_stop": (self.widget.el_stop_dsb, 90, float),
            "el_step": (self.widget.el_step_dsb, 1, float),
        }
        CONF.register_widgets(widget_map)

    def on_cal_browse_btn_pressed(self) -> None:
        fname, _ = QFileDialog.getOpenFileName(self, "Open Calibration File", filter="Calibration File (*.pycal)")
        if fname == "":
            return

        self.load_cal(fname)

    @property
    def polarizations(self) -> list[tuple[str, int, int]]:
        return [
            (self.widget.pol1_le.text(), *self.widget.pol1_cb.currentData()),
            (self.widget.pol2_le.text(), *self.widget.pol2_cb.currentData()),
        ]

    def update_params(self, params: list[tuple[int, int]]) -> None:
        param_strs = [f"S{a}{b}" for a, b in params]
        self.widget.pol1_cb.clear()
        self.widget.pol2_cb.clear()

        for param_str, param in zip(param_strs, params, strict=True):
            self.widget.pol1_cb.addItem(param_str, userData=param)
            self.widget.pol2_cb.addItem(param_str, userData=param)

    def run_cal_wizard(self) -> None:
        analyzer = QApplication.activeWindow().analyzer
        if analyzer is None:
            QMessageBox.warning(
                self, "No Analyzer", "You must be connected to an analyzer to run the Calibration Wizard"
            )
            return
        self.cal_wizard = CalWizard(analyzer, self)
        self.cal_wizard.exec()

        if self.cal_wizard.ref_ntwk is None:
            return

        self.load_cal(self.cal_wizard.cal_path)

    def load_cal(self, path: str | Path) -> None:
        try:
            self.cal = Calibration.load(path)
        except Exception:
            QMessageBox.warning(self, "Invalid Calibration File", f"{path} is not a valid calibration file")
            return

        self.widget.cal_file_le.setText(str(path))
        self.widget.cal_file_toggle.setEnabled(True)
        self.widget.cal_file_toggle.setChecked(True)
        self.widget.view_cal_btn.setEnabled(True)

    def view_cal(self) -> None:
        self.view_dlg = CalViewDialog(self.cal, self)
        self.view_dlg.exec()
