################################################################################
## Form generated from reading UI file 'positioner_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from ..widgets.category_combobox import CategoryComboBox


class Ui_PositionerWidget:
    def setupUi(self, PositionerWidget):
        if not PositionerWidget.objectName():
            PositionerWidget.setObjectName("PositionerWidget")
        PositionerWidget.resize(432, 318)
        self.verticalLayout_3 = QVBoxLayout(PositionerWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.model_label = QLabel(PositionerWidget)
        self.model_label.setObjectName("model_label")

        self.horizontalLayout.addWidget(self.model_label)

        self.model_cb = CategoryComboBox(PositionerWidget)
        self.model_cb.setObjectName("model_cb")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model_cb.sizePolicy().hasHeightForWidth())
        self.model_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.model_cb)

        self.address_label = QLabel(PositionerWidget)
        self.address_label.setObjectName("address_label")

        self.horizontalLayout.addWidget(self.address_label)

        self.address_cb = QComboBox(PositionerWidget)
        self.address_cb.setObjectName("address_cb")
        sizePolicy.setHeightForWidth(self.address_cb.sizePolicy().hasHeightForWidth())
        self.address_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.address_cb)

        self.connect_btn = QPushButton(PositionerWidget)
        self.connect_btn.setObjectName("connect_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connect_btn.sizePolicy().hasHeightForWidth())
        self.connect_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton(PositionerWidget)
        self.disconnect_btn.setObjectName("disconnect_btn")

        self.horizontalLayout.addWidget(self.disconnect_btn)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.az_gb = QGroupBox(PositionerWidget)
        self.az_gb.setObjectName("az_gb")
        self.verticalLayout = QVBoxLayout(self.az_gb)
        self.verticalLayout.setObjectName("verticalLayout")
        self.current_az_lcd_num = QLCDNumber(self.az_gb)
        self.current_az_lcd_num.setObjectName("current_az_lcd_num")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.current_az_lcd_num.sizePolicy().hasHeightForWidth())
        self.current_az_lcd_num.setSizePolicy(sizePolicy2)
        self.current_az_lcd_num.setMinimumSize(QSize(0, 50))
        self.current_az_lcd_num.setFrameShadow(QFrame.Plain)
        self.current_az_lcd_num.setSegmentStyle(QLCDNumber.Flat)
        self.current_az_lcd_num.setProperty("intValue", 0)

        self.verticalLayout.addWidget(self.current_az_lcd_num)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.az_step_label = QLabel(self.az_gb)
        self.az_step_label.setObjectName("az_step_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.az_step_label)

        self.az_step_dsb = QDoubleSpinBox(self.az_gb)
        self.az_step_dsb.setObjectName("az_step_dsb")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.az_step_dsb.sizePolicy().hasHeightForWidth())
        self.az_step_dsb.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setPointSize(12)
        self.az_step_dsb.setFont(font)
        self.az_step_dsb.setMaximum(180.000000000000000)
        self.az_step_dsb.setSingleStep(0.500000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.az_step_dsb)

        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.az_left_btn = QPushButton(self.az_gb)
        self.az_left_btn.setObjectName("az_left_btn")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.az_left_btn.sizePolicy().hasHeightForWidth())
        self.az_left_btn.setSizePolicy(sizePolicy4)
        self.az_left_btn.setIconSize(QSize(32, 32))
        self.az_left_btn.setFlat(False)

        self.horizontalLayout_2.addWidget(self.az_left_btn)

        self.az_zero_btn = QPushButton(self.az_gb)
        self.az_zero_btn.setObjectName("az_zero_btn")
        sizePolicy4.setHeightForWidth(self.az_zero_btn.sizePolicy().hasHeightForWidth())
        self.az_zero_btn.setSizePolicy(sizePolicy4)
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        self.az_zero_btn.setFont(font1)
        self.az_zero_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_2.addWidget(self.az_zero_btn)

        self.az_right_btn = QPushButton(self.az_gb)
        self.az_right_btn.setObjectName("az_right_btn")
        sizePolicy4.setHeightForWidth(self.az_right_btn.sizePolicy().hasHeightForWidth())
        self.az_right_btn.setSizePolicy(sizePolicy4)
        self.az_right_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_2.addWidget(self.az_right_btn)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.az_jog_to_label = QLabel(self.az_gb)
        self.az_jog_to_label.setObjectName("az_jog_to_label")
        self.az_jog_to_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.az_jog_to_label)

        self.az_jog_to_le = QLineEdit(self.az_gb)
        self.az_jog_to_le.setObjectName("az_jog_to_le")
        sizePolicy4.setHeightForWidth(self.az_jog_to_le.sizePolicy().hasHeightForWidth())
        self.az_jog_to_le.setSizePolicy(sizePolicy4)

        self.horizontalLayout_4.addWidget(self.az_jog_to_le)

        self.az_jog_to_btn = QPushButton(self.az_gb)
        self.az_jog_to_btn.setObjectName("az_jog_to_btn")
        self.az_jog_to_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_4.addWidget(self.az_jog_to_btn)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6.addWidget(self.az_gb)

        self.el_gb = QGroupBox(PositionerWidget)
        self.el_gb.setObjectName("el_gb")
        self.verticalLayout_2 = QVBoxLayout(self.el_gb)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.current_el_lcd_num = QLCDNumber(self.el_gb)
        self.current_el_lcd_num.setObjectName("current_el_lcd_num")
        sizePolicy2.setHeightForWidth(self.current_el_lcd_num.sizePolicy().hasHeightForWidth())
        self.current_el_lcd_num.setSizePolicy(sizePolicy2)
        self.current_el_lcd_num.setMinimumSize(QSize(0, 50))
        self.current_el_lcd_num.setFrameShadow(QFrame.Plain)
        self.current_el_lcd_num.setLineWidth(1)
        self.current_el_lcd_num.setSegmentStyle(QLCDNumber.Flat)

        self.verticalLayout_2.addWidget(self.current_el_lcd_num)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.formLayout_2.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.el_step_label = QLabel(self.el_gb)
        self.el_step_label.setObjectName("el_step_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.el_step_label)

        self.el_step_dsb = QDoubleSpinBox(self.el_gb)
        self.el_step_dsb.setObjectName("el_step_dsb")
        sizePolicy3.setHeightForWidth(self.el_step_dsb.sizePolicy().hasHeightForWidth())
        self.el_step_dsb.setSizePolicy(sizePolicy3)
        self.el_step_dsb.setFont(font)
        self.el_step_dsb.setMaximum(180.000000000000000)
        self.el_step_dsb.setSingleStep(0.500000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.el_step_dsb)

        self.verticalLayout_2.addLayout(self.formLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.el_ccw_btn = QPushButton(self.el_gb)
        self.el_ccw_btn.setObjectName("el_ccw_btn")
        sizePolicy4.setHeightForWidth(self.el_ccw_btn.sizePolicy().hasHeightForWidth())
        self.el_ccw_btn.setSizePolicy(sizePolicy4)
        self.el_ccw_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_3.addWidget(self.el_ccw_btn)

        self.el_0_btn = QPushButton(self.el_gb)
        self.el_0_btn.setObjectName("el_0_btn")
        sizePolicy4.setHeightForWidth(self.el_0_btn.sizePolicy().hasHeightForWidth())
        self.el_0_btn.setSizePolicy(sizePolicy4)
        self.el_0_btn.setFont(font1)

        self.horizontalLayout_3.addWidget(self.el_0_btn)

        self.el_cw_btn = QPushButton(self.el_gb)
        self.el_cw_btn.setObjectName("el_cw_btn")
        sizePolicy4.setHeightForWidth(self.el_cw_btn.sizePolicy().hasHeightForWidth())
        self.el_cw_btn.setSizePolicy(sizePolicy4)
        self.el_cw_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_3.addWidget(self.el_cw_btn)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.el_jog_to_label = QLabel(self.el_gb)
        self.el_jog_to_label.setObjectName("el_jog_to_label")
        self.el_jog_to_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.el_jog_to_label)

        self.el_jog_to_le = QLineEdit(self.el_gb)
        self.el_jog_to_le.setObjectName("el_jog_to_le")
        sizePolicy4.setHeightForWidth(self.el_jog_to_le.sizePolicy().hasHeightForWidth())
        self.el_jog_to_le.setSizePolicy(sizePolicy4)

        self.horizontalLayout_5.addWidget(self.el_jog_to_le)

        self.el_jog_to_btn = QPushButton(self.el_gb)
        self.el_jog_to_btn.setObjectName("el_jog_to_btn")
        self.el_jog_to_btn.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.el_jog_to_btn)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6.addWidget(self.el_gb)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.set_origin_btn = QPushButton(PositionerWidget)
        self.set_origin_btn.setObjectName("set_origin_btn")

        self.horizontalLayout_7.addWidget(self.set_origin_btn)

        self.return_to_origin_btn = QPushButton(PositionerWidget)
        self.return_to_origin_btn.setObjectName("return_to_origin_btn")

        self.horizontalLayout_7.addWidget(self.return_to_origin_btn)

        self.verticalLayout_3.addLayout(self.horizontalLayout_7)

        self.retranslateUi(PositionerWidget)

        self.az_left_btn.setDefault(False)

        QMetaObject.connectSlotsByName(PositionerWidget)

    # setupUi

    def retranslateUi(self, PositionerWidget):
        PositionerWidget.setWindowTitle(QCoreApplication.translate("PositionerWidget", "Form", None))
        self.model_label.setText(QCoreApplication.translate("PositionerWidget", "Model", None))
        self.address_label.setText(QCoreApplication.translate("PositionerWidget", "Address", None))
        self.connect_btn.setText(QCoreApplication.translate("PositionerWidget", "Connect", None))
        self.disconnect_btn.setText(QCoreApplication.translate("PositionerWidget", "Disconnect", None))
        self.az_gb.setTitle(QCoreApplication.translate("PositionerWidget", "Azimuth", None))
        self.az_step_label.setText(QCoreApplication.translate("PositionerWidget", "Step", None))
        self.az_left_btn.setText("")
        self.az_zero_btn.setText(QCoreApplication.translate("PositionerWidget", "0", None))
        self.az_right_btn.setText("")
        self.az_jog_to_label.setText(QCoreApplication.translate("PositionerWidget", "Jog To", None))
        self.az_jog_to_btn.setText("")
        self.el_gb.setTitle(QCoreApplication.translate("PositionerWidget", "Elevation", None))
        self.el_step_label.setText(QCoreApplication.translate("PositionerWidget", "Step", None))
        self.el_ccw_btn.setText("")
        self.el_0_btn.setText(QCoreApplication.translate("PositionerWidget", "0", None))
        self.el_cw_btn.setText("")
        self.el_jog_to_label.setText(QCoreApplication.translate("PositionerWidget", "Jog To", None))
        self.el_jog_to_btn.setText("")
        self.set_origin_btn.setText(QCoreApplication.translate("PositionerWidget", "Set 0,0", None))
        self.return_to_origin_btn.setText(QCoreApplication.translate("PositionerWidget", "Return to 0,0", None))

    # retranslateUi
