"""Defines several useful plots to use throughout PyChamber.

isort:skip_file
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from matplotlib.pyplot import Line2D

from dataclasses import dataclass
from math import floor, ceil
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

import matplotlib
import numpy as np

from pychamber.logger import LOG

matplotlib.use('QT5Agg')


@dataclass
class PlotLimits:
    """Contains the plot's view limits."""

    min_: float
    max_: float
    step: float


class MplCanvas(Canvas):
    """A matplotlib canvas containing a figure."""

    def __init__(self):
        """Create the canvas."""
        self.fig = Figure()
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


class MplWidget(QWidget):
    """Base class of plot widgets.

    An MplWidget contains a list of artists which draw the actual lines in a
    plot.

    Attributes:
        artists: list of matplotlib artists
        autoscaled: Signal raised when a plot is autoscaled. Used to alert the
            containing widget if it needs to change it's plot limit controls
    """

    artists: List[Line2D]
    autoscaled = pyqtSignal(object)

    def __init__(self, parent=None):
        """Create the plot.

        Arguments:
            parent: the parent QWidget
        """
        LOG.debug("Creating plot...")
        super().__init__(parent)

        self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(policy)

        self._autoscale: bool = False

    # def sizeHint(self) -> QSize:
    #     return QSize(300, 300)

    def reset_plot(self) -> None:
        """Remove all lines and reset data.

        Sets artists to a single-element list of an empty Line2D.
        """
        for artist in self.artists:
            artist.remove()
        self.artists = self.ax.plot(np.array([]), np.array([]))
        self.update_scale()

    def update_scale(self) -> None:
        """Updates the plot scale from the classes scale attributes.

        Warning:
            Must be implemented by subclass.
        """
        ...

    @property
    def autoscale(self) -> bool:
        """If the plot is set to autoscale.

        Returns:
            bool: if autoscale is enabled
        """
        return self._autoscale

    @autoscale.setter
    def autoscale(self, set: bool) -> None:
        """Sets autoscaling and autoscales the plot if it was enabled.

        Arguments:
            set: True to turn on, False to turn off
        """
        self._autoscale = set
        self.autoscale_plot()

    def autoscale_plot(self) -> None:
        """Autoscales the plot based on the existing data.

        Warning:
            Must be implemented by subclass
        """
        ...

    def redraw_plot(self) -> None:
        """Refresh the plot. Useful when autoscaling."""
        for artist in self.artists:
            xdata = artist.get_xdata()
            ydata = artist.get_ydata()

            artist.set_xdata(xdata)
            artist.set_ydata(ydata)

        self.canvas.draw()

    def plot_new_data(self, xdata: np.ndarray, ydata: np.ndarray, plot: int = 0) -> None:
        """Plots new data as opposed to appending a new piece of data.

        Arguments:
            xdata: the xdata of the plot (as defined by the projection)
            ydata: the ydata of the plot (as defined by the projection)
            plot: the plot to change the data for. Can be used when displaying
                multiple lines on a single plot
        """
        self.artists[plot].set_xdata(xdata)
        self.artists[plot].set_ydata(ydata)

        if self.autoscale:
            self.autoscale_plot()
        else:
            self.canvas.draw()

    def update_plot(self, xdata: np.ndarray, ydata: np.ndarray, plot: int = 0) -> None:
        """Append new data to a plot and redraw.

        Adds new data to a plot. Can be a single piece of data or multiple. Must
        be the same length!

        Arguments:
            xdata: the new piece of xdata of the plot
            ydata: the new piece of ydata of the plot
            plot: the plot to add the data to. Can be used when displaying
                multiple lines on a single plot
        """
        self.artists[plot].set_xdata(np.append(self.artists[plot].get_xdata(), xdata))
        self.artists[plot].set_ydata(np.append(self.artists[plot].get_ydata(), ydata))
        if self.autoscale:
            self.autoscale_plot()

        self.canvas.draw()

    def add_plot(self, xdata: np.ndarray, ydata: np.ndarray) -> None:
        """Add a new line to the plot.

        Arguments:
            xdata: x data of new line
            ydata: y data of new line
        """
        artist, *_ = self.ax.plot(xdata, ydata)
        self.artists.append(artist)
        self.redraw_plot()


