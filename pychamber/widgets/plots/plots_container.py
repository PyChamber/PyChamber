from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TYPE_CHECKING, List, Optional, Type

import skrf
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from pychamber.logger import log
from pychamber.plugins.base import PyChamberPlugin
from pychamber.ui import size_policy

from .over_freq import OverFreqPlot
from .polar import PolarPlot
from .pychamber_plot import PyChamberPlot
from .rectangular import RectangularPlot
from .three_d import ThreeDPlot


class PlotsWidget(PyChamberPlugin):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName('plots')
        self.setLayout(QVBoxLayout())
        self.setSizePolicy(size_policy["PREF_PREF"])
        self.setMinimumSize(600, 600)

        self._plots: List[PyChamberPlot] = []

    @property
    def plots(self) -> List[PyChamberPlot]:
        return self._plots

    def setup(self) -> None:
        log.debug("Creating Plots widget...")
        self.tab_widget = QTabWidget(self)
        self.layout().addWidget(self.tab_widget)

        # TODO: Make this dynamic for users to be able to add desired plots
        self.add_plot(PolarPlot, "Polar Plot")
        self.add_plot(RectangularPlot, "Rectangular Plot")
        self.add_plot(OverFreqPlot, "Over Frequency Plot")
        self.add_plot(ThreeDPlot, "3D Plot")

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        for plot in self._plots:
            plot.rx_updated_data(ntwk)

    def add_plot(self, plot_type: Type, tab_name: str) -> None:
        plot_widget = plot_type(self.tab_widget)
        plot_widget.setup()

        self._plots.append(plot_widget)
        self.tab_widget.addTab(plot_widget, tab_name)
