from __future__ import annotations

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide6.QtWidgets import QDialog, QWidget

from ..ui.new_plot_dlg import Ui_NewPlotDialog


class NewPlotDialog(QDialog, Ui_NewPlotDialog):
    default_bg_color = "#DDDDDD"
    default_label_color = "#00CC00"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.bg_color_btn.color = self.default_bg_color

        self.connect_signals()

    def connect_signals(self) -> None:
        self.plot_type_cb.currentTextChanged.connect(lambda text: self.plot_pg_gb.setTitle(f"{text} Plot Settings"))

    @property
    def title(self) -> str:
        t = self.title_le.text()
        return t if t != "" else "Plot"

    def construct_widget(self, parent: QWidget | None = None) -> pg.PlotWidget | gl.GLViewWidget | None:
        plot_ctrl_idx = self.plot_controls.currentIndex()
        if plot_ctrl_idx == 0:
            return None

        plot_ctrl_widget = self.plot_controls.currentWidget().children()[1]
        widget = plot_ctrl_widget.create_plot(parent)
        if not isinstance(widget, gl.GLViewWidget):
            widget.getPlotItem().setTitle(self.title)

        return widget
