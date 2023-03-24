from pyqtgraph import dockarea
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from pychamber.experiment_result import ExperimentResult

from ..ui.plot_widget import Ui_PlotWidget
from .custom_dock_label import CustomDockLabel
from .new_plot_dlg import NewPlotDialog


class PlotWidget(QMainWindow, Ui_PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)
        self.setupUi(self)

        self.results = None
        self.plots = []
        self.new_plot_dlg = NewPlotDialog(self)

        self.add_plot_action.triggered.connect(self.add_plot)

    def update_data(self, results: ExperimentResult) -> None:
        self.results = results
        self.update_all_plots()

    def update_all_plots(self) -> None:
        if self.results is None:
            return

    def add_plot(
        self,
    ) -> None:
        res = self.new_plot_dlg.exec()
        if res == 0:
            return
        widget = self.new_plot_dlg.construct_widget()
        if widget is None:
            return

        label = CustomDockLabel(self.new_plot_dlg.title, fontSize="16px", background_color="#00CC00")
        dock = dockarea.Dock(name=None, label=label, size=(1, 1), autoOrientation=False)
        dock.setOrientation("horizontal")
        dock.addWidget(widget)
        self.dock_area.addDock(dock, "below")

        self.plots.append(widget)
