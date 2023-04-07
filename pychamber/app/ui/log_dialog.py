# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'log_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QPlainTextEdit, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_LogDialog(object):
    def setupUi(self, LogDialog):
        if not LogDialog.objectName():
            LogDialog.setObjectName(u"LogDialog")
        LogDialog.resize(650, 400)
        self.verticalLayout = QVBoxLayout(LogDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.log_pte = QPlainTextEdit(LogDialog)
        self.log_pte.setObjectName(u"log_pte")

        self.verticalLayout.addWidget(self.log_pte)


        self.retranslateUi(LogDialog)

        QMetaObject.connectSlotsByName(LogDialog)
    # setupUi

    def retranslateUi(self, LogDialog):
        LogDialog.setWindowTitle(QCoreApplication.translate("LogDialog", u"PyChamber - Logs", None))
    # retranslateUi

