import pyqtgraph as pg
from pyqtgraph import dockarea
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from ..ui.plot_widget import Ui_PlotWidget
from .custom_dock_label import CustomDockLabel
from .polar_plot import PolarPlotWidget


class PlotWidget(QMainWindow, Ui_PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        self.setupUi(self)

        self.add_polar_action.triggered.connect(self.add_polar_plot)
        self.add_cart_action.triggered.connect(self.add_cartesian_plot)

    def add_polar_plot(self) -> None:
        label = CustomDockLabel("Polar", fontSize="16px", background_color="#00cc00")
        d = dockarea.Dock(name=None, label=label, size=(1, 1), autoOrientation=False)
        d.setOrientation("horizontal")
        self.dock_area.addDock(d, "below")
        w = PolarPlotWidget(title="Polar")
        w.setBackground("#555555")
        d.addWidget(w)

    def add_cartesian_plot(self) -> None:
        label = CustomDockLabel("Cartesian", fontSize="16px", background_color="#00cc00")
        d = dockarea.Dock(name=None, label=label, size=(1, 1), autoOrientation=False)
        d.setOrientation("horizontal")
        self.dock_area.addDock(d, "below")
        w = pg.PlotWidget(title="Cartesian")
        w.setBackground("#555555")
        d.addWidget(w)
