import numpy as np
from pyqtgraph import PlotDataItem


class PolarPlotDataItem(PlotDataItem):
    def __init__(self, theta, r):
        x, y = self.pol_to_cart(theta, r)
        self.theta, self.r = theta, r
        super().__init__(x, y)

    def getOriginalDataset(self):
        return self.theta, self.r

    def pol_to_cart(self, theta, r):
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        return x, y
