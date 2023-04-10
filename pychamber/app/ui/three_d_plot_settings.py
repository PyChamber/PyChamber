# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'three_d_plot_settings.ui'
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
    QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from ..widgets.frequency_lineedit import FrequencyLineEdit
from pyqtgraph import ColorButton

class Ui_ThreeDPlotSettings(object):
    def setupUi(self, ThreeDPlotSettings):
        if not ThreeDPlotSettings.objectName():
            ThreeDPlotSettings.setObjectName(u"ThreeDPlotSettings")
        ThreeDPlotSettings.resize(330, 525)
        self.verticalLayout = QVBoxLayout(ThreeDPlotSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label = QLabel(ThreeDPlotSettings)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label)

        self.title_le = QLineEdit(ThreeDPlotSettings)
        self.title_le.setObjectName(u"title_le")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.title_le)

        self.label_4 = QLabel(ThreeDPlotSettings)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.bg_color_btn = ColorButton(ThreeDPlotSettings)
        self.bg_color_btn.setObjectName(u"bg_color_btn")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.bg_color_btn)


        self.verticalLayout.addLayout(self.formLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.spherical_checkbox = QCheckBox(ThreeDPlotSettings)
        self.spherical_checkbox.setObjectName(u"spherical_checkbox")
        self.spherical_checkbox.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout.addWidget(self.spherical_checkbox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_9 = QLabel(ThreeDPlotSettings)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignCenter)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_9)

        self.freq_le = FrequencyLineEdit(ThreeDPlotSettings)
        self.freq_le.setObjectName(u"freq_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.freq_le)

        self.r_var_label = QLabel(ThreeDPlotSettings)
        self.r_var_label.setObjectName(u"r_var_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.r_var_label)

        self.r_var_cb = QComboBox(ThreeDPlotSettings)
        self.r_var_cb.setObjectName(u"r_var_cb")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.r_var_cb)

        self.pol_label = QLabel(ThreeDPlotSettings)
        self.pol_label.setObjectName(u"pol_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.pol_label)

        self.pol_cb = QComboBox(ThreeDPlotSettings)
        self.pol_cb.setObjectName(u"pol_cb")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.pol_cb)

        self.cmap_label = QLabel(ThreeDPlotSettings)
        self.cmap_label.setObjectName(u"cmap_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.cmap_label)

        self.cmap_cb = QComboBox(ThreeDPlotSettings)
        self.cmap_cb.setObjectName(u"cmap_cb")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.cmap_cb)

        self.min_label = QLabel(ThreeDPlotSettings)
        self.min_label.setObjectName(u"min_label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.min_label)

        self.min_sb = QDoubleSpinBox(ThreeDPlotSettings)
        self.min_sb.setObjectName(u"min_sb")
        self.min_sb.setMinimum(-1000000.000000000000000)
        self.min_sb.setMaximum(1000000.000000000000000)
        self.min_sb.setSingleStep(0.250000000000000)
        self.min_sb.setValue(0.000000000000000)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.min_sb)

        self.max_label = QLabel(ThreeDPlotSettings)
        self.max_label.setObjectName(u"max_label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.max_label)

        self.max_sb = QDoubleSpinBox(ThreeDPlotSettings)
        self.max_sb.setObjectName(u"max_sb")
        self.max_sb.setMinimum(-100000.000000000000000)
        self.max_sb.setMaximum(1000000.000000000000000)
        self.max_sb.setSingleStep(0.250000000000000)
        self.max_sb.setValue(1.000000000000000)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.max_sb)

        self.label_8 = QLabel(ThreeDPlotSettings)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_8)

        self.calibrated_checkbox = QCheckBox(ThreeDPlotSettings)
        self.calibrated_checkbox.setObjectName(u"calibrated_checkbox")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.calibrated_checkbox)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(ThreeDPlotSettings)

        QMetaObject.connectSlotsByName(ThreeDPlotSettings)
    # setupUi

    def retranslateUi(self, ThreeDPlotSettings):
        ThreeDPlotSettings.setWindowTitle(QCoreApplication.translate("ThreeDPlotSettings", u"Form", None))
        self.label.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Title", None))
        self.label_4.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Background Color", None))
        self.bg_color_btn.setText(QCoreApplication.translate("ThreeDPlotSettings", u"PushButton", None))
        self.spherical_checkbox.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Spherical", None))
        self.label_9.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Frequency", None))
        self.r_var_label.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Z Variable", None))
        self.pol_label.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Polarization", None))
        self.cmap_label.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Colormap", None))
        self.min_label.setText(QCoreApplication.translate("ThreeDPlotSettings", u"R Minimum", None))
        self.max_label.setText(QCoreApplication.translate("ThreeDPlotSettings", u"R Maximum", None))
        self.label_8.setText(QCoreApplication.translate("ThreeDPlotSettings", u"Calibrated", None))
        self.calibrated_checkbox.setText("")
    # retranslateUi

