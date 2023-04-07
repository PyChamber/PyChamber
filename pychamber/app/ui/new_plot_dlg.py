# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_plot_dlg.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGroupBox, QLabel,
    QLineEdit, QSizePolicy, QStackedWidget, QVBoxLayout,
    QWidget)

from ..widgets.contour_plot_settings import ContourPlotSettings
from ..widgets.polar_plot_settings import PolarPlotSettings
from ..widgets.rect_plot_settings import RectPlotSettings
from ..widgets.three_d_plot_settings import ThreeDPlotSettings
from pyqtgraph import ColorButton

class Ui_NewPlotDialog(object):
    def setupUi(self, NewPlotDialog):
        if not NewPlotDialog.objectName():
            NewPlotDialog.setObjectName(u"NewPlotDialog")
        NewPlotDialog.resize(425, 411)
        self.verticalLayout_7 = QVBoxLayout(NewPlotDialog)
        self.verticalLayout_7.setSpacing(9)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(NewPlotDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.title_le = QLineEdit(NewPlotDialog)
        self.title_le.setObjectName(u"title_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.title_le)

        self.label_4 = QLabel(NewPlotDialog)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.bg_color_btn = ColorButton(NewPlotDialog)
        self.bg_color_btn.setObjectName(u"bg_color_btn")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.bg_color_btn)

        self.label_5 = QLabel(NewPlotDialog)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_5)

        self.plot_type_cb = QComboBox(NewPlotDialog)
        self.plot_type_cb.addItem("")
        self.plot_type_cb.addItem("")
        self.plot_type_cb.addItem("")
        self.plot_type_cb.addItem("")
        self.plot_type_cb.addItem("")
        self.plot_type_cb.setObjectName(u"plot_type_cb")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.plot_type_cb)


        self.verticalLayout_7.addLayout(self.formLayout)

        self.plot_pg_gb = QGroupBox(NewPlotDialog)
        self.plot_pg_gb.setObjectName(u"plot_pg_gb")
        self.plot_pg_gb.setAutoFillBackground(False)
        self.plot_pg_gb.setStyleSheet(u"QGroupBox {\n"
"    border: 2px solid gray;\n"
"    border-radius: 4px;\n"
"    margin-top: 1ex; \n"
"	padding: 1px 0px;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top center; \n"
"    padding: 0 3px;\n"
"}")
        self.plot_pg_gb.setAlignment(Qt.AlignCenter)
        self.plot_pg_gb.setFlat(False)
        self.verticalLayout_2 = QVBoxLayout(self.plot_pg_gb)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 9, 3, 3)
        self.plot_controls = QStackedWidget(self.plot_pg_gb)
        self.plot_controls.setObjectName(u"plot_controls")
        self.no_plot_type_pg = QWidget()
        self.no_plot_type_pg.setObjectName(u"no_plot_type_pg")
        self.verticalLayout = QVBoxLayout(self.no_plot_type_pg)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(self.no_plot_type_pg)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.plot_controls.addWidget(self.no_plot_type_pg)
        self.polar_settings = PolarPlotSettings()
        self.polar_settings.setObjectName(u"polar_settings")
        self.plot_controls.addWidget(self.polar_settings)
        self.rect_settings = RectPlotSettings()
        self.rect_settings.setObjectName(u"rect_settings")
        self.plot_controls.addWidget(self.rect_settings)
        self.contour_settings = ContourPlotSettings()
        self.contour_settings.setObjectName(u"contour_settings")
        self.plot_controls.addWidget(self.contour_settings)
        self.three_d_settings = ThreeDPlotSettings()
        self.three_d_settings.setObjectName(u"three_d_settings")
        self.plot_controls.addWidget(self.three_d_settings)

        self.verticalLayout_2.addWidget(self.plot_controls)


        self.verticalLayout_7.addWidget(self.plot_pg_gb)

        self.buttonBox = QDialogButtonBox(NewPlotDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_7.addWidget(self.buttonBox)

        self.verticalLayout_7.setStretch(1, 1)

        self.retranslateUi(NewPlotDialog)
        self.buttonBox.accepted.connect(NewPlotDialog.accept)
        self.buttonBox.rejected.connect(NewPlotDialog.reject)
        self.plot_type_cb.currentIndexChanged.connect(self.plot_controls.setCurrentIndex)

        self.plot_controls.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(NewPlotDialog)
    # setupUi

    def retranslateUi(self, NewPlotDialog):
        NewPlotDialog.setWindowTitle(QCoreApplication.translate("NewPlotDialog", u"Add Plot", None))
        self.label.setText(QCoreApplication.translate("NewPlotDialog", u"Title", None))
        self.label_4.setText(QCoreApplication.translate("NewPlotDialog", u"Background Color", None))
        self.bg_color_btn.setText(QCoreApplication.translate("NewPlotDialog", u"PushButton", None))
        self.label_5.setText(QCoreApplication.translate("NewPlotDialog", u"Plot Type", None))
        self.plot_type_cb.setItemText(0, "")
        self.plot_type_cb.setItemText(1, QCoreApplication.translate("NewPlotDialog", u"Polar", None))
        self.plot_type_cb.setItemText(2, QCoreApplication.translate("NewPlotDialog", u"Rectangular", None))
        self.plot_type_cb.setItemText(3, QCoreApplication.translate("NewPlotDialog", u"Contour", None))
        self.plot_type_cb.setItemText(4, QCoreApplication.translate("NewPlotDialog", u"3D", None))

        self.plot_pg_gb.setTitle(QCoreApplication.translate("NewPlotDialog", u"No Plot Settings", None))
        self.label_2.setText(QCoreApplication.translate("NewPlotDialog", u"Select a plot type", None))
    # retranslateUi

