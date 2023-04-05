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
        self.add_rect_action = QAction(PlotWidget)
        self.add_rect_action.setObjectName(u"add_rect_action")
        icon1 = QIcon()
        icon1.addFile(u":/icons/add_rect.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_rect_action.setIcon(icon1)
        self.add_contour_action = QAction(PlotWidget)
        self.add_contour_action.setObjectName(u"add_contour_action")
        icon2 = QIcon()
        icon2.addFile(u":/icons/add_contour.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_contour_action.setIcon(icon2)
        self.add_three_d_action = QAction(PlotWidget)
        self.add_three_d_action.setObjectName(u"add_three_d_action")
        icon3 = QIcon()
        icon3.addFile(u":/icons/add_3d.png", QSize(), QIcon.Normal, QIcon.Off)
        self.add_three_d_action.setIcon(icon3)
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
        self.toolBar.addAction(self.add_rect_action)
        self.toolBar.addAction(self.add_contour_action)
        self.toolBar.addAction(self.add_three_d_action)

        self.retranslateUi(PlotWidget)

        QMetaObject.connectSlotsByName(PlotWidget)
    # setupUi

    def retranslateUi(self, PlotWidget):
        PlotWidget.setWindowTitle(QCoreApplication.translate("PlotWidget", u"MainWindow", None))
        self.add_polar_action.setText(QCoreApplication.translate("PlotWidget", u"Polar Plot", None))
#if QT_CONFIG(tooltip)
        self.add_polar_action.setToolTip(QCoreApplication.translate("PlotWidget", u"Add Polar Plot", None))
#endif // QT_CONFIG(tooltip)
        self.add_rect_action.setText(QCoreApplication.translate("PlotWidget", u"Rectangular Plot", None))
#if QT_CONFIG(tooltip)
        self.add_rect_action.setToolTip(QCoreApplication.translate("PlotWidget", u"Add Rectangular Plot", None))
#endif // QT_CONFIG(tooltip)
        self.add_contour_action.setText(QCoreApplication.translate("PlotWidget", u"Contour Plot", None))
#if QT_CONFIG(tooltip)
        self.add_contour_action.setToolTip(QCoreApplication.translate("PlotWidget", u"Add Contour Plot", None))
#endif // QT_CONFIG(tooltip)
        self.add_three_d_action.setText(QCoreApplication.translate("PlotWidget", u"Add 3D Plot", None))
#if QT_CONFIG(tooltip)
        self.add_three_d_action.setToolTip(QCoreApplication.translate("PlotWidget", u"3D Plot", None))
#endif // QT_CONFIG(tooltip)
        self.toolBar.setWindowTitle(QCoreApplication.translate("PlotWidget", u"toolBar", None))
    # retranslateUi

