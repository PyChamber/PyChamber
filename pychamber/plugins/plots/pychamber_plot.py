"""Defines the interface for plot tabs."""
from dataclasses import dataclass
from typing import Optional

import skrf
from PyQt5.QtCore import QStringListModel, pyqtSignal
from PyQt5.QtWidgets import QWidget

from pychamber.logger import LOG  # noqa: F401


@dataclass
class PlotControls:
    """Used to request new data."""

    polarization: str
    azimuth: Optional[float] = None
    elevation: Optional[float] = None


class PyChamberPlot(QWidget):
    """A plot.

    This defines the interface all plot widgets need to provide. This will
    enable us to implement drag/drop functionality in the future.

    Attributes:
        new_data_requested: Signal raised when the plot needs new data.
    """

    new_data_requested = pyqtSignal(PlotControls)

    def __init__(self, parent=None) -> None:
        """Instantiate the plot."""
        super().__init__(parent)

    def setup(self) -> None:
        """Perform all the necessary setup steps."""
        self._add_widgets()
        self._connect_signals()
        self.reset()

    def post_visible_setup(self) -> None:
        pass

    def autoscale(self) -> None:
        """Autoscale the plot."""
        ...

    def init_controls(self, **kwargs) -> None:
        """Initialize the control widgets to some state."""
        ...

    def set_polarization_model(self, model: QStringListModel) -> None:
        """If the plot contains a polarization control, this sets the model."""
        ...

    def reset(self) -> None:
        """Clear the plot and reset the controls."""
        ...

    def newfig(self) -> None:
        """Replace the figure. Used to apply new themes"""
        ...

    def _connect_signals(self) -> None:
        ...

    def _send_controls_state(self) -> None:
        ...

    def _add_widgets(self) -> None:
        ...

    def rx_updated_data(self, ntwk: skrf.Network) -> None:
        """Receive a new piece of data and add it to the plot.

        This function will decide if the data needs to be added to the plot
        based on the current controls state.

        Arguments:
            ntwk: the new piece of data to plot.
        """
        ...

    def plot_new_data(self, data: skrf.NetworkSet) -> None:
        """Clear the plot and plot new data e.g. when controls change.

        Arguments:
            data: the new data to plot
        """
        ...
