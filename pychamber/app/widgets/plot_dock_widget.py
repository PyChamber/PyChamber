from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import contextlib

from pyqtgraph import dockarea
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from pychamber import ExperimentResult

from ..ui.plot_widget import Ui_PlotWidget
from .contour_plot_settings import ContourPlotWidget
from .custom_dock_label import CustomDockLabel
from .plot_widget import PlotWidget
from .polar_plot_settings import PolarPlotWidget
from .rect_plot_settings import RectPlotWidget
from .three_d_plot_settings import ThreeDPlotWidget


# TODO: Look into RemoteGraphicsView
class PlotDockWidget(QMainWindow, Ui_PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        self.setupUi(self)

        self._results = None
        self.plots: list[PlotWidget] = []

        self.add_polar_action.triggered.connect(self.add_polar_plot)
        self.add_rect_action.triggered.connect(self.add_rect_plot)
        self.add_contour_action.triggered.connect(self.add_contour_plot)
        self.add_three_d_action.triggered.connect(self.add_three_d_plot)

    @property
    def results(self) -> ExperimentResult | None:
        return self._results

    @results.setter
    def results(self, results: ExperimentResult):
        self._results = results
        for plot in self.plots:
            plot.data = results

    def add_polar_plot(self) -> None:
        widget = PolarPlotWidget(self.results)
        self.add_plot(widget)

    def add_rect_plot(self) -> None:
        widget = RectPlotWidget(self.results)
        self.add_plot(widget)

    def add_contour_plot(self) -> None:
        widget = ContourPlotWidget(self.results)
        self.add_plot(widget)

    def add_three_d_plot(self) -> None:
        widget = ThreeDPlotWidget(self.results)
        self.add_plot(widget)

    def add_plot(self, widget: PlotWidget) -> None:
        if widget is None:
            return

        label = CustomDockLabel("Plot", fontSize="16px", background_color="#00CC00")
        dock = dockarea.Dock(name=None, label=label, size=(1, 1), autoOrientation=False)
        dock.setOrientation("horizontal")
        dock.addWidget(widget)
        self.dock_area.addDock(dock, "below")
        dock.sigClosed.connect(lambda: self.remove_plot(widget))

        self.plots.append(widget)

    def remove_plot(self, plot):
        with contextlib.suppress(ValueError):
            self.plots.remove(plot)
