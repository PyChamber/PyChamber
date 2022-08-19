from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TYPE_CHECKING, List, Optional, Type
    from pychamber.main_window import MainWindow

import skrf
from PyQt5.QtCore import QStringListModel, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout

from pychamber.logger import log
from pychamber.plugins.base import PyChamberPlugin
from pychamber.ui import size_policy

from .over_freq import OverFreqPlot
from .polar import PolarPlot
from .pychamber_plot import PlotControls, PyChamberPlot
from .rectangular import RectangularPlot


class PlotsPlugin(PyChamberPlugin):
    new_data_requested = pyqtSignal(object)

    def __init__(self, parent: Optional[MainWindow] = None) -> None:
        super().__init__(parent)

        self.setObjectName('plots')
        self.setLayout(QVBoxLayout())
        self.setSizePolicy(size_policy["PREF_PREF"])
        self.setMinimumSize(600, 600)

        self._plots: List[PyChamberPlot] = []
        self._pol_model: QStringListModel = QStringListModel([], self)

    @property
    def plots(self) -> List[PyChamberPlot]:
        return self._plots

    def set_polarizations(self, pols: List[str]) -> None:
        self._pol_model.setStringList(pols)

    def setup(self) -> None:
        log.debug("Creating Plots widget...")
        self.tab_widget = QTabWidget(self)
        self.layout().addWidget(self.tab_widget)

        # TODO: Make this dynamic for users to be able to add desired plots
        self.add_plot(PolarPlot, "Polar Plot")
        self.add_plot(RectangularPlot, "Rectangular Plot")
        self.add_plot(OverFreqPlot, "Over Frequency Plot")
        # self.add_plot(ThreeDPlot, "3D Plot")

    def post_visible_setup(self) -> None:
        for plot in self._plots:
            plot.post_visible_setup()
            plot.new_data_requested.connect(self._on_new_data_requested)

    def _on_new_data_requested(self, ctrls: PlotControls) -> None:
        plot = self.sender()
        self.new_data_requested.emit((plot, ctrls))

    def init_plots(self, **kwargs) -> None:
        for plot in self._plots:
            plot.init_from_experiment(**kwargs)
            plot.reset()

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        for plot in self._plots:
            plot.rx_updated_data(ntwk)

    def add_plot(self, plot_type: Type, tab_name: str) -> None:
        plot_widget = plot_type(self.tab_widget)
        plot_widget.setup()
        plot_widget.set_polarization_model(self._pol_model)

        self._plots.append(plot_widget)
        self.tab_widget.addTab(plot_widget, tab_name)
