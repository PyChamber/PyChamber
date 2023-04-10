# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'contour_plot_settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

from ..widgets.frequency_lineedit import FrequencyLineEdit
from pyqtgraph import ColorButton

class Ui_ContourPlotSettings(object):
    def setupUi(self, ContourPlotSettings):
        if not ContourPlotSettings.objectName():
            ContourPlotSettings.setObjectName(u"ContourPlotSettings")
        ContourPlotSettings.resize(450, 518)
        self.formLayout = QFormLayout(ContourPlotSettings)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(ContourPlotSettings)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.title_le = QLineEdit(ContourPlotSettings)
        self.title_le.setObjectName(u"title_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.title_le)

        self.label_4 = QLabel(ContourPlotSettings)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.bg_color_btn = ColorButton(ContourPlotSettings)
        self.bg_color_btn.setObjectName(u"bg_color_btn")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.bg_color_btn)

        self.label_9 = QLabel(ContourPlotSettings)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_9)

        self.freq_le = FrequencyLineEdit(ContourPlotSettings)
        self.freq_le.setObjectName(u"freq_le")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.freq_le)

        self.z_var_label = QLabel(ContourPlotSettings)
        self.z_var_label.setObjectName(u"z_var_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.z_var_label)

        self.z_var_cb = QComboBox(ContourPlotSettings)
        self.z_var_cb.setObjectName(u"z_var_cb")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.z_var_cb)

        self.pol_label = QLabel(ContourPlotSettings)
        self.pol_label.setObjectName(u"pol_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.pol_label)

        self.pol_cb = QComboBox(ContourPlotSettings)
        self.pol_cb.setObjectName(u"pol_cb")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.pol_cb)

        self.cmap_label = QLabel(ContourPlotSettings)
        self.cmap_label.setObjectName(u"cmap_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.cmap_label)

        self.cmap_cb = QComboBox(ContourPlotSettings)
        self.cmap_cb.setObjectName(u"cmap_cb")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.cmap_cb)

        self.label_5 = QLabel(ContourPlotSettings)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_5)

        self.min_sb = QDoubleSpinBox(ContourPlotSettings)
        self.min_sb.setObjectName(u"min_sb")
        self.min_sb.setMinimum(-1000000.000000000000000)
        self.min_sb.setMaximum(1000000.000000000000000)
        self.min_sb.setSingleStep(0.250000000000000)
        self.min_sb.setValue(0.000000000000000)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.min_sb)

        self.label_6 = QLabel(ContourPlotSettings)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_6)

        self.max_sb = QDoubleSpinBox(ContourPlotSettings)
        self.max_sb.setObjectName(u"max_sb")
        self.max_sb.setMinimum(-100000.000000000000000)
        self.max_sb.setMaximum(1000000.000000000000000)
        self.max_sb.setSingleStep(0.250000000000000)
        self.max_sb.setValue(1.000000000000000)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.max_sb)

        self.label_11 = QLabel(ContourPlotSettings)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_11)

        self.calibrated_checkbox = QCheckBox(ContourPlotSettings)
        self.calibrated_checkbox.setObjectName(u"calibrated_checkbox")

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.calibrated_checkbox)

        self.label_8 = QLabel(ContourPlotSettings)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.label_8)

        self.autoscale_checkbox = QCheckBox(ContourPlotSettings)
        self.autoscale_checkbox.setObjectName(u"autoscale_checkbox")

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.autoscale_checkbox)

        self.label_10 = QLabel(ContourPlotSettings)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.label_10)

        self.isolines_checkbox = QCheckBox(ContourPlotSettings)
        self.isolines_checkbox.setObjectName(u"isolines_checkbox")
        self.isolines_checkbox.setChecked(False)

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.isolines_checkbox)


        self.retranslateUi(ContourPlotSettings)

        QMetaObject.connectSlotsByName(ContourPlotSettings)
    # setupUi

    def retranslateUi(self, ContourPlotSettings):
        ContourPlotSettings.setWindowTitle(QCoreApplication.translate("ContourPlotSettings", u"Form", None))
        self.label.setText(QCoreApplication.translate("ContourPlotSettings", u"Title", None))
        self.label_4.setText(QCoreApplication.translate("ContourPlotSettings", u"Background Color", None))
        self.bg_color_btn.setText(QCoreApplication.translate("ContourPlotSettings", u"PushButton", None))
        self.label_9.setText(QCoreApplication.translate("ContourPlotSettings", u"Frequency", None))
        self.z_var_label.setText(QCoreApplication.translate("ContourPlotSettings", u"Z Variable", None))
        self.pol_label.setText(QCoreApplication.translate("ContourPlotSettings", u"Polarization", None))
        self.cmap_label.setText(QCoreApplication.translate("ContourPlotSettings", u"Colormap", None))
        self.label_5.setText(QCoreApplication.translate("ContourPlotSettings", u"Z Minimum", None))
        self.label_6.setText(QCoreApplication.translate("ContourPlotSettings", u"Z Maximum", None))
        self.label_11.setText(QCoreApplication.translate("ContourPlotSettings", u"Calibrated", None))
        self.calibrated_checkbox.setText("")
        self.label_8.setText(QCoreApplication.translate("ContourPlotSettings", u"Autoscale", None))
        self.autoscale_checkbox.setText("")
        self.label_10.setText(QCoreApplication.translate("ContourPlotSettings", u"Isolines", None))
        self.isolines_checkbox.setText("")
    # retranslateUi

