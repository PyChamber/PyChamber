# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rect_trace_settings.ui'
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
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

from ..widgets.frequency_lineedit import FrequencyLineEdit
from ..widgets.list_spinbox import ListSpinBox
from pyqtgraph import ColorButton

class Ui_RectTraceSettings(object):
    def setupUi(self, RectTraceSettings):
        if not RectTraceSettings.objectName():
            RectTraceSettings.setObjectName(u"RectTraceSettings")
        RectTraceSettings.resize(402, 145)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RectTraceSettings.sizePolicy().hasHeightForWidth())
        RectTraceSettings.setSizePolicy(sizePolicy)
        self.horizontalLayout_4 = QHBoxLayout(RectTraceSettings)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupBox = QGroupBox(RectTraceSettings)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setAlignment(Qt.AlignCenter)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.phi_widget = QWidget(self.groupBox)
        self.phi_widget.setObjectName(u"phi_widget")
        self.verticalLayout_10 = QVBoxLayout(self.phi_widget)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.phi_widget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label)

        self.phi_lsb = ListSpinBox(self.phi_widget)
        self.phi_lsb.setObjectName(u"phi_lsb")

        self.verticalLayout_10.addWidget(self.phi_lsb)


        self.horizontalLayout.addWidget(self.phi_widget)

        self.theta_widget = QWidget(self.groupBox)
        self.theta_widget.setObjectName(u"theta_widget")
        self.verticalLayout_8 = QVBoxLayout(self.theta_widget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_10 = QLabel(self.theta_widget)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_10)

        self.theta_lsb = ListSpinBox(self.theta_widget)
        self.theta_lsb.setObjectName(u"theta_lsb")

        self.verticalLayout_8.addWidget(self.theta_lsb)


        self.horizontalLayout.addWidget(self.theta_widget)

        self.freq_widget = QWidget(self.groupBox)
        self.freq_widget.setObjectName(u"freq_widget")
        self.horizontalLayout_3 = QHBoxLayout(self.freq_widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_9 = QLabel(self.freq_widget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_9)

        self.freq_le = FrequencyLineEdit(self.freq_widget)
        self.freq_le.setObjectName(u"freq_le")

        self.verticalLayout_7.addWidget(self.freq_le)


        self.horizontalLayout_3.addLayout(self.verticalLayout_7)


        self.horizontalLayout.addWidget(self.freq_widget)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setSpacing(2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_6)

        self.pol_cb = QComboBox(self.groupBox)
        self.pol_cb.setObjectName(u"pol_cb")

        self.verticalLayout_6.addWidget(self.pol_cb)


        self.horizontalLayout.addLayout(self.verticalLayout_6)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)

        self.trace_color_btn = ColorButton(self.groupBox)
        self.trace_color_btn.setObjectName(u"trace_color_btn")

        self.verticalLayout_3.addWidget(self.trace_color_btn)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)

        self.trace_width_dsb = QDoubleSpinBox(self.groupBox)
        self.trace_width_dsb.setObjectName(u"trace_width_dsb")
        self.trace_width_dsb.setDecimals(1)
        self.trace_width_dsb.setValue(1.000000000000000)

        self.verticalLayout_4.addWidget(self.trace_width_dsb)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_4)

        self.calibrated_checkbox = QCheckBox(self.groupBox)
        self.calibrated_checkbox.setObjectName(u"calibrated_checkbox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.calibrated_checkbox.sizePolicy().hasHeightForWidth())
        self.calibrated_checkbox.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.calibrated_checkbox, 0, Qt.AlignHCenter)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_4.addWidget(self.groupBox)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.remove_rect_trace = QPushButton(RectTraceSettings)
        self.remove_rect_trace.setObjectName(u"remove_rect_trace")

        self.verticalLayout_9.addWidget(self.remove_rect_trace)


        self.horizontalLayout_4.addLayout(self.verticalLayout_9)


        self.retranslateUi(RectTraceSettings)

        QMetaObject.connectSlotsByName(RectTraceSettings)
    # setupUi

    def retranslateUi(self, RectTraceSettings):
        RectTraceSettings.setWindowTitle(QCoreApplication.translate("RectTraceSettings", u"Form", None))
        self.groupBox.setTitle("")
        self.label.setText(QCoreApplication.translate("RectTraceSettings", u"Phi", None))
        self.label_10.setText(QCoreApplication.translate("RectTraceSettings", u"Theta", None))
        self.label_9.setText(QCoreApplication.translate("RectTraceSettings", u"Frequency", None))
        self.label_6.setText(QCoreApplication.translate("RectTraceSettings", u"Polarization", None))
        self.label_2.setText(QCoreApplication.translate("RectTraceSettings", u"Color", None))
        self.trace_color_btn.setText("")
        self.label_3.setText(QCoreApplication.translate("RectTraceSettings", u"Width", None))
        self.trace_width_dsb.setSuffix(QCoreApplication.translate("RectTraceSettings", u"px", None))
        self.label_4.setText(QCoreApplication.translate("RectTraceSettings", u"Calibrated", None))
        self.calibrated_checkbox.setText("")
        self.remove_rect_trace.setText("")
    # retranslateUi

