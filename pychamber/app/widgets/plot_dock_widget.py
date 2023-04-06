from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import contextlib

from pyqtgraph import dockarea
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMainWindow

from pychamber import ExperimentResult
from pychamber.app.logger import LOG

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
        LOG.debug("Creating PlotDockWidget")
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
        LOG.debug("Setting results")
        self._results = results
        for plot in self.plots:
            plot.data = results

    def add_polar_plot(self) -> None:
        LOG.debug("Adding polar plot")
        widget = PolarPlotWidget(self.results, title="Polar Plot")
        self.add_plot(widget)

    def add_rect_plot(self) -> None:
        LOG.debug("Adding rectangular plot")
        widget = RectPlotWidget(self.results, title="Rectangular Plot")
        self.add_plot(widget)

    def add_contour_plot(self) -> None:
        LOG.debug("Adding contour plot")
        widget = ContourPlotWidget(self.results, title="Contour Plot")
        self.add_plot(widget)

    def add_three_d_plot(self) -> None:
        LOG.debug("Adding 3D plot")
        widget = ThreeDPlotWidget(self.results, title="3D Plot")
        self.add_plot(widget)

    def add_plot(self, widget: PlotWidget) -> None:
        if widget is None:
            return

        label = CustomDockLabel(widget.title, fontSize="16px")
        widget.titleChanged.connect(lambda text: label.setText(" " if len(text) == 0 else text))
        dock = dockarea.Dock(name=None, label=label, size=(1, 1), autoOrientation=False)
        dock.setOrientation("horizontal")
        dock.addWidget(widget)
        last = next(self.dock_area.docks.values(), None)
        for _last in self.dock_area.docks.values():
            pass
        relative = last

        if relative is not None and relative.container() is None:
            relative = None

        self.dock_area.addDock(dock, "below", relativeTo=relative)

        dock.sigClosed.connect(lambda: self.remove_plot(widget))

        self.plots.append(widget)

    def remove_plot(self, plot):
        LOG.debug("Removing plot")
        with contextlib.suppress(ValueError):
            self.plots.remove(plot)
