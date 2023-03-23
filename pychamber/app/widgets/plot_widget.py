import pyqtgraph as pg
from pyqtgraph import dockarea
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from ..ui.plot_widget import Ui_PlotWidget
from .new_plot_dlg import NewPlotDialog
from .custom_dock_label import CustomDockLabel
from .polar_plot import PolarPlotWidget
from pychamber.experiment_result import ExperimentResult

class PlotWidget(QMainWindow, Ui_PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        self.setupUi(self)

        self.results = None
        self.plots = []
        self.new_plot_dlg = NewPlotDialog(self)

        self.add_polar_action.triggered.connect(self.add_polar_plot)
        self.add_cart_action.triggered.connect(self.add_cartesian_plot)

    def update_data(self, results: ExperimentResult) -> None:
        self.results = results
        self.update_all_plots()

    def update_all_plots(self) -> None:
        if self.results is None:
            return

    def add_plot(
            self, 
            plot_widget, 
            title: str = "",
            label_color: str = "#00cc00",
            plot_bg_color: str = "#DDDDDD"
        ) -> None:
        label = CustomDockLabel(title, fontSize="16px", background_color=label_color)
        d = dockarea.Dock(name=None, label=label, size=(1, 1), autoOrientation=False)
        d.setOrientation("horizontal")
        self.dock_area.addDock(d, "below")
        w = plot_widget(title=label)
        w.setBackground(plot_bg_color)
        d.addWidget(w)

        self.plots.append(w)

    def add_polar_plot(self, **kwargs) -> None:
        self.new_plot_dlg.exec()
        self.add_plot(PolarPlotWidget, **kwargs)

    def add_cartesian_plot(self, **kwargs) -> None:
        self.new_plot_dlg.exec()
        self.add_plot(pg.PlotWidget, **kwargs)
