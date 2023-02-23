################################################################################
## Form generated from reading UI file 'log_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
)
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout


class Ui_LogDialog:
    def setupUi(self, LogDialog):
        if not LogDialog.objectName():
            LogDialog.setObjectName("LogDialog")
        LogDialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(LogDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.log_pte = QPlainTextEdit(LogDialog)
        self.log_pte.setObjectName("log_pte")

        self.verticalLayout.addWidget(self.log_pte)

        self.retranslateUi(LogDialog)

        QMetaObject.connectSlotsByName(LogDialog)

    # setupUi

    def retranslateUi(self, LogDialog):
        LogDialog.setWindowTitle(QCoreApplication.translate("LogDialog", "PyChamber - Logs", None))

    # retranslateUi
