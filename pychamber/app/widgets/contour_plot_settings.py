import pyqtgraph as pg
from PySide6.QtWidgets import QWidget

from ..ui.contour_plot_settings import Ui_ContourPlotSettings


class ContourPlotSettings(QWidget, Ui_ContourPlotSettings):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

    def create_plot(self, parent: QWidget | None = None) -> pg.PlotWidget:
        return pg.PlotWidget(parent=parent)
