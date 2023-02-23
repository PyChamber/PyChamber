################################################################################
## Form generated from reading UI file 'plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from pyqtgraph.dockarea import DockArea
from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QIcon,
)
from PySide6.QtWidgets import QToolBar


class Ui_PlotWidget:
    def setupUi(self, PlotWidget):
        if not PlotWidget.objectName():
            PlotWidget.setObjectName("PlotWidget")
        PlotWidget.resize(800, 600)
        self.add_polar_action = QAction(PlotWidget)
        self.add_polar_action.setObjectName("add_polar_action")
        icon = QIcon()
        icon.addFile(":/icons/add_polar.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_polar_action.setIcon(icon)
        self.add_cart_action = QAction(PlotWidget)
        self.add_cart_action.setObjectName("add_cart_action")
        icon1 = QIcon()
        icon1.addFile(":/icons/add_cartesian.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_cart_action.setIcon(icon1)
        self.add_3d_action = QAction(PlotWidget)
        self.add_3d_action.setObjectName("add_3d_action")
        self.dock_area = DockArea(PlotWidget)
        self.dock_area.setObjectName("dock_area")
        PlotWidget.setCentralWidget(self.dock_area)
        self.plot_toolbar = QToolBar(PlotWidget)
        self.plot_toolbar.setObjectName("plot_toolbar")
        self.plot_toolbar.setMovable(False)
        self.plot_toolbar.setAllowedAreas(Qt.RightToolBarArea)
        self.plot_toolbar.setIconSize(QSize(48, 48))
        self.plot_toolbar.setFloatable(False)
        PlotWidget.addToolBar(Qt.RightToolBarArea, self.plot_toolbar)

        self.plot_toolbar.addAction(self.add_polar_action)
        self.plot_toolbar.addAction(self.add_cart_action)
        self.plot_toolbar.addAction(self.add_3d_action)

        self.retranslateUi(PlotWidget)

        QMetaObject.connectSlotsByName(PlotWidget)

    # setupUi

    def retranslateUi(self, PlotWidget):
        PlotWidget.setWindowTitle(QCoreApplication.translate("PlotWidget", "MainWindow", None))
        self.add_polar_action.setText(QCoreApplication.translate("PlotWidget", "Polar", None))
        # if QT_CONFIG(tooltip)
        self.add_polar_action.setToolTip(QCoreApplication.translate("PlotWidget", "Add Polar Plot", None))
        # endif // QT_CONFIG(tooltip)
        self.add_cart_action.setText(QCoreApplication.translate("PlotWidget", "Cartesian", None))
        # if QT_CONFIG(tooltip)
        self.add_cart_action.setToolTip(QCoreApplication.translate("PlotWidget", "Add Cartesian Plot", None))
        # endif // QT_CONFIG(tooltip)
        self.add_3d_action.setText(QCoreApplication.translate("PlotWidget", "3D", None))
        self.plot_toolbar.setWindowTitle(QCoreApplication.translate("PlotWidget", "toolBar", None))

    # retranslateUi
