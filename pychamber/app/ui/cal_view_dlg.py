# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cal_view_dlg.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHeaderView, QPlainTextEdit,
    QSizePolicy, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

from pyqtgraph import PlotWidget

class Ui_CalViewDialog(object):
    def setupUi(self, CalViewDialog):
        if not CalViewDialog.objectName():
            CalViewDialog.setObjectName(u"CalViewDialog")
        CalViewDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(CalViewDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(CalViewDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.plots_tab = QWidget()
        self.plots_tab.setObjectName(u"plots_tab")
        self.verticalLayout_2 = QVBoxLayout(self.plots_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.cal_plot = PlotWidget(self.plots_tab)
        self.cal_plot.setObjectName(u"cal_plot")

        self.verticalLayout_2.addWidget(self.cal_plot)

        self.tabWidget.addTab(self.plots_tab, "")
        self.table_tab = QWidget()
        self.table_tab.setObjectName(u"table_tab")
        self.verticalLayout_4 = QVBoxLayout(self.table_tab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.cal_table = QTableWidget(self.table_tab)
        self.cal_table.setObjectName(u"cal_table")

        self.verticalLayout_4.addWidget(self.cal_table)

        self.tabWidget.addTab(self.table_tab, "")
        self.notes_tab = QWidget()
        self.notes_tab.setObjectName(u"notes_tab")
        self.verticalLayout_3 = QVBoxLayout(self.notes_tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.notes_pte = QPlainTextEdit(self.notes_tab)
        self.notes_pte.setObjectName(u"notes_pte")

        self.verticalLayout_3.addWidget(self.notes_pte)

        self.tabWidget.addTab(self.notes_tab, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(CalViewDialog)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(CalViewDialog)
    # setupUi

    def retranslateUi(self, CalViewDialog):
        CalViewDialog.setWindowTitle(QCoreApplication.translate("CalViewDialog", u"View Calibration", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.plots_tab), QCoreApplication.translate("CalViewDialog", u"Plot", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.table_tab), QCoreApplication.translate("CalViewDialog", u"Table", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.notes_tab), QCoreApplication.translate("CalViewDialog", u"Notes", None))
    # retranslateUi

