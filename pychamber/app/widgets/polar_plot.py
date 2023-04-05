from dataclasses import dataclass

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


@dataclass
class PolarPlotDataItem:
    data_item: pg.PlotDataItem
    theta: np.ndarray = np.array([])
    r: np.ndarray = np.array([])


class PolarPlot(pg.GraphicsView):
    sigRangeChanged = QtCore.Signal(object, object)
    sigTransformChanged = QtCore.Signal(object)
    rRangeUpdated = QtCore.Signal(float, float, float)

    def __init__(self, parent=None, useOpenGL=None, background="default", auto_scale=False, **kargs):
        super().__init__(parent, useOpenGL, background)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.enableMouse(False)

        self.plotItem = pg.PlotItem(**kargs)
        self.setCentralItem(self.plotItem)

        self.plotItems = []
        self.autoScale = auto_scale

        for m in [
            "addItem",
            "removeItem",
            "autoRange",
            "clear",
            "setAxisItems",
            "setXRange",
            "setYRange",
            "setRange",
            "setAspectLocked",
            "setMouseEnabled",
            "setXLink",
            "setYLink",
            "enableAutoRange",
            "disableAutoRange",
            "setLimits",
            "register",
            "unregister",
            "viewRect",
        ]:
            setattr(self, m, getattr(self.plotItem, m))
        self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)

        self.circleList = []
        self.circleLabel = []
        self.angleList = []
        self.angleLabel = []
        self.data = ([], [])

        self.r_min = 0
        self.r_max = 1
        self.r_step = 0.15
        self.angle_zero_location = 0
        self.angle_tick_spacing = 30
        self.theta_dir = -1
        self.angle_ticks = np.arange(-np.pi, np.pi, np.deg2rad(self.angle_tick_spacing))
        self.circle_units = ""
        self.polar_amp_offset = self.r_max - self.r_min
        self.n_circles = 6

        self.plotItem.setAspectLocked()
        self.plotItem.hideAxis("left")
        self.plotItem.hideAxis("bottom")

        self.circleLabel.append(pg.TextItem(f"{self.r_min:.2g}", angle=-45))
        self.plotItem.addItem(self.circleLabel[-1])
        self.circleLabel[-1].setPos(0, 0)
        for pos in np.arange(self.r_max, self.r_min, -self.r_step):
            self.add_circle(pos)

        for angle in self.angle_ticks:
            self.add_radial_line(angle)

        self.plotItem.setMouseEnabled(x=False, y=False)

    def getPlotItem(self) -> pg.PlotItem:
        return self.plotItem

    @property
    def units(self) -> str:
        return self.circle_units

    @units.setter
    def units(self, unit: str) -> None:
        self.circle_units = unit
        self.update_labels()

    def viewRangeChanged(self, view_range, view):
        self.sigRangeChanged.emit(self, view_range)

    def add_radial_line(self, angle):
        if np.isclose(angle, 0):
            angle = 0

        x = self.polar_amp_offset * np.cos(angle)
        y = self.polar_amp_offset * np.sin(angle)

        line = pg.PlotCurveItem([0, x], [0, y])
        line.setPen(pg.mkPen(0.2))
        line.setZValue(-1)
        self.addItem(line)
        self.angleList.append(line)

        label_x = x + self.r_step / 2 * np.cos(angle)
        label_y = y + self.r_step / 2 * np.sin(angle)

        label = pg.TextItem(f"{np.rad2deg(self.theta_dir * angle):.3g}", anchor=(0.5, 0.5))
        label.setPos(label_x, label_y)
        self.addItem(label)
        self.angleLabel.append(label)

    def add_circle(self, pos):
        location = self.r_max - pos
        circle = QtWidgets.QGraphicsEllipseItem(
            -self.polar_amp_offset + location,
            -self.polar_amp_offset + location,
            (self.polar_amp_offset - location) * 2,
            (self.polar_amp_offset - location) * 2,
        )
        circle.setStartAngle(0)
        circle.setSpanAngle(5760)
        circle.setPen(pg.mkPen(0.2))
        circle.setZValue(-1)
        self.plotItem.addItem(circle)
        self.circleList.append(circle)

        label = pg.TextItem(f"{pos:.2g} {self.circle_units}", angle=-45)
        label.setPos(self.polar_amp_offset - location, 0)
        self.plotItem.addItem(label)
        self.circleLabel.append(label)

    def set_r_min(self, value):
        self.r_min = value
        if self.r_min >= self.r_max:
            self.r_max = self.r_min + 1
        self.polar_amp_offset = self.r_max - self.r_min
        if self.r_step > self.polar_amp_offset:
            self.r_step = self.r_max
        self.redraw()

    def set_r_max(self, r_max):
        self.r_max = r_max
        if self.r_min >= self.r_max:
            self.r_min = self.r_max - 1
        self.polar_amp_offset = self.r_max - self.r_min
        if self.r_step > self.polar_amp_offset:
            self.r_step = self.r_max
        self.redraw()

    def set_r_step(self, step):
        self.r_step = step
        self.redraw()

    def set_r_range(self, r_min, r_max, r_step):
        self.r_min = r_min
        self.r_max = r_max
        self.r_step = r_step
        self.polar_amp_offset = self.r_max - self.r_min
        self.redraw()

    def set_angle_zero_location(self, angle):
        self.angle_zero_location = self.theta_dir * angle
        self.redraw()

    def setAutoScale(self, state: bool):
        self.autoScale = state
        self.redraw()

    def setTitle(self, text: str) -> None:
        self.plotItem.setTitle(text)

    def auto_scale(self):
        if len(self.plotItems) == 0 or any(len(item.r) == 0 for item in self.plotItems):
            return
        new_rmin = np.amin([item.r for item in self.plotItems])
        new_rmax = np.amax([item.r for item in self.plotItems])

        if new_rmin == new_rmax:
            new_rmin = new_rmin - 1
            new_rmax = new_rmax + 1

        self.r_min = new_rmin
        self.r_max = new_rmax
        self.r_step = (self.r_max - self.r_min) / 5
        self.polar_amp_offset = self.r_max - self.r_min

    def update_grid(self):
        self.circleLabel[0].setPos(0, 0)
        self.circleLabel[0].setText(f"{self.r_min:.2g} {self.circle_units}")
        circles = np.arange(self.r_max, self.r_min, -self.r_step)
        if len(circles) > 10:
            circles = np.linspace(self.r_max, self.r_min, 5)
            self.r_step = np.abs(circles[1] - circles[0])
            self.rRangeUpdated.emit(self.r_min, self.r_max, self.r_step)
        if len(self.circleList) > len(circles):
            n = len(circles)
            to_remove = zip(self.circleList[n:], self.circleLabel[n + 1 :], strict=False)
            for circle, label in to_remove:
                self.removeItem(circle)
                self.removeItem(label)
            self.circleList = self.circleList[0:n]
            self.circleLabel = self.circleLabel[0 : n + 1]
        elif len(self.circleList) < len(circles):
            n = len(circles)
            num_to_add = n - len(self.circleList)
            for _ in range(num_to_add):
                self.add_circle(0)

        for i, (line, ang_label) in enumerate(zip(self.angleList, self.angleLabel, strict=False)):
            angle = self.angle_ticks[i] + np.deg2rad(self.angle_zero_location)
            x = self.polar_amp_offset * np.cos(angle)
            y = self.polar_amp_offset * np.sin(angle)
            line.setData([0, x], [0, y])
            label_x = x + self.r_step / 2 * np.cos(angle)
            label_y = y + self.r_step / 2 * np.sin(angle)
            ang_label.setText(f"{np.rad2deg(self.theta_dir * self.angle_ticks[i]):.3g}")
            ang_label.setPos(label_x, label_y)
        self.angleLabel[len(self.angleLabel) // 2].setText("0")

        for i, pos in enumerate(circles):
            location = self.r_max - pos
            self.circleList[i].setRect(
                -self.polar_amp_offset + location,
                -self.polar_amp_offset + location,
                (self.polar_amp_offset - location) * 2,
                (self.polar_amp_offset - location) * 2,
            )
            self.circleLabel[i + 1].setText(f"{pos:.2g} {self.circle_units}")
            self.circleLabel[i + 1].setPos(self.polar_amp_offset - location, 0)

    def update_labels(self):
        self.circleLabel[0].setText(f"{self.r_min:.2g} {self.circle_units}")
        for i, pos in enumerate(self.circles):
            location = self.r_max - pos
            self.circleLabel[i + 1].setText(f"{pos:.2g} {self.circle_units}")
            self.circleLabel[i + 1].setPos(self.polar_amp_offset - location, 0)

    def redraw(self):
        if self.autoScale:
            self.auto_scale()
        self.update_grid()
        for item in self.plotItems:
            if item.theta is None or item.r is None:
                continue
            x, y = self.mapData(self.theta_dir * item.theta, item.r)
            item.data_item.setData(x, y)

    def redrawItem(self, item):
        if self.autoScale:
            self.auto_scale()
        self.update_grid()
        if item.theta is None or item.r is None:
            return
        x, y = self.mapData(self.theta_dir * item.theta, item.r)
        item.data_item.setData(x, y)

    def mapData(self, theta, r):
        theta_mapped = theta + self.angle_zero_location
        r_mapped = np.clip(r, self.r_min, self.r_max)
        r_mapped = r_mapped + np.abs(self.r_min)

        x = r_mapped * np.cos(np.deg2rad(theta_mapped))
        y = r_mapped * np.sin(np.deg2rad(theta_mapped))

        return x, y

    def plot(self, theta=None, r=None, **kwargs):
        plot_item = PolarPlotDataItem(pg.PlotDataItem(**kwargs))
        self.plotItems.append(plot_item)
        self.addItem(plot_item.data_item)

        if theta is None or r is None:
            return plot_item

        if len(theta) == 0 or len(r) == 0:
            return plot_item

        plot_item.theta = theta
        plot_item.r = r
        x, y = self.mapData(plot_item.theta, plot_item.r)

        plot_item.data_item.setData(x, y)

        if self.autoScale:
            self.auto_scale()

    def removeTrace(self, item: PolarPlotDataItem):
        self.removeItem(item.data_item)
