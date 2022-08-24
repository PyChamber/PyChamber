"""Qt5 MatPlotLib Widget.

    isort:skip_file
"""

from dataclasses import dataclass
from typing import Optional
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from pychamber.logger import log

matplotlib.use('QT5Agg')


@dataclass
class PlotLimits:
    min_: float
    max_: float
    step: float


class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


class MplWidget(QWidget):
    artist: plt.Line2D
    autoscaled = pyqtSignal(object)

    def __init__(self, parent=None):
        log.debug("Creating plot...")
        super().__init__(parent)

        self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(policy)

        self._grid = True

        self._autoscale: bool = False

    def reset_plot(self) -> None:
        ...

    def update_scale(self) -> None:
        ...

    @property
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, setting: bool) -> None:
        self._grid = setting

    @property
    def autoscale(self) -> bool:
        return self._autoscale

    @autoscale.setter
    def autoscale(self, set: bool) -> None:
        self._autoscale = set
        self.autoscale_plot()

    def autoscale_plot(self) -> None:
        ...

    def redraw_plot(self) -> None:
        xdata = self.artist.get_xdata()
        ydata = self.artist.get_ydata()

        self.artist.set_xdata(xdata)
        self.artist.set_ydata(ydata)

        self.canvas.draw()

    def plot_new_data(self, xdata: np.ndarray, ydata: np.ndarray) -> None:
        self.artist.set_xdata(xdata)
        self.artist.set_ydata(ydata)

        if self.autoscale:
            self.autoscale_plot()
        else:
            self.canvas.draw()

    def update_plot(self, xdata: np.ndarray, ydata: np.ndarray) -> None:
        self.artist.set_xdata(np.append(self.artist.get_xdata(), xdata))
        self.artist.set_ydata(np.append(self.artist.get_ydata(), ydata))
        if self.autoscale:
            self.autoscale_plot()

        self.canvas.draw()

    def sizeHint(self) -> QSize:
        return QSize(300, 300)


