"""Qt5 MatPlotLib Widget.

    isort:skip_file
"""

from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

import matplotlib
import numpy as np

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

    def blit(self) -> None:
        self.ax.draw_artist(self.artist)
        self.canvas.blit(self.canvas.fig.bbox)


class MplRectWidget(MplWidget):
    def __init__(self, color: str, parent=None):
        super(MplRectWidget, self).__init__(color, parent)

        self.ax = self.canvas.fig.add_subplot()
        self.artist, *_ = self.ax.plot(np.array([0]), np.array([0]), color=self.color)
        self.ax.grid(self.grid)
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Gain [dB]")
        self.canvas.draw()

    def update_plot(
        self, xdata: np.ndarray, ydata: np.ndarray, redraw: bool = False
    ) -> None:
        self.artist, *_ = self.ax.plot(xdata, ydata, color=self.color)
        self.blit()

    def update_scale(self) -> None:
        x = self.artist.get_xdata(orig=True)
        y = self.artist.get_ydata(orig=True)
        self.ax.cla()
        self.artist, *_ = self.ax.plot(x, y, color=self.color)
        self.ax.grid(self.grid)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_yticks(np.arange(self.ymin, self.ymax + 1, self.ystep))
        self.canvas.draw()

    def set_scale_min(self, min: float) -> None:
        self.ymin = min
        self.update_scale()

    def set_scale_max(self, max: float) -> None:
        self.ymax = max
        self.update_scale()

    def set_scale_step(self, step: float) -> None:
        self.ystep = step
        self.update_scale()

    def set_scale(self, min: float, max: float, step: float) -> None:
        self.ymin = min
        self.ymax = max
        self.ystep = step
        self.update_scale()


class MplPolarWidget(MplWidget):
    def __init__(self, color: str, parent=None):
        super(MplPolarWidget, self).__init__(color, parent)

        self._ticks = True

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

    def update_plot(
        self, xdata: np.ndarray, ydata: np.ndarray, redraw: bool = False
    ) -> None:
        if redraw:
            x = self.artist.get_xdata(orig=True)  # type: ignore
            y = self.artist.get_ydata(orig=True)  # type: ignore
            self.ax.cla()
            self.artist, *_ = self.ax.plot(xdata, ydata, color=self.color)
            if not self.ticks:
                self.ax.set_xticklabels([])
                self.ax.set_yticklabels([])
            self.ax.set_theta_zero_location('N')
            self.ax.set_thetagrids(np.arange(0, 360, 30))
            self.canvas.draw()
        else:
            self.artist, *_ = self.ax.plot(xdata, ydata, color=self.color)
            self.blit()

    def update_scale(self) -> None:
        x = self.artist.get_xdata(orig=True)
        y = self.artist.get_ydata(orig=True)
        self.ax.cla()
        self.artist, *_ = self.ax.plot(x, y, color=self.color)
        self.ax.grid(self.grid)
        self.ax.set_rlim(self.rmin, self.rmax)
        self.ax.set_rticks(np.arange(self.rmin, self.rmax + 1, self.rstep))
        self.canvas.draw()

    def set_scale_min(self, min: float) -> None:
        self.rmin = min
        self.update_scale()

    def set_scale_max(self, max: float) -> None:
        self.rmax = max
        self.update_scale()

    def set_scale_step(self, step: float) -> None:
        self.rstep = step
        self.update_scale()

    def set_scale(self, min: float, max: float, step: float) -> None:
        self.rmin = min
        self.rmax = max
        self.rstep = step
        self.update_scale()
