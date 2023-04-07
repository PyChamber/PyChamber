# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'polar_plot_settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from pyqtgraph import ColorButton

class Ui_PolarPlotSettings(object):
    def setupUi(self, PolarPlotSettings):
        if not PolarPlotSettings.objectName():
            PolarPlotSettings.setObjectName(u"PolarPlotSettings")
        PolarPlotSettings.resize(318, 600)
        self.verticalLayout = QVBoxLayout(PolarPlotSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(PolarPlotSettings)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.title_le = QLineEdit(PolarPlotSettings)
        self.title_le.setObjectName(u"title_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.title_le)

        self.label_4 = QLabel(PolarPlotSettings)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.bg_color_btn = ColorButton(PolarPlotSettings)
        self.bg_color_btn.setObjectName(u"bg_color_btn")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.bg_color_btn)

        self.label_3 = QLabel(PolarPlotSettings)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.ang_var_cb = QComboBox(PolarPlotSettings)
        self.ang_var_cb.setObjectName(u"ang_var_cb")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.ang_var_cb)

        self.label_9 = QLabel(PolarPlotSettings)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_9)

        self.theta_zero_ang_dsb = QDoubleSpinBox(PolarPlotSettings)
        self.theta_zero_ang_dsb.setObjectName(u"theta_zero_ang_dsb")
        self.theta_zero_ang_dsb.setMinimum(-180.000000000000000)
        self.theta_zero_ang_dsb.setMaximum(180.000000000000000)
        self.theta_zero_ang_dsb.setSingleStep(1.000000000000000)
        self.theta_zero_ang_dsb.setValue(0.000000000000000)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.theta_zero_ang_dsb)

        self.label_2 = QLabel(PolarPlotSettings)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_2)

        self.r_var_cb = QComboBox(PolarPlotSettings)
        self.r_var_cb.setObjectName(u"r_var_cb")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.r_var_cb)

        self.min_label = QLabel(PolarPlotSettings)
        self.min_label.setObjectName(u"min_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.min_label)

        self.min_sb = QDoubleSpinBox(PolarPlotSettings)
        self.min_sb.setObjectName(u"min_sb")
        self.min_sb.setMinimum(-1000000.000000000000000)
        self.min_sb.setMaximum(1000000.000000000000000)
        self.min_sb.setSingleStep(0.250000000000000)
        self.min_sb.setValue(0.000000000000000)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.min_sb)

        self.max_label = QLabel(PolarPlotSettings)
        self.max_label.setObjectName(u"max_label")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.max_label)

        self.max_sb = QDoubleSpinBox(PolarPlotSettings)
        self.max_sb.setObjectName(u"max_sb")
        self.max_sb.setMinimum(-100000.000000000000000)
        self.max_sb.setMaximum(1000000.000000000000000)
        self.max_sb.setSingleStep(0.250000000000000)
        self.max_sb.setValue(1.000000000000000)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.max_sb)

        self.step_label = QLabel(PolarPlotSettings)
        self.step_label.setObjectName(u"step_label")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.step_label)

        self.step_sb = QDoubleSpinBox(PolarPlotSettings)
        self.step_sb.setObjectName(u"step_sb")
        self.step_sb.setMinimum(0.000000000000000)
        self.step_sb.setMaximum(100000.000000000000000)
        self.step_sb.setSingleStep(0.250000000000000)
        self.step_sb.setValue(0.250000000000000)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.step_sb)

        self.label_8 = QLabel(PolarPlotSettings)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_8)

        self.autoscale_checkbox = QCheckBox(PolarPlotSettings)
        self.autoscale_checkbox.setObjectName(u"autoscale_checkbox")

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.autoscale_checkbox)


        self.verticalLayout.addLayout(self.formLayout)

        self.add_trace_btn = QPushButton(PolarPlotSettings)
        self.add_trace_btn.setObjectName(u"add_trace_btn")
        self.add_trace_btn.setFlat(False)

        self.verticalLayout.addWidget(self.add_trace_btn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(PolarPlotSettings)

        QMetaObject.connectSlotsByName(PolarPlotSettings)
    # setupUi

    def retranslateUi(self, PolarPlotSettings):
        PolarPlotSettings.setWindowTitle(QCoreApplication.translate("PolarPlotSettings", u"Form", None))
        self.label.setText(QCoreApplication.translate("PolarPlotSettings", u"Title", None))
        self.label_4.setText(QCoreApplication.translate("PolarPlotSettings", u"Background Color", None))
        self.bg_color_btn.setText(QCoreApplication.translate("PolarPlotSettings", u"PushButton", None))
        self.label_3.setText(QCoreApplication.translate("PolarPlotSettings", u"Angular Variable", None))
        self.label_9.setText(QCoreApplication.translate("PolarPlotSettings", u"Zero location", None))
        self.label_2.setText(QCoreApplication.translate("PolarPlotSettings", u"R Variable", None))
        self.min_label.setText(QCoreApplication.translate("PolarPlotSettings", u"R Minimum", None))
        self.max_label.setText(QCoreApplication.translate("PolarPlotSettings", u"R Maximum", None))
        self.step_label.setText(QCoreApplication.translate("PolarPlotSettings", u"R Step", None))
        self.label_8.setText(QCoreApplication.translate("PolarPlotSettings", u"Autoscale", None))
        self.autoscale_checkbox.setText("")
        self.add_trace_btn.setText(QCoreApplication.translate("PolarPlotSettings", u"Add Trace", None))
    # retranslateUi

