# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rect_plot_settings.ui'
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

class Ui_RectPlotSettings(object):
    def setupUi(self, RectPlotSettings):
        if not RectPlotSettings.objectName():
            RectPlotSettings.setObjectName(u"RectPlotSettings")
        RectPlotSettings.resize(799, 595)
        self.verticalLayout = QVBoxLayout(RectPlotSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(RectPlotSettings)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.title_le = QLineEdit(RectPlotSettings)
        self.title_le.setObjectName(u"title_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.title_le)

        self.label_4 = QLabel(RectPlotSettings)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.bg_color_btn = ColorButton(RectPlotSettings)
        self.bg_color_btn.setObjectName(u"bg_color_btn")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.bg_color_btn)

        self.label_2 = QLabel(RectPlotSettings)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.x_var_cb = QComboBox(RectPlotSettings)
        self.x_var_cb.setObjectName(u"x_var_cb")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.x_var_cb)

        self.label_3 = QLabel(RectPlotSettings)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_3)

        self.y_var_cb = QComboBox(RectPlotSettings)
        self.y_var_cb.setObjectName(u"y_var_cb")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.y_var_cb)

        self.min_label = QLabel(RectPlotSettings)
        self.min_label.setObjectName(u"min_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.min_label)

        self.min_sb = QDoubleSpinBox(RectPlotSettings)
        self.min_sb.setObjectName(u"min_sb")
        self.min_sb.setMinimum(-1000000.000000000000000)
        self.min_sb.setMaximum(1000000.000000000000000)
        self.min_sb.setSingleStep(0.250000000000000)
        self.min_sb.setValue(0.000000000000000)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.min_sb)

        self.max_label = QLabel(RectPlotSettings)
        self.max_label.setObjectName(u"max_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.max_label)

        self.max_sb = QDoubleSpinBox(RectPlotSettings)
        self.max_sb.setObjectName(u"max_sb")
        self.max_sb.setMinimum(-100000.000000000000000)
        self.max_sb.setMaximum(1000000.000000000000000)
        self.max_sb.setSingleStep(0.250000000000000)
        self.max_sb.setValue(1.000000000000000)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.max_sb)

        self.label_8 = QLabel(RectPlotSettings)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_8)

        self.autoscale_checkbox = QCheckBox(RectPlotSettings)
        self.autoscale_checkbox.setObjectName(u"autoscale_checkbox")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.autoscale_checkbox)


        self.verticalLayout.addLayout(self.formLayout)

        self.add_trace_btn = QPushButton(RectPlotSettings)
        self.add_trace_btn.setObjectName(u"add_trace_btn")

        self.verticalLayout.addWidget(self.add_trace_btn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(RectPlotSettings)

        QMetaObject.connectSlotsByName(RectPlotSettings)
    # setupUi

    def retranslateUi(self, RectPlotSettings):
        RectPlotSettings.setWindowTitle(QCoreApplication.translate("RectPlotSettings", u"Form", None))
        self.label.setText(QCoreApplication.translate("RectPlotSettings", u"Title", None))
        self.label_4.setText(QCoreApplication.translate("RectPlotSettings", u"Background Color", None))
        self.bg_color_btn.setText(QCoreApplication.translate("RectPlotSettings", u"PushButton", None))
        self.label_2.setText(QCoreApplication.translate("RectPlotSettings", u"X Axis", None))
        self.label_3.setText(QCoreApplication.translate("RectPlotSettings", u"Y Axis", None))
        self.min_label.setText(QCoreApplication.translate("RectPlotSettings", u"Y Minimum", None))
        self.max_label.setText(QCoreApplication.translate("RectPlotSettings", u"Y Maximum", None))
        self.label_8.setText(QCoreApplication.translate("RectPlotSettings", u"Autoscale", None))
        self.autoscale_checkbox.setText("")
        self.add_trace_btn.setText(QCoreApplication.translate("RectPlotSettings", u"Add Trace", None))
    # retranslateUi

