################################################################################
## Form generated from reading UI file 'experiment_controls.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QRect,
)
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(742, 409)
        self.widget = QWidget(Form)
        self.widget.setObjectName("widget")
        self.widget.setGeometry(QRect(120, 110, 261, 58))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.widget)
        self.pushButton_3.setObjectName("pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.pushButton_4 = QPushButton(self.widget)
        self.pushButton_4.setObjectName("pushButton_4")

        self.verticalLayout.addWidget(self.pushButton_4)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.pushButton.setText(QCoreApplication.translate("Form", "Full Scan", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", "Scan Azimuth", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", "Scan Elevation", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", "Abort", None))

    # retranslateUi
