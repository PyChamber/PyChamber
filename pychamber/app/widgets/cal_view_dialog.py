from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

import numpy as np
import pyqtgraph as pg
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QTableWidgetItem

from pychamber.app.logger import LOG
from pychamber.app.ui.cal_view_dlg import Ui_CalViewDialog
from pychamber.calibration import Calibration


class CalViewDialog(QDialog, Ui_CalViewDialog):
    def __init__(self, calibration: Calibration, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        LOG.debug("Launching calibration view dialog")
        self.setupUi(self)

        self.cal = calibration
        self.postvisible_setup()

    def postvisible_setup(self) -> None:
        self.pens = [pg.mkPen((143, 175, 217), width=3), pg.mkPen((255, 212, 59), width=3)]
        self.cal_plot.setBackground("#ffffff")
        self.cal_plot.setLabel("left", "Loss", units="dB")
        self.cal_plot.setLabel("bottom", "Frequency", units="Hz")
        self.cal_plot.getPlotItem().showGrid(True, True)
        self.cal_plot.getPlotItem().addLegend(brush=(240, 240, 240), pen=(120, 120, 120), labelTextColor=(0, 0, 0))

        self.plot_polarizations()
        self.update_table()
        self.update_notes()

    def plot_polarizations(self) -> None:
        LOG.debug("Plotting polarizations")
        for i, pol in enumerate(self.cal.networks):
            self.cal_plot.plot(pol.f, -1 * pol.s_db.flatten(), pen=self.pens[i], name=pol.name)

    def update_table(self) -> None:
        LOG.debug("Updating table")
        s_dbs = np.array([ntwk.s_db for ntwk in self.cal.networks])
        s_dbs = s_dbs.reshape((len(s_dbs), -1))
        vals = np.vstack((self.cal.frequency.f, s_dbs)).T
        self.cal_table.setColumnCount(len(vals.T))
        self.cal_table.setHorizontalHeaderLabels(["Frequency", *self.cal.polarizations])
        for row in vals:
            row_pos = self.cal_table.rowCount()
            self.cal_table.insertRow(row_pos)
            for j, col in enumerate(row):
                self.cal_table.setItem(row_pos, j, QTableWidgetItem(f"{col:.3f}"))
                item = self.cal_table.item(row_pos, j)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def update_notes(self) -> None:
        LOG.debug("Updating notes")
        self.notes_pte.setPlainText(self.cal.notes)
        self.notes_pte.setReadOnly(True)
