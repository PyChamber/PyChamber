"""Qt5 MatPlotLib Widget.

    isort:skip_file
"""

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.ticker import EngFormatter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from pychamber.logger import log

matplotlib.use('QT5Agg')


class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


class MplWidget(QWidget):
    def __init__(self, color: str, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

        self._grid = True
        self.color = color

    @property
    def grid(self) -> bool:
        return self._grid

    @grid.setter
    def grid(self, setting: bool) -> None:
        self._grid = setting

    def sizeHint(self) -> QSize:
        return QSize(300, 300)


class MplRectWidget(MplWidget):
    def __init__(self, color: str, parent=None):
        super(MplRectWidget, self).__init__(color, parent)

        self.ax = self.canvas.fig.add_subplot()
        self.artist, *_ = self.ax.plot(np.array([0]), np.array([0]), color=self.color)
        self.ax.grid(self.grid)
        self.xformatter = EngFormatter(unit='Hz')
        self.xtitle = ""
        self.ytitle = ""

        # Semi-sensible defaults
        self.ymin = -30.0
        self.ymax = 0.0
        self.ystep = 10.0

    def update_plot(self, xdata: np.ndarray, ydata: np.ndarray) -> None:
        self.ax.cla()
        self.artist, *_ = self.ax.plot(xdata, ydata, color=self.color)
        self.ax.grid(self.grid)
        self.ax.xaxis.set_major_formatter(self.xformatter)
        if len(xdata) > 1:
            self.ax.set_xlim(np.amin(xdata), np.amax(xdata))
        self.ax.set_xlabel(self.xtitle)
        self.ax.set_ylabel(self.ytitle)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_yticks(np.arange(self.ymin, self.ymax + 1, self.ystep))
        self.canvas.draw()

    def refresh_plot(self) -> None:
        x = self.artist.get_xdata(orig=True)
        y = self.artist.get_ydata(orig=True)
        self.update_plot(x, y)

    def auto_scale(self) -> None:
        y = self.artist.get_ydata(orig=True)
        if len(y) <= 1:
            return
        min_ = np.floor(np.amin(y))
        max_ = np.ceil(np.amax(y))
        step = np.round((max_ - min_) / 4)
        self.set_scale(min_, max_, step)  # type: ignore

    def set_scale_min(self, min: float) -> None:
        self.ymin = min
        self.refresh_plot()

    def set_scale_max(self, max: float) -> None:
        self.ymax = max
        self.refresh_plot()

    def set_scale_step(self, step: float) -> None:
        self.ystep = step
        self.refresh_plot()

    def set_scale(self, min: float, max: float, step: float) -> None:
        self.ymin = min
        self.ymax = max
        self.ystep = step
        self.refresh_plot()

    def set_xtitle(self, text: str) -> None:
        self.xtitle = text

    def set_ytitle(self, text: str) -> None:
        self.ytitle = text


class MplPolarWidget(MplWidget):
    def __init__(self, color: str, parent=None):
        super(MplPolarWidget, self).__init__(color, parent)

        self._ticks = True
        # Semi-sensible defaults
        self.rmin = -30.0
        self.rmax = 0.0
        self.rstep = 10.0

        self.ax = self.canvas.fig.add_subplot(projection='polar')
        self.ax.set_theta_zero_location('N')
        self.ax.set_thetagrids(np.arange(0, 360, 30))
        self.artist, *_ = self.ax.plot(np.array([0]), np.array([0]), color=self.color)
        self.canvas.draw()

    @property
    def ticks(self) -> bool:
        return self._ticks

    @ticks.setter
    def ticks(self, setting: bool) -> None:
        self._ticks = setting

    def update_plot(self, xdata: np.ndarray, ydata: np.ndarray) -> None:
        thetas = np.hstack((self.artist.get_xdata(orig=True), xdata))
        rs = np.hstack((self.artist.get_ydata(orig=True), ydata))

        self.artist.set_data(thetas, rs)
        self.canvas.draw()

    def refresh_plot(self) -> None:
        x = self.artist.get_xdata(orig=True)
        y = self.artist.get_ydata(orig=True)
        self.update_plot(x, y)

    def auto_scale(self) -> None:
        y = self.artist.get_ydata(orig=True)
        if len(y) <= 1:
            return
        min_ = np.floor(np.amin(y))
        max_ = np.ceil(np.amax(y))
        step = np.round((max_ - min_) / 4)
        self.set_scale(min_, max_, step)  # type: ignore

    def set_scale_min(self, min: float) -> None:
        self.rmin = min
        self.refresh_plot()

    def set_scale_max(self, max: float) -> None:
        self.rmax = max
        self.refresh_plot()

    def set_scale_step(self, step: float) -> None:
        self.rstep = step
        self.refresh_plot()

    def set_scale(self, min: float, max: float, step: float) -> None:
        self.rmin = min
        self.rmax = max
        self.rstep = step if not np.isclose(step, 0.0) else 1.0
        self.refresh_plot()


class Mpl3DWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
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
