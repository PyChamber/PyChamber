# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plot_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QSizePolicy, QToolBar,
    QWidget)

from pyqtgraph.dockarea import DockArea
from  . import resources_rc

class Ui_PlotWidget(object):
    def setupUi(self, PlotWidget):
        if not PlotWidget.objectName():
            PlotWidget.setObjectName(u"PlotWidget")
        PlotWidget.resize(800, 600)
        self.add_polar_action = QAction(PlotWidget)
        self.add_polar_action.setObjectName(u"add_polar_action")
        icon = QIcon()
        icon.addFile(u":/icons/add_polar.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_polar_action.setIcon(icon)
        self.add_cart_action = QAction(PlotWidget)
        self.add_cart_action.setObjectName(u"add_cart_action")
        icon1 = QIcon()
        icon1.addFile(u":/icons/add_cartesian.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_cart_action.setIcon(icon1)
        self.add_3d_action = QAction(PlotWidget)
        self.add_3d_action.setObjectName(u"add_3d_action")
        self.dock_area = DockArea(PlotWidget)
        self.dock_area.setObjectName(u"dock_area")
        PlotWidget.setCentralWidget(self.dock_area)
        self.toolBar = QToolBar(PlotWidget)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setAutoFillBackground(False)
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QSize(36, 36))
        PlotWidget.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.add_polar_action)
        self.toolBar.addAction(self.add_cart_action)
        self.toolBar.addAction(self.add_3d_action)

        self.retranslateUi(PlotWidget)

        QMetaObject.connectSlotsByName(PlotWidget)
    # setupUi

    def retranslateUi(self, PlotWidget):
        PlotWidget.setWindowTitle(QCoreApplication.translate("PlotWidget", u"MainWindow", None))
        self.add_polar_action.setText(QCoreApplication.translate("PlotWidget", u"New Polar Plot", None))
#if QT_CONFIG(tooltip)
        self.add_polar_action.setToolTip(QCoreApplication.translate("PlotWidget", u"Add Polar Plot", None))
#endif // QT_CONFIG(tooltip)
        self.add_cart_action.setText(QCoreApplication.translate("PlotWidget", u"New Rectangular Plot", None))
#if QT_CONFIG(tooltip)
        self.add_cart_action.setToolTip(QCoreApplication.translate("PlotWidget", u"Add Cartesian Plot", None))
#endif // QT_CONFIG(tooltip)
        self.add_3d_action.setText(QCoreApplication.translate("PlotWidget", u"New 3D Plot", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("PlotWidget", u"toolBar", None))
    # retranslateUi

