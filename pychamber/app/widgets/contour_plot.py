import itertools

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


class ContourPlot(pg.PlotWidget):
    newZBounds = QtCore.Signal(float, float)

    def __init__(
        self,
        title="",
        background="default",
        cmap="viridis",
        x_tick_spacing=15,
        y_tick_spacing=30,
        num_levels=10,
        auto_scale=False,
        draw_isos=True,
        **kwargs,
    ):
        super().__init__(title=title, background=background, **kwargs)

        self.x_tick_spacing = x_tick_spacing
        self.y_tick_spacing = y_tick_spacing
        self.num_levels = num_levels
        self.isocurves = []
        self.autoScale = auto_scale
        self.drawIsolines = draw_isos
        self.z_min = 0
        self.z_max = 1

        self.x = np.array([])
        self.y = np.array([])
        self.z = np.array([])

        self.img_item = pg.ImageItem()
        self.addItem(self.img_item)
        self.cbar = self.addColorBar(self.img_item, colorMap=cmap, interactive=False)
        self.setMouseEnabled(x=False, y=False)
        self.disableAutoRange()
        self.hideButtons()
        self.showAxes(True, showValues=(True, False, False, True))

    def setCmap(self, cmap):
        self.img_item.setColorMap(cmap)
        self.cbar.setColorMap(cmap)

    def setAutoScale(self, state):
        self.autoScale = state
        self.redraw()

    def setTitle(self, text: str) -> None:
        self.getPlotItem().setTitle(text)

    def setZMin(self, z):
        self.z_min = z
        self.redraw()

    def setZMax(self, z):
        self.z_max = z
        self.redraw()

    def setDrawIsolines(self, state: bool):
        self.drawIsolines = state
        if state:
            self.draw_isos()
            return

        for c in self.isocurves:
            self.removeItem(c)
        self.isocurves = []

    def setXLabel(self, text: str = "", units: str = "") -> None:
        self.getPlotItem().getAxis("bottom").setLabel(text=text, units=units)

    def setYLabel(self, text: str = "", units: str = "") -> None:
        self.getPlotItem().getAxis("left").setLabel(text=text, units=units)

    def setData(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.redraw()

    def draw_isos(self):
        levels = np.linspace(self.z_min, self.z_max, self.num_levels)
        self.isocurves = []
        for i in range(len(levels)):
            v = levels[i]
            c = pg.IsocurveItem(level=v, pen=(i, len(levels) * 1.5))
            self.addItem(c)
            c.setZValue(10)
            self.isocurves.append(c)
            c.setData(self.z)

    def redraw(self):
        x = self.x
        y = self.y
        z = self.z
        if any((x is None, y is None, z is None)) or any((len(x) == 0, len(y) == 0, len(z) == 0)):
            return

        self.setRange(xRange=(0, len(x)), yRange=(0, len(y)), padding=0.05)

        x_step = round(len(x) / ((np.nanmax(x) - np.nanmin(x)) / self.x_tick_spacing))
        y_step = round(len(y) / ((np.nanmax(y) - np.nanmin(y)) / self.y_tick_spacing))
        x_ticks = {k + 0.5: str(v) for k, v in itertools.islice(enumerate(x), 0, None, x_step)}
        y_ticks = {k + 0.5: str(v) for k, v in itertools.islice(enumerate(y), 0, None, y_step)}

        self.getPlotItem().getAxis("bottom").setTicks([x_ticks.items()])
        self.getPlotItem().getAxis("left").setTicks([y_ticks.items()])

        for c in self.isocurves:
            self.removeItem(c)

        if self.drawIsolines:
            self.draw_isos()

        if self.autoScale:
            self.z_min = np.clip(np.nanmin(z), -100, None)
            self.z_max = np.nanmax(z)
            self.newZBounds.emit(self.z_min, self.z_max)

        self.img_item.setImage(z)

        self.cbar.setLevels((self.z_min, self.z_max))