class MplRectWidget(MplWidget):
    """A rectangular plot."""

    def __init__(self, parent=None):
        """Create a rectangular plot.

        Arguments:
            parent: parent QWidget
        """
        super().__init__(parent)

        self.ax = self.canvas.fig.add_subplot()
        self.artists = self.ax.plot(np.array([0]), np.array([0]))
        self.ax.grid(True)

        self._xmin = 0
        self._xmax = 1

        self._ymin = -30
        self._ymax = 0
        self._ystep = 10

    @property
    def xmin(self) -> int:
        """Minimum x value."""
        return self._xmin

    @xmin.setter
    def xmin(self, val: int) -> None:
        self._xmin = val
        self.update_scale()

    @property
    def xmax(self) -> int:
        """Maximum x value."""
        return self._xmax

    @xmax.setter
    def xmax(self, val: int) -> None:
        self._xmax = val
        self.update_scale()

    @property
    def ymin(self) -> int:
        """Minimum y value."""
        return self._ymin

    @ymin.setter
    def ymin(self, val: int) -> None:
        self._ymin = val
        self.update_scale()

    @property
    def ymax(self) -> int:
        """Maximum y value."""
        return self._ymax

    @ymax.setter
    def ymax(self, val: int) -> None:
        self._ymax = val
        self.update_scale()

    @property
    def ystep(self) -> int:
        """Y step. (Distance between y-lines)."""
        return self._ystep

    @ystep.setter
    def ystep(self, val: int) -> None:
        self._ystep = val
        self.update_scale()

    def autoscale_plot(self) -> None:
        """Autoscale the y-limits."""
        if len(y := self.artists[0].get_ydata()) > 0:
            self._ymin = floor(min(y))
            self._ymax = ceil(max(y))
            self.update_scale()
            self.autoscaled.emit(PlotLimits(self.ymin, self.ymax, self.ystep))

    def set_xlabel(self, label: str) -> None:
        """Set the x label."""
        self.ax.set_xlabel(label)

    def set_ylabel(self, label: str) -> None:
        """Set the y label."""
        self.ax.set_ylabel(label)

    def set_title(self, title: str) -> None:
        """Set the plot title."""
        self.ax.set_title(title)

    def update_scale(self) -> None:
        """Update the scale to match the class attributes.

        Scaling works by setting the class variables then calling this function.
        """
        self.ax.set_xbound(self._xmin, self._xmax)
        self.ax.set_xticks(np.linspace(self._xmin, self._xmax, 6))
        self.ax.set_ybound(self._ymin, self._ymax)
        self.ax.set_yticks(np.arange(self._ymin, self._ymax, self._ystep))
        self.redraw_plot()


class MplPolarWidget(MplWidget):
    """A polar plot."""

    def __init__(self, parent=None):
        """A polar plot."""
        super().__init__(parent)

        self.ax = self.canvas.fig.add_subplot(projection='polar')
        self.ax.set_theta_zero_location('N')
        self.ax.set_thetagrids(np.arange(0, 360, 30))
        self.artists = self.ax.plot(np.array([]), np.array([]))

        self.ax.set_xticks(np.deg2rad(np.arange(-180, 180, 30)))
        self.ax.set_thetalim(-np.pi, np.pi)

        self.canvas.draw()

        self._rmin = -30
        self._rmax = 0
        self._rstep = 10

    @property
    def rmin(self) -> int:
        """Minimum r value."""
        return self._rmin

    @rmin.setter
    def rmin(self, val: int) -> None:
        self._rmin = val
        self.update_scale()

    @property
    def rmax(self) -> int:
        """Maximum r value."""
        return self._rmax

    @rmax.setter
    def rmax(self, val: int) -> None:
        self._rmax = val
        self.update_scale()

    @property
    def rstep(self) -> int:
        """R step size."""
        return self._rstep

    @rstep.setter
    def rstep(self, val: int) -> None:
        self._rstep = val
        self.update_scale()

    def autoscale_plot(self) -> None:
        """Autoscale the plot to fit r values."""
        if len(y := self.artists[0].get_ydata()) > 0:
            self._rmin = floor(min(y))
            self._rmax = ceil(max(y))
            self.update_scale()
            self.autoscaled.emit(PlotLimits(self.rmin, self.rmax, self.rstep))

    def update_scale(self) -> None:
        """Update the scale to match the class attributes.

        Scaling works by setting the class variables then calling this function.
        """
        self.ax.set_rlim(self._rmin, self._rmax)
        self.ax.set_rticks(np.arange(self._rmin, self._rmax, self._rstep))
        self.redraw_plot()
