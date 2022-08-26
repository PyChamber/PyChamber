"""Defines the PlotsPlugin.

This is a TabWidget with different plots available. Eventually, the goal is to
have a list of available plots the user can drag and drop into the widget to add
different plots.
"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type
    from pychamber.main_window import MainWindow

import skrf
from PyQt5.QtCore import QStringListModel, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout

from pychamber.logger import LOG
from pychamber.plugins import ExperimentPlugin, PyChamberPlugin
from pychamber.ui import size_policy

from .over_freq import OverFreqPlot
from .polar import PolarPlot
from .pychamber_plot import PlotControls, PyChamberPlot
from .rectangular import RectangularPlot


class PlotsPlugin(PyChamberPlugin):
    """The Plots plugin.

    Attributes:
        new_data_requested: Signal raised when a plot's controls are changed and
            it needs new data
    """

    NAME = "plots"
    CONFIG: Dict = {}

    new_data_requested = pyqtSignal(object)

    def __init__(self, parent: MainWindow) -> None:
        """Instantiate the plugin.

        Arguments:
            parent: the PyChamber main window
        """
        super().__init__(parent)

        self.setObjectName('plots')
        self.setLayout(QVBoxLayout())
        self.setSizePolicy(size_policy["PREF_PREF"])
        self.setMinimumSize(600, 600)

        self._plots: List[PyChamberPlot] = []
        self._pol_model: QStringListModel = QStringListModel([], self)

        self.experiment: Optional[ExperimentPlugin] = None

    @property
    def plots(self) -> List[PyChamberPlot]:
        """Get the currently existing plots."""
        return self._plots

    def set_polarizations(self, pols: List[str]) -> None:
        """Set the names of the polarizations.

        Plots with polarization settings all connect to the plugin's
        polarzation ListModel.
        """
        self._pol_model.setStringList(pols)

    def _setup(self) -> None:
        LOG.debug("Creating Plots widget...")
        self.tab_widget = QTabWidget(self)
        self.layout().addWidget(self.tab_widget)

        self.experiment = cast(ExperimentPlugin, self.main.get_plugin("experiment"))
        self.experiment.ntwk_model.data_loaded.connect(self._on_data_loaded)

        # TODO: Make this dynamic for users to be able to add desired plots
        self.add_plot(PolarPlot, "Polar Plot")
        self.add_plot(RectangularPlot, "Rectangular Plot")
        self.add_plot(OverFreqPlot, "Over Frequency Plot")
        # self.add_plot(ThreeDPlot, "3D Plot")

    def _post_visible_setup(self) -> None:
        for plot in self._plots:
            plot.post_visible_setup()
            plot.new_data_requested.connect(self._on_new_data_requested)

    def _on_new_data_requested(self, ctrls: PlotControls) -> None:
        assert self.experiment is not None
        plot = cast(PyChamberPlot, self.sender())
        LOG.debug(f"Getting new data from {plot} with controls {ctrls}")
        ntwk_set = self.experiment.ntwk_model.get_data(**dataclasses.asdict(ctrls))
        if len(ntwk_set) == 0:
            return
        plot.plot_new_data(ntwk_set)

    def _on_data_loaded(self) -> None:
        LOG.debug("Loaded data")
        assert self.experiment is not None
        ntwk_model = self.experiment.ntwk_model
        for plot in self._plots:
            plot.blockSignals(True)

        self.set_polarizations(ntwk_model.polarizations)
        LOG.debug(f"{ntwk_model.azimuths=}")
        LOG.debug(f"{ntwk_model.elevations=}")
        self.init_plots(
            frequencies=ntwk_model.frequencies,
            azimuths=ntwk_model.azimuths,
            elevations=ntwk_model.elevations,
        )
        for plot in self._plots:
            plot.blockSignals(False)

        for plot in self._plots:
            plot._send_controls_state()
            plot.autoscale()

    def init_plots(self, **kwargs) -> None:
        """Initialize all existing plots."""
        for plot in self._plots:
            plot.init_controls(**kwargs)
            plot.reset()

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        """Receive new data and update existing plots.

        Arguments:
            ntwk: Network representing new data. Plots are responsible for
                deciding if the data is relevant to their current configuration
        """
        for plot in self._plots:
            plot.rx_updated_data(ntwk)

    def add_plot(self, plot_type: Type, tab_name: str) -> None:
        """Add a new plot widget.

        Arguments:
            plot_type: the type of plot. Should be of type PyChamberPlot
            tab_name: the name to be assigned to the tab the plot lives in
        """
        plot_widget = plot_type(self.tab_widget)
        plot_widget.setup()
        plot_widget.set_polarization_model(self._pol_model)

        self._plots.append(plot_widget)
        self.tab_widget.addTab(plot_widget, tab_name)

    def reset_plots(self) -> None:
        """Reset all plots."""
        for plot in self._plots:
            plot.reset()
