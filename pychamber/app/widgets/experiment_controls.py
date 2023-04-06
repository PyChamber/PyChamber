import functools
from operator import setitem
from pathlib import Path

from qtpy.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget

from pychamber.app.logger import LOG
from pychamber.app.ui.experiment_widget import Ui_ExperimentWidget
from pychamber.calibration import Calibration
from pychamber.settings import CONF

from .cal_view_dialog import CalViewDialog
from .cal_wizard import CalWizard


class ExperimentControls(QWidget, Ui_ExperimentWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        LOG.debug("Creating ExperimentControls")
        self.setupUi(self)

        self.postvisible_setup()
        self.connect_signals()

    def connect_signals(self) -> None:
        LOG.debug("Connecting signals")
        self.phi_start_dsb.valueChanged.connect(functools.partial(setitem, CONF, "phi_start"))
        self.phi_stop_dsb.valueChanged.connect(functools.partial(setitem, CONF, "phi_stop"))
        self.phi_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "phi_step"))
        self.theta_start_dsb.valueChanged.connect(functools.partial(setitem, CONF, "theta_start"))
        self.theta_stop_dsb.valueChanged.connect(functools.partial(setitem, CONF, "theta_stop"))
        self.theta_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "theta_step"))
        self.pol1_le.textChanged.connect(functools.partial(setitem, CONF, "pol_1_label"))
        self.pol2_le.textChanged.connect(functools.partial(setitem, CONF, "pol_2_label"))
        self.cal_file_le.textChanged.connect(functools.partial(setitem, CONF, "cal_file"))
        self.cal_file_toggle.toggled.connect(functools.partial(setitem, CONF, "cal_on"))
        self.cal_file_browse_btn.pressed.connect(self.on_cal_browse_btn_pressed)
        self.cal_wizard_btn.pressed.connect(self.run_cal_wizard)
        self.view_cal_btn.pressed.connect(self.view_cal)

    def postvisible_setup(self) -> None:
        widget_map = {
            "phi_start": (self.phi_start_dsb, 0, float),
            "phi_stop": (self.phi_stop_dsb, 90, float),
            "phi_step": (self.phi_step_dsb, 1, float),
            "theta_start": (self.theta_start_dsb, 0, float),
            "theta_stop": (self.theta_stop_dsb, 90, float),
            "theta_step": (self.theta_step_dsb, 1, float),
            "pol_1_label": (self.pol1_le, "", str),
            "pol_2_label": (self.pol2_le, "", str),
            "cal_file": (self.cal_file_le, "", str),
            "cal_on": (self.cal_file_toggle, False, bool),
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
            (self.pol1_le.text(), *self.pol1_cb.currentData()),
            (self.pol2_le.text(), *self.pol2_cb.currentData()),
        ]

    def update_params(self, params: list[tuple[int, int]]) -> None:
        LOG.debug("Updating parameter comboboxes")
        param_strs = [f"S{a}{b}" for a, b in params]
        self.pol1_cb.clear()
        self.pol2_cb.clear()

        for param_str, param in zip(param_strs, params, strict=True):
            self.pol1_cb.addItem(param_str, userData=param)
            self.pol2_cb.addItem(param_str, userData=param)

    def run_cal_wizard(self) -> None:
        LOG.debug("Launching calibration wizard")
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
        LOG.debug("Loading calibration")
        try:
            self.cal = Calibration.load(path)
        except Exception:
            QMessageBox.warning(self, "Invalid Calibration File", f"{path} is not a valid calibration file")
            return

        self.cal_file_le.setText(str(path))
        self.cal_file_toggle.setEnabled(True)
        self.cal_file_toggle.setChecked(True)
        self.view_cal_btn.setEnabled(True)

    def view_cal(self) -> None:
        LOG.debug("Launching calibration view dialog")
        self.view_dlg = CalViewDialog(self.cal, self)
        self.view_dlg.exec()
