# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'positioner_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGroupBox, QHBoxLayout, QLCDNumber,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from ..widgets.category_combobox import CategoryComboBox

class Ui_PositionerWidget(object):
    def setupUi(self, PositionerWidget):
        if not PositionerWidget.objectName():
            PositionerWidget.setObjectName(u"PositionerWidget")
        PositionerWidget.resize(595, 409)
        self.verticalLayout_4 = QVBoxLayout(PositionerWidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.model_label = QLabel(PositionerWidget)
        self.model_label.setObjectName(u"model_label")

        self.horizontalLayout.addWidget(self.model_label)

        self.model_cb = CategoryComboBox(PositionerWidget)
        self.model_cb.setObjectName(u"model_cb")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model_cb.sizePolicy().hasHeightForWidth())
        self.model_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.model_cb)

        self.address_label = QLabel(PositionerWidget)
        self.address_label.setObjectName(u"address_label")

        self.horizontalLayout.addWidget(self.address_label)

        self.address_cb = QComboBox(PositionerWidget)
        self.address_cb.setObjectName(u"address_cb")
        sizePolicy.setHeightForWidth(self.address_cb.sizePolicy().hasHeightForWidth())
        self.address_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.address_cb)

        self.connect_btn = QPushButton(PositionerWidget)
        self.connect_btn.setObjectName(u"connect_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connect_btn.sizePolicy().hasHeightForWidth())
        self.connect_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton(PositionerWidget)
        self.disconnect_btn.setObjectName(u"disconnect_btn")

        self.horizontalLayout.addWidget(self.disconnect_btn)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.controls_widget = QWidget(PositionerWidget)
        self.controls_widget.setObjectName(u"controls_widget")
        self.controls_layout = QVBoxLayout(self.controls_widget)
        self.controls_layout.setObjectName(u"controls_layout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.phi_gb = QGroupBox(self.controls_widget)
        self.phi_gb.setObjectName(u"phi_gb")
        self.verticalLayout = QVBoxLayout(self.phi_gb)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.current_phi_lcd_num = QLCDNumber(self.phi_gb)
        self.current_phi_lcd_num.setObjectName(u"current_phi_lcd_num")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.current_phi_lcd_num.sizePolicy().hasHeightForWidth())
        self.current_phi_lcd_num.setSizePolicy(sizePolicy2)
        self.current_phi_lcd_num.setMinimumSize(QSize(0, 50))
        self.current_phi_lcd_num.setFrameShadow(QFrame.Plain)
        self.current_phi_lcd_num.setSegmentStyle(QLCDNumber.Flat)
        self.current_phi_lcd_num.setProperty("intValue", 0)

        self.verticalLayout.addWidget(self.current_phi_lcd_num)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.phi_step_label = QLabel(self.phi_gb)
        self.phi_step_label.setObjectName(u"phi_step_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.phi_step_label)

        self.phi_step_dsb = QDoubleSpinBox(self.phi_gb)
        self.phi_step_dsb.setObjectName(u"phi_step_dsb")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.phi_step_dsb.sizePolicy().hasHeightForWidth())
        self.phi_step_dsb.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setPointSize(12)
        self.phi_step_dsb.setFont(font)
        self.phi_step_dsb.setMaximum(180.000000000000000)
        self.phi_step_dsb.setSingleStep(0.500000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.phi_step_dsb)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.phi_minus_btn = QPushButton(self.phi_gb)
        self.phi_minus_btn.setObjectName(u"phi_minus_btn")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.phi_minus_btn.sizePolicy().hasHeightForWidth())
        self.phi_minus_btn.setSizePolicy(sizePolicy4)
        self.phi_minus_btn.setIconSize(QSize(32, 32))
        self.phi_minus_btn.setFlat(False)

        self.horizontalLayout_2.addWidget(self.phi_minus_btn)

        self.phi_zero_btn = QPushButton(self.phi_gb)
        self.phi_zero_btn.setObjectName(u"phi_zero_btn")
        sizePolicy4.setHeightForWidth(self.phi_zero_btn.sizePolicy().hasHeightForWidth())
        self.phi_zero_btn.setSizePolicy(sizePolicy4)
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        self.phi_zero_btn.setFont(font1)
        self.phi_zero_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_2.addWidget(self.phi_zero_btn)

        self.phi_plus_btn = QPushButton(self.phi_gb)
        self.phi_plus_btn.setObjectName(u"phi_plus_btn")
        sizePolicy4.setHeightForWidth(self.phi_plus_btn.sizePolicy().hasHeightForWidth())
        self.phi_plus_btn.setSizePolicy(sizePolicy4)
        self.phi_plus_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_2.addWidget(self.phi_plus_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.phi_jog_to_label = QLabel(self.phi_gb)
        self.phi_jog_to_label.setObjectName(u"phi_jog_to_label")
        self.phi_jog_to_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.phi_jog_to_label)

        self.phi_jog_to_dsb = QDoubleSpinBox(self.phi_gb)
        self.phi_jog_to_dsb.setObjectName(u"phi_jog_to_dsb")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.phi_jog_to_dsb.sizePolicy().hasHeightForWidth())
        self.phi_jog_to_dsb.setSizePolicy(sizePolicy5)

        self.horizontalLayout_4.addWidget(self.phi_jog_to_dsb)

        self.phi_jog_to_btn = QPushButton(self.phi_gb)
        self.phi_jog_to_btn.setObjectName(u"phi_jog_to_btn")
        self.phi_jog_to_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_4.addWidget(self.phi_jog_to_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_6.addWidget(self.phi_gb)

        self.theta_gb = QGroupBox(self.controls_widget)
        self.theta_gb.setObjectName(u"theta_gb")
        self.verticalLayout_2 = QVBoxLayout(self.theta_gb)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.current_theta_lcd_num = QLCDNumber(self.theta_gb)
        self.current_theta_lcd_num.setObjectName(u"current_theta_lcd_num")
        sizePolicy2.setHeightForWidth(self.current_theta_lcd_num.sizePolicy().hasHeightForWidth())
        self.current_theta_lcd_num.setSizePolicy(sizePolicy2)
        self.current_theta_lcd_num.setMinimumSize(QSize(0, 50))
        self.current_theta_lcd_num.setFrameShadow(QFrame.Plain)
        self.current_theta_lcd_num.setLineWidth(1)
        self.current_theta_lcd_num.setSegmentStyle(QLCDNumber.Flat)

        self.verticalLayout_2.addWidget(self.current_theta_lcd_num)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.theta_step_label = QLabel(self.theta_gb)
        self.theta_step_label.setObjectName(u"theta_step_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.theta_step_label)

        self.theta_step_dsb = QDoubleSpinBox(self.theta_gb)
        self.theta_step_dsb.setObjectName(u"theta_step_dsb")
        sizePolicy3.setHeightForWidth(self.theta_step_dsb.sizePolicy().hasHeightForWidth())
        self.theta_step_dsb.setSizePolicy(sizePolicy3)
        self.theta_step_dsb.setFont(font)
        self.theta_step_dsb.setMaximum(180.000000000000000)
        self.theta_step_dsb.setSingleStep(0.500000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.theta_step_dsb)


        self.verticalLayout_2.addLayout(self.formLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.theta_minus_btn = QPushButton(self.theta_gb)
        self.theta_minus_btn.setObjectName(u"theta_minus_btn")
        sizePolicy4.setHeightForWidth(self.theta_minus_btn.sizePolicy().hasHeightForWidth())
        self.theta_minus_btn.setSizePolicy(sizePolicy4)
        self.theta_minus_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_3.addWidget(self.theta_minus_btn)

        self.theta_zero_btn = QPushButton(self.theta_gb)
        self.theta_zero_btn.setObjectName(u"theta_zero_btn")
        sizePolicy4.setHeightForWidth(self.theta_zero_btn.sizePolicy().hasHeightForWidth())
        self.theta_zero_btn.setSizePolicy(sizePolicy4)
        self.theta_zero_btn.setFont(font1)

        self.horizontalLayout_3.addWidget(self.theta_zero_btn)

        self.theta_plus_btn = QPushButton(self.theta_gb)
        self.theta_plus_btn.setObjectName(u"theta_plus_btn")
        sizePolicy4.setHeightForWidth(self.theta_plus_btn.sizePolicy().hasHeightForWidth())
        self.theta_plus_btn.setSizePolicy(sizePolicy4)
        self.theta_plus_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_3.addWidget(self.theta_plus_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.theta_jog_to_label = QLabel(self.theta_gb)
        self.theta_jog_to_label.setObjectName(u"theta_jog_to_label")
        self.theta_jog_to_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.theta_jog_to_label)

        self.theta_jog_to_dsb = QDoubleSpinBox(self.theta_gb)
        self.theta_jog_to_dsb.setObjectName(u"theta_jog_to_dsb")
        sizePolicy5.setHeightForWidth(self.theta_jog_to_dsb.sizePolicy().hasHeightForWidth())
        self.theta_jog_to_dsb.setSizePolicy(sizePolicy5)

        self.horizontalLayout_5.addWidget(self.theta_jog_to_dsb)

        self.theta_jog_to_btn = QPushButton(self.theta_gb)
        self.theta_jog_to_btn.setObjectName(u"theta_jog_to_btn")
        self.theta_jog_to_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.theta_jog_to_btn)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_6.addWidget(self.theta_gb)


        self.controls_layout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.set_origin_btn = QPushButton(self.controls_widget)
        self.set_origin_btn.setObjectName(u"set_origin_btn")

        self.horizontalLayout_7.addWidget(self.set_origin_btn)

        self.return_to_origin_btn = QPushButton(self.controls_widget)
        self.return_to_origin_btn.setObjectName(u"return_to_origin_btn")

        self.horizontalLayout_7.addWidget(self.return_to_origin_btn)


        self.controls_layout.addLayout(self.horizontalLayout_7)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.controls_layout.addItem(self.verticalSpacer)


        self.verticalLayout_4.addWidget(self.controls_widget)

        self.verticalLayout_4.setStretch(1, 1)

        self.retranslateUi(PositionerWidget)

        self.phi_minus_btn.setDefault(False)


        QMetaObject.connectSlotsByName(PositionerWidget)
    # setupUi

    def retranslateUi(self, PositionerWidget):
        PositionerWidget.setWindowTitle(QCoreApplication.translate("PositionerWidget", u"Form", None))
        self.model_label.setText(QCoreApplication.translate("PositionerWidget", u"Model", None))
        self.address_label.setText(QCoreApplication.translate("PositionerWidget", u"Address", None))
        self.connect_btn.setText(QCoreApplication.translate("PositionerWidget", u"Connect", None))
        self.disconnect_btn.setText(QCoreApplication.translate("PositionerWidget", u"Disconnect", None))
        self.phi_gb.setTitle(QCoreApplication.translate("PositionerWidget", u"Phi", None))
        self.phi_step_label.setText(QCoreApplication.translate("PositionerWidget", u"Step", None))
        self.phi_minus_btn.setText("")
        self.phi_zero_btn.setText(QCoreApplication.translate("PositionerWidget", u"0", None))
        self.phi_plus_btn.setText("")
        self.phi_jog_to_label.setText(QCoreApplication.translate("PositionerWidget", u"Jog To", None))
        self.phi_jog_to_btn.setText("")
        self.theta_gb.setTitle(QCoreApplication.translate("PositionerWidget", u"Theta", None))
        self.theta_step_label.setText(QCoreApplication.translate("PositionerWidget", u"Step", None))
        self.theta_minus_btn.setText("")
        self.theta_zero_btn.setText(QCoreApplication.translate("PositionerWidget", u"0", None))
        self.theta_plus_btn.setText("")
        self.theta_jog_to_label.setText(QCoreApplication.translate("PositionerWidget", u"Jog To", None))
        self.theta_jog_to_btn.setText("")
        self.set_origin_btn.setText(QCoreApplication.translate("PositionerWidget", u"Set 0,0", None))
        self.return_to_origin_btn.setText(QCoreApplication.translate("PositionerWidget", u"Return to 0,0", None))
    # retranslateUi

