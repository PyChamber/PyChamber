# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'polar_trace_settings.ui'
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

class Ui_PolarTraceSettings(object):
    def setupUi(self, PolarTraceSettings):
        if not PolarTraceSettings.objectName():
            PolarTraceSettings.setObjectName(u"PolarTraceSettings")
        PolarTraceSettings.resize(469, 151)
        self.horizontalLayout_3 = QHBoxLayout(PolarTraceSettings)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.groupBox = QGroupBox(PolarTraceSettings)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frequencyLabel = QLabel(self.groupBox)
        self.frequencyLabel.setObjectName(u"frequencyLabel")
        self.frequencyLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.frequencyLabel)

        self.freq_le = FrequencyLineEdit(self.groupBox)
        self.freq_le.setObjectName(u"freq_le")

        self.verticalLayout_5.addWidget(self.freq_le)


        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_6)

        self.pol_cb = QComboBox(self.groupBox)
        self.pol_cb.setObjectName(u"pol_cb")

        self.verticalLayout_2.addWidget(self.pol_cb)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 0)
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_4)

        self.calibrated_checkbox = QCheckBox(self.groupBox)
        self.calibrated_checkbox.setObjectName(u"calibrated_checkbox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.calibrated_checkbox.sizePolicy().hasHeightForWidth())
        self.calibrated_checkbox.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.calibrated_checkbox, 0, Qt.AlignHCenter)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_7.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.phi_widget = QWidget(self.groupBox)
        self.phi_widget.setObjectName(u"phi_widget")
        self.verticalLayout_9 = QVBoxLayout(self.phi_widget)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.phi_widget)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.label)

        self.phi_lsb = ListSpinBox(self.phi_widget)
        self.phi_lsb.setObjectName(u"phi_lsb")

        self.verticalLayout_9.addWidget(self.phi_lsb)


        self.horizontalLayout_2.addWidget(self.phi_widget)

        self.theta_widget = QWidget(self.groupBox)
        self.theta_widget.setObjectName(u"theta_widget")
        self.verticalLayout_8 = QVBoxLayout(self.theta_widget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_9 = QLabel(self.theta_widget)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_9)

        self.theta_lsb = ListSpinBox(self.theta_widget)
        self.theta_lsb.setObjectName(u"theta_lsb")

        self.verticalLayout_8.addWidget(self.theta_lsb)


        self.horizontalLayout_2.addWidget(self.theta_widget)

        self.verticalLayout_3 = QVBoxLayout()
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


        self.verticalLayout_7.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_3.addWidget(self.groupBox)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.remove_polar_trace = QPushButton(PolarTraceSettings)
        self.remove_polar_trace.setObjectName(u"remove_polar_trace")

        self.verticalLayout_6.addWidget(self.remove_polar_trace)


        self.horizontalLayout_3.addLayout(self.verticalLayout_6)


        self.retranslateUi(PolarTraceSettings)

        QMetaObject.connectSlotsByName(PolarTraceSettings)
    # setupUi

    def retranslateUi(self, PolarTraceSettings):
        PolarTraceSettings.setWindowTitle(QCoreApplication.translate("PolarTraceSettings", u"Form", None))
        self.frequencyLabel.setText(QCoreApplication.translate("PolarTraceSettings", u"Frequency", None))
        self.label_6.setText(QCoreApplication.translate("PolarTraceSettings", u"Polarization", None))
        self.label_4.setText(QCoreApplication.translate("PolarTraceSettings", u"Calibrated", None))
        self.calibrated_checkbox.setText("")
        self.label.setText(QCoreApplication.translate("PolarTraceSettings", u"Phi", None))
        self.label_9.setText(QCoreApplication.translate("PolarTraceSettings", u"Theta", None))
        self.label_2.setText(QCoreApplication.translate("PolarTraceSettings", u"Color", None))
        self.trace_color_btn.setText("")
        self.label_3.setText(QCoreApplication.translate("PolarTraceSettings", u"Width", None))
        self.trace_width_dsb.setSuffix(QCoreApplication.translate("PolarTraceSettings", u"px", None))
        self.remove_polar_trace.setText("")
    # retranslateUi

