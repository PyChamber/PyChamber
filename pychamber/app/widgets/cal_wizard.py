from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

import functools
from pathlib import Path

import numpy as np
import pyqtgraph as pg
import skrf
from qtpy.QtWidgets import QFileDialog, QWizard

from pychamber.app.ui.cal_wizard import Ui_CalWizard
from pychamber.calibration import Calibration


class CalWizard(QWizard, Ui_CalWizard):
    def __init__(self, analyzer: skrf.vi.VNA, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.analyzer = analyzer
        self.postvisible_setup()
        self.connect_signals()

    def postvisible_setup(self) -> None:
        self.ref_pen = pg.mkPen((90, 94, 120), width=3)
        self.loss_pens = [pg.mkPen((143, 175, 217), width=3), pg.mkPen((255, 212, 59), width=3)]

        self.ref_ntwk: skrf.Network | None = None
        self.losses: list[skrf.Network] = [skrf.Network() for _ in range(2)]
        self.cal_saved = False

        self.loss_plotitems = []
        self.loss_plotitems.extend([self.loss_plot.plot() for _ in range(2)])

        self.reference_pg.isComplete = lambda: self.ref_ntwk is not None
        self.cal_pg.isComplete = lambda: self.cal_saved

        self.ref_ant_plot.setBackground("#ffffff")
        self.ref_ant_plot.setLabel("left", "Magnitude", units="dB")
        self.ref_ant_plot.setLabel("bottom", "Frequency", units="Hz")
        self.ref_ant_plot.getPlotItem().showGrid(True, True)

        self.loss_plot.setBackground("#ffffff")
        self.loss_plot.setLabel("left", "Loss", units="dB")
        self.loss_plot.setLabel("bottom", "Frequency", units="Hz")
        self.loss_plot.getPlotItem().showGrid(True, True)
        self.loss_plot.getPlotItem().addLegend(brush=(240, 240, 240), pen=(120, 120, 120), labelTextColor=(0, 0, 0))

    def connect_signals(self) -> None:
        self.ref_ant_browse_btn.pressed.connect(self.load_ref_antenna)
        self.meas_pol1_btn.pressed.connect(functools.partial(self.measure_polarization, 1))
        self.meas_pol2_btn.pressed.connect(functools.partial(self.measure_polarization, 2))
        self.save_cal_btn.pressed.connect(self.save_cal)
        self.pol1_cb.currentTextChanged.connect(lambda text: self.meas_pol1_btn.setEnabled(text != ""))
        self.pol2_cb.currentTextChanged.connect(lambda text: self.meas_pol2_btn.setEnabled(text != ""))

    def load_ref_antenna(self) -> None:
        fname, _ = QFileDialog.getOpenFileName(self, "Open File")
        if fname == "":
            return

        fpath = Path(fname)
        self.ref_ant_label.setText(fpath.name)

        csv = np.genfromtxt(fpath, delimiter=",")
        csv = csv[csv[:, 0].argsort()]
        freqs = csv[:, 0] * 1e9
        mags_db = csv[:, 1]
        mags_lin = 10 ** (mags_db / 20)

        self.ref_ant_plot.plot(freqs, mags_db, pen=self.ref_pen)
        self.ref_ntwk = skrf.Network(frequency=skrf.Frequency.from_f(freqs, unit="Hz"), s=mags_lin.reshape(-1, 1, 1))
        self.ref_ntwk.name = fpath.name
        self.reference_pg.completeChanged.emit()

    def measure_polarization(self, polarization: int) -> None:
        msmnt_name = "PYCHAMBER_TEMP"
        msmnt_param = self.pol1_cb.currentText() if polarization == 1 else self.pol2_cb.currentText()
        self.analyzer.create_measurement(msmnt_name, msmnt_param)
        ntwk = self.analyzer.get_data(msmnt_name)
        self.analyzer.delete_measurement(msmnt_name)

        loss = self.calc_loss(ntwk)
        pol_name = self.pol1_le.text() if polarization == 1 else self.pol2_le.text()
        loss.params = {"polarization": pol_name}
        loss.name = pol_name

        self.losses[polarization] = loss
        self.loss_plotitems[polarization].setData(loss.f, -1 * loss.s_db.flatten(), pen=self.loss1_pen, name=pol_name)
        self.loss_plot.getPlotItem().legend.removeItem(self.loss_plotitems[polarization])
        self.loss_plot.getPlotItem().legend.addItem(self.loss_plotitems[polarization], pol_name)

        self.save_cal_btn.setEnabled(True)

    def calc_loss(self, ntwk: skrf.Network) -> skrf.Network:
        ref = self.ref_ntwk
        if len(self.ref_ntwk) != len(ntwk):
            ref = ref.interpolate(ntwk.frequency)
            self.ref_ntwk = ref

        return ntwk / ref

    def save_cal(self) -> None:
        fname, _ = QFileDialog.getSaveFileName(self, "Save Calibration", filter="Calibration File (*.pycal)")
        if fname == "":
            return

        self.cal_path = Path(fname).with_suffix(".pycal")
        notes = [
            "Calibration Notes:@",
            # read_mdif includes all lines starting with !, but we only
            # want our notes when we load later. So we introduce our
            # own delimiter
            *(f"{line}@" for line in self.notes_pte.toPlainText().split("\n")),
        ]
        cal = Calibration([self.pol1_loss, self.pol2_loss], notes=notes)
        cal.save(self.cal_path)

        self.cal_saved = True
        self.cal_pg.completeChanged.emit()
