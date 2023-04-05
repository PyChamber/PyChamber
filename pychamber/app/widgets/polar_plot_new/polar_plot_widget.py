import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from .polar_grid_item import PolarGridItem
from .polar_plot_data_item import PolarPlotDataItem


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        kwds["enableMenu"] = False
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.PanMode)

    def addItem(self, item, ignoreBounds=False):
        super().addItem(item, ignoreBounds)
        item.boundingRect().center()
        # item.setPos(QtCore.QPointF(-bounds.x(), -bounds.y()))

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.RightButton:
            self.autoRange()

    ## reimplement mouseDragEvent to disable continuous axis zoom
    # TODO
    def mouseDragEvent(self, ev, axis=None):
        # length = (ev.lastPos() - ev.pos()).length()
        ev.ignore()

    def wheelEvent(self, ev, axis=None):
        if axis in (0, 1):
            mask = [False, False]
            mask[axis] = self.state["mouseEnabled"][axis]
        else:
            mask = self.state["mouseEnabled"][:]
        s = 1.02 ** (ev.delta() * self.state["wheelScaleFactor"])  # actual scaling factor
        s = [(None if m is False else s) for m in mask]

        self._resetTarget()
        self.scaleBy(s, center=None)
        ev.accept()
        self.sigRangeChangedManually.emit(mask)


class PolarPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, background="default", plotItem=None, **kargs) -> None:
        self.vb = CustomViewBox()
        self.vb.setAspectLocked(True)
        self.polarGrid = PolarGridItem()
        self.vb.addItem(self.polarGrid)
        self.plot_items = []

        super().__init__(viewBox=self.vb, enableMenu=False)

        self.getPlotItem().showAxes(False)

    def plot(self, theta, r, **kargs):
        clear = kargs.get("clear", False)
        params = kargs.get("params", None)

        if clear:
            self.getPlotItem().clear()

        item = PolarPlotDataItem(theta, r, **kargs)
        self.plot_items.append(item)

        if params is None:
            params = {}
        self.addItem(item, params=params)

        return item

    def setLogScale(self, state=False):
        self.log_state = state
        if state and not self.log_state:
            view = self.vb.viewRect()
            r = min(view.width() / 2, view.height() / 2)
            r = 20 * np.log10(r)
            self.vb.setRange(xRange=(-r, r), yRange=(-r, r))

        self.polarGrid.setLogScale(state)
