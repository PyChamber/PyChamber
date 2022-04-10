"""Qt5 MatPlotLib Widget.

    isort:skip_file
"""

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas

import matplotlib

matplotlib.use('QT5Agg')


class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
