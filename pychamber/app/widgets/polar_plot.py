import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


class PolarPlotWidget(pg.GraphicsView):
    # signals wrapped from PlotItem / ViewBox
    sigRangeChanged = QtCore.Signal(object, object)
    sigTransformChanged = QtCore.Signal(object)

    def __init__(self, parent=None, useOpenGL=None, background="default", **kargs):
        super().__init__(parent, useOpenGL, background)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.enableMouse(False)

        self.plotItem = pg.PlotItem(**kargs)
        self.setCentralItem(self.plotItem)

        self.polarPlot = pg.PlotDataItem()
        self.polarPlotHold = pg.PlotDataItem()

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
        # QtCore.QObject.connect(self.plotItem, QtCore.SIGNAL('viewChanged'), self.viewChanged)
        self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)

        self.penActive = pg.mkPen(color=(244, 143, 177), width=2)
        self.penHold = pg.mkPen(color=(158, 158, 158), width=1)

        self.circleList = []
        self.circleLabel = []
        self.angleList = []
        self.angleLabel = []

        self.r_min = -30
        self.r_max = 0
        self.r_step = 10
        self.angle_zero_location = 0
        self.circle_units = "dB"
        self.polar_amp_offset = self.r_max - self.r_min
        self.n_circles = 6
        self.polarPlot.setPen(self.penActive)
        self.addItem(self.polarPlot)

        self.plotItem.setAspectLocked()
        self.plotItem.hideAxis("left")
        self.plotItem.hideAxis("bottom")

        self.circleLabel.append(pg.TextItem(f"{self.r_min:.2g} dB", angle=-45))
        self.plotItem.addItem(self.circleLabel[-1])
        self.circleLabel[-1].setPos(0, 0)
        for pos in np.arange(self.r_max, self.r_min, -self.r_step):
            self.add_circle(pos)

        for angle in np.arange(-np.pi, np.pi, np.deg2rad(30)):
            self.add_radial_line(angle)

        self.plotItem.setMouseEnabled(x=False, y=False)

    def viewRangeChanged(self, view_range, view):
        self.sigRangeChanged.emit(self, view_range)

    def add_radial_line(self, angle):
        if np.isclose(angle, 0):
            angle = 0

        x = self.polar_amp_offset * np.cos(angle + self.angle_zero_location)
        y = self.polar_amp_offset * np.sin(angle + self.angle_zero_location)

        line = pg.PlotCurveItem([0, x], [0, y])
        line.setPen(pg.mkPen(0.2))
        line.setZValue(-1)
        self.addItem(line)
        self.angleList.append(line)

        label_x = x + self.r_step / 2 * np.cos(angle + self.angle_zero_location)
        label_y = y + self.r_step / 2 * np.sin(angle + self.angle_zero_location)

        label = pg.TextItem(f"{np.rad2deg(angle):.3g}", anchor=(0.5, 0.5))
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
        self.update_grid()

    def set_r_max(self, r_max):
        self.r_max = r_max
        if self.r_min >= self.r_max:
            self.r_min = self.r_max - 1
        self.polar_amp_offset = self.r_max - self.r_min
        if self.r_step > self.polar_amp_offset:
            self.r_step = self.r_max
        self.update_grid()

    def set_r_step(self, step):
        self.r_step = step
        self.update_grid()

    def set_angle_zero_location(self, angle):
        self.angle_zero_location = np.deg2rad(angle)
        self.update_grid()

    def update_grid(self):
        self.circleLabel[0].setPos(0, 0)
        self.circleLabel[0].setText(f"{self.r_min:.2g} {self.circle_units}")
        circles = np.arange(self.r_max, self.r_min, -self.r_step)
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
                self.add_circle(0)  # Don't care about the position since we're setting it just below

        for line, ang_label in zip(self.angleList, self.angleLabel, strict=False):
            xs, ys = line.getData()
            x_end, y_end = xs[1], ys[1]
            angle = np.arctan2(y_end, x_end)
            x = self.polar_amp_offset * np.cos(angle + self.angle_zero_location)
            y = self.polar_amp_offset * np.sin(angle + self.angle_zero_location)
            line.setData([0, x], [0, y])
            label_x = x + self.r_step / 2 * np.cos(angle + self.angle_zero_location)
            label_y = y + self.r_step / 2 * np.sin(angle + self.angle_zero_location)
            ang_label.setPos(label_x, label_y)

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

    def plot(self, thetas, rs):
        thetas = thetas + self.angle_zero_location
        rs = np.where(rs <= self.r_min, self.r_min, rs)
        rs = rs + np.abs(self.r_min)
        x = rs * np.cos(thetas)
        y = rs * np.sin(thetas)
        self.polarPlot.setData(x, y)
