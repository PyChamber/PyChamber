import numpy as np
import pyqtgraph.functions as fn
from pyqtgraph import getConfigOption
from pyqtgraph.graphicsItems.UIGraphicsItem import UIGraphicsItem
from pyqtgraph.Qt import QtCore, QtGui


class PolarGridItem(UIGraphicsItem):
    """
    **Bases:** :class:`UIGraphicsItem <pyqtgraph.UIGraphicsItem>`

    Displays a rectangular grid of lines indicating major divisions within a coordinate system.
    Automatically determines what divisions to use.
    """

    def __init__(
        self,
        pen="default",
        textPen="default",
        angle_range=(-180, 180),
        radial_tick_spacing=10,
        angle_tick_spacing=30,
        theta_zero_location=90,
    ):
        UIGraphicsItem.__init__(self)

        self.opts = {}

        self.setPen(pen)
        self.setTextPen(textPen)
        self.setAngleRange(*angle_range)
        self.setRadialTickSpacing(radial_tick_spacing)
        self.setAngleTickSpacing(angle_tick_spacing)
        self.setThetaZeroLocation(90)
        self.setLogScale()
        self.setRange()

    def setPen(self, *args, **kwargs):
        """Set the pen used to draw the grid."""
        if kwargs == {} and (args == () or args == ("default",)):
            self.opts["pen"] = fn.mkPen(getConfigOption("foreground"))
        else:
            self.opts["pen"] = fn.mkPen(*args, **kwargs)

        self.picture = None
        self.update()

    def setTextPen(self, *args, **kwargs):
        """Set the pen used to draw the texts."""
        if kwargs == {} and (args == () or args == ("default",)):
            self.opts["textPen"] = fn.mkPen(getConfigOption("foreground"))
        else:
            if args == (None,):
                self.opts["textPen"] = None
            else:
                self.opts["textPen"] = fn.mkPen(*args, **kwargs)

        self.picture = None
        self.update()

    def setRadialTickSpacing(self, step=10):
        self.r_tick_spacing = step

    def setAngleTickSpacing(self, theta=30):
        self.angle_tick_spacing = theta
        self.update()

    def setRange(self, r_min: int = -30, r_max: int = 0):
        self.r_min = r_min
        self.r_max = r_max
        self.r_offset = self.r_max - self.r_min
        self.update()

    def setAngleRange(self, start=0, stop=360):
        self.start_angle = start
        self.sweep_angle = stop - start
        self.update()

    def setThetaZeroLocation(self, zero=90):
        self.angle_zero_location = zero
        self.update()

    def setUnit(self, unit=""):
        self.unit = unit
        self.update()

    def setLogScale(self, state=False):
        self.log_scale = state
        self.setUnit("dB")
        self.update()

    def viewRangeChanged(self):
        UIGraphicsItem.viewRangeChanged(self)
        self.picture = None

    def boundingRect(self):
        lvr = self.viewRect()
        rad = min(lvr.width() / 2, lvr.height() / 2)

        start = -(self.start_angle - self.angle_zero_location)
        start = start + (360 if start < 0 else 0)
        sweep = self.sweep_angle
        invert = False

        end = start - sweep
        end = end + (360 if end < 0 else 0)
        start, end = start % 360, end % 360
        end = 360 if end == 0 else end
        if start > end:
            temp = start
            start = end
            end = temp
        invert = sweep > 180

        axes = [start < theta < end for theta in [0, 90, 180, 270]]
        if invert:
            axes = [not ax for ax in axes]

        right = rad if axes[0] else max(0, rad * np.cos(np.deg2rad(start)), rad * np.cos(np.deg2rad(end)))
        top = rad if axes[1] else max(0, rad * np.sin(np.deg2rad(start)), rad * np.sin(np.deg2rad(end)))
        left = -rad if axes[2] else min(0, rad * np.cos(np.deg2rad(start)), rad * np.cos(np.deg2rad(end)))
        bottom = -rad if axes[3] else min(0, rad * np.sin(np.deg2rad(start)), rad * np.sin(np.deg2rad(end)))

        return QtCore.QRectF(left, top, right - left, bottom - top)

    def paint(self, p, opt, widget):
        if self.picture is None:
            self.generatePicture()
        p.drawPicture(
            QtCore.QPointF(-self.boundingRect().center().x(), -self.boundingRect().center().y()), self.picture
        )

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter()
        p.begin(self.picture)

        self.getViewWidget().rect()
        self.pixelWidth(), self.pixelHeight()
        # [vr.width(), vr.height()]
        lvr = self.viewRect()
        ul = np.array([lvr.left(), lvr.top()])
        br = np.array([lvr.right(), lvr.bottom()])

        if ul[1] > br[1]:
            x = ul[1]
            ul[1] = br[1]
            br[1] = x

        linePen = self.opts["pen"]
        linePen.setCosmetic(True)
        p.setPen(linePen)

        rad = min(lvr.width() / 2, lvr.height() / 2)
        rads = np.linspace(0, rad, num=5)

        start_angle = self.start_angle - self.angle_zero_location
        for r in rads:
            bounds = QtCore.QRectF(-r, -r, 2 * r, 2 * r)
            p.drawPie(bounds, start_angle * 16, self.sweep_angle * 16)

        for theta in np.arange(
            start_angle + self.angle_tick_spacing, start_angle + self.sweep_angle, self.angle_tick_spacing
        ):
            x = rad * np.cos(np.deg2rad(theta))
            y = -rad * np.sin(np.deg2rad(theta))
            p.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(x, y))

        tr = self.deviceTransform()
        p.setWorldTransform(fn.invertQTransform(tr))

        textPen = self.opts["textPen"]
        if textPen is not None:
            p.setPen(textPen)
            for r in rads:
                text = f"{r - self.r_offset:.2g} {self.unit}" if self.log_scale else f"{r:.2g} {self.unit}"
                x = np.cos(np.deg2rad(self.start_angle + self.angle_zero_location)) * r
                y = np.sin(np.deg2rad(self.start_angle + self.angle_zero_location)) * r
                point = tr.map(QtCore.QPointF(x, y))
                p.drawText(point, text)

        p.end()
