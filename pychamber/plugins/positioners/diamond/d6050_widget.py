################################################################################
## Form generated from reading UI file 'd6050_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from qtpy.QtCore import QCoreApplication, QMetaObject, QSize
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class Ui_D6050Widget:
    def setupUi(self, D6050Widget):
        if not D6050Widget.objectName():
            D6050Widget.setObjectName("D6050Widget")
        D6050Widget.resize(400, 168)
        self.verticalLayout = QVBoxLayout(D6050Widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.zaxis_gb = QGroupBox(D6050Widget)
        self.zaxis_gb.setObjectName("zaxis_gb")
        self.verticalLayout_2 = QVBoxLayout(self.zaxis_gb)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.z_minus_btn = QPushButton(self.zaxis_gb)
        self.z_minus_btn.setObjectName("z_minus_btn")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.z_minus_btn.sizePolicy().hasHeightForWidth())
        self.z_minus_btn.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.z_minus_btn)

        self.current_z_lcd_num = QLCDNumber(self.zaxis_gb)
        self.current_z_lcd_num.setObjectName("current_z_lcd_num")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.current_z_lcd_num.sizePolicy().hasHeightForWidth())
        self.current_z_lcd_num.setSizePolicy(sizePolicy1)
        self.current_z_lcd_num.setMinimumSize(QSize(0, 50))
        self.current_z_lcd_num.setFrameShadow(QFrame.Plain)
        self.current_z_lcd_num.setSegmentStyle(QLCDNumber.Flat)
        self.current_z_lcd_num.setProperty("value", 0.000000000000000)
        self.current_z_lcd_num.setProperty("intValue", 0)

        self.horizontalLayout.addWidget(self.current_z_lcd_num)

        self.z_plus_btn = QPushButton(self.zaxis_gb)
        self.z_plus_btn.setObjectName("z_plus_btn")
        sizePolicy.setHeightForWidth(self.z_plus_btn.sizePolicy().hasHeightForWidth())
        self.z_plus_btn.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.z_plus_btn)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.z_step_label = QLabel(self.zaxis_gb)
        self.z_step_label.setObjectName("z_step_label")

        self.verticalLayout_2.addWidget(self.z_step_label)

        self.z_step_dsb = QDoubleSpinBox(self.zaxis_gb)
        self.z_step_dsb.setObjectName("z_step_dsb")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.z_step_dsb.sizePolicy().hasHeightForWidth())
        self.z_step_dsb.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setPointSize(12)
        self.z_step_dsb.setFont(font)
        self.z_step_dsb.setMaximum(180.000000000000000)
        self.z_step_dsb.setSingleStep(0.500000000000000)

        self.verticalLayout_2.addWidget(self.z_step_dsb)

        self.verticalLayout_2.setStretch(0, 1)

        self.verticalLayout.addWidget(self.zaxis_gb)

        self.retranslateUi(D6050Widget)

        QMetaObject.connectSlotsByName(D6050Widget)

    # setupUi

    def retranslateUi(self, D6050Widget):
        D6050Widget.setWindowTitle(QCoreApplication.translate("D6050Widget", "Form", None))
        self.zaxis_gb.setTitle(QCoreApplication.translate("D6050Widget", "Z Axis", None))
        self.z_minus_btn.setText("")
        self.z_plus_btn.setText("")
        self.z_step_label.setText(QCoreApplication.translate("D6050Widget", "Step", None))
        self.z_step_dsb.setSuffix(QCoreApplication.translate("D6050Widget", " mm", None))

    # retranslateUi