class MplRectWidget(MplWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ax = self.canvas.fig.add_subplot()
        self.artist, *_ = self.ax.plot(np.array([0]), np.array([0]))
        self.ax.grid(self.grid)

        self._xmin = 0
        self._xmax = 1

        self._ymin = -30
        self._ymax = 0
        self._ystep = 10

    @property
    def xmin(self) -> int:
        return self._xmin

    @xmin.setter
    def xmin(self, val: int) -> None:
        self._xmin = val
        self.update_scale()

    @property
    def xmax(self) -> int:
        return self._xmax

    @xmax.setter
    def xmax(self, val: int) -> None:
        self._xmax = val
        self.update_scale()

    @property
    def ymin(self) -> int:
        return self._ymin

    @ymin.setter
    def ymin(self, val: int) -> None:
        self._ymin = val
        self.update_scale()

    @property
    def ymax(self) -> int:
        return self._ymax

    @ymax.setter
    def ymax(self, val: int) -> None:
        self._ymax = val
        self.update_scale()

    @property
    def ystep(self) -> int:
        return self._ystep

    @ystep.setter
    def ystep(self, val: int) -> None:
        self._ystep = val
        self.update_scale()

    def autoscale_plot(self) -> None:
        if len(y := self.artist.get_ydata()) > 0:
            self._ymin = min(y)
            self._ymax = max(y)
            self.update_scale()
            self.autoscaled.emit(PlotLimits(self.ymin, self.ymax, self.ystep))

    def set_xlabel(self, label: str) -> None:
        self.ax.set_xlabel(label)

    def set_ylabel(self, label: str) -> None:
        self.ax.set_ylabel(label)

    def reset_plot(self) -> None:
        self.artist, *_ = self.ax.plot(np.array([]), np.array([]))
        self.update_scale()

    def update_scale(self) -> None:
        self.ax.set_xbound(self._xmin, self._xmax)
        self.ax.set_xticks(np.linspace(self._xmin, self._xmax, 6))
        self.ax.set_ybound(self._ymin, self._ymax)
        self.ax.set_yticks(np.arange(self._ymin, self._ymax, self._ystep))
        self.redraw_plot()


class MplPolarWidget(MplWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ax = self.canvas.fig.add_subplot(projection='polar')
        self.ax.set_theta_zero_location('N')
        self.ax.set_thetagrids(np.arange(0, 360, 30))
        self.artist, *_ = self.ax.plot(np.array([]), np.array([]))

        self.ax.set_xticks(np.deg2rad(np.arange(-180, 180, 30)))
        self.ax.set_thetalim(-np.pi, np.pi)

        self.canvas.draw()

        self._rmin = -30
        self._rmax = 0
        self._rstep = 10

    @property
    def rmin(self) -> int:
        return self._rmin

    @rmin.setter
    def rmin(self, val: int) -> None:
        self._rmin = val
        self.update_scale()

    @property
    def rmax(self) -> int:
        return self._rmax

    @rmax.setter
    def rmax(self, val: int) -> None:
        self._rmax = val
        self.update_scale()

    @property
    def rstep(self) -> int:
        return self._rstep

    @rstep.setter
    def rstep(self, val: int) -> None:
        self._rstep = val
        self.update_scale()

    def autoscale_plot(self) -> None:
        if len(y := self.artist.get_ydata()) > 0:
            self._rmin = min(y)
            self._rmax = max(y)
            self.update_scale()
            self.autoscaled.emit(PlotLimits(self.rmin, self.rmax, self.rstep))

    def reset_plot(self) -> None:
        self.artist, *_ = self.ax.plot(np.array([]), np.array([]))
        self.update_scale()

    def update_scale(self) -> None:
        self.ax.set_rlim(self._rmin, self._rmax)
        self.ax.set_rticks(np.arange(self._rmin, self._rmax, self._rstep))
        xdata = self.artist.get_xdata()
        ydata = self.artist.get_ydata()
        self.redraw_plot()


# TODO: 3D plotting needs some work...
class Mpl3DWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(policy)

        self.ax_lim = 0.5

        self.ax = self.canvas.fig.add_subplot(projection='3d')
        self.ax.grid(False)
        self.ax.set_axis_off()
        self.ax.set_proj_type('ortho')
        self.ax.view_init(elev=30, azim=45)
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_zlim(-1.5, 1.5)

        self.ax.quiver3D(0, 0, 0, self.ax_lim, 0, 0, length=1, colors='r', linewidth=3)
        self.ax.quiver3D(0, 0, 0, 0, self.ax_lim, 0, length=1, colors='g', linewidth=3)
        self.ax.quiver3D(0, 0, 0, 0, 0, self.ax_lim, length=1, colors='b', linewidth=3)
        self.ax.text3D(self.ax_lim, 0, 0, 'X', fontsize=14)
        self.ax.text3D(0, self.ax_lim, 0, 'Y', fontsize=14)
        self.ax.text3D(0, 0, self.ax_lim, 'Z', fontsize=14)
        plt.tight_layout()
        self.canvas.draw()

    def sizeHint(self) -> QSize:
        return QSize(500, 300)

    # https://stackoverflow.com/questions/54822873/python-plotting-antenna-radiation-pattern/63059296#63059296
    def update_plot(
        self, azimuths: np.ndarray, elevations: np.ndarray, mags: np.ndarray
    ) -> None:
        log.debug(f"{mags=}")
        mesh_az, mesh_el = np.meshgrid(azimuths, elevations)

        # normalize. 3D plots.....don't like negative radii
        mags = mags / np.max(mags)

        x = mags * np.sin(mesh_el) * np.cos(mesh_az)
        y = mags * np.sin(mesh_el) * np.sin(mesh_az)
        z = mags * np.cos(mesh_el)

        self.artist = self.ax.plot_surface(
            x, y, z, color='viridian', rstride=1, cstride=1, antialiased=True
        )
        self.canvas.draw()
