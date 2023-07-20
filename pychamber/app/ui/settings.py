# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QLabel, QSizePolicy,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(583, 451)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.West)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.general = QWidget()
        self.general.setObjectName(u"general")
        self.formLayout = QFormLayout(self.general)
        self.formLayout.setObjectName(u"formLayout")
        self.backend_label = QLabel(self.general)
        self.backend_label.setObjectName(u"backend_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.backend_label)

        self.backend_cb = QComboBox(self.general)
        self.backend_cb.setObjectName(u"backend_cb")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.backend_cb)

        self.theme_cb = QComboBox(self.general)
        self.theme_cb.addItem("")
        self.theme_cb.addItem("")
        self.theme_cb.setObjectName(u"theme_cb")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.theme_cb)

        self.theme_label = QLabel(self.general)
        self.theme_label.setObjectName(u"theme_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.theme_label)

        self.tabWidget.addTab(self.general, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.backend_label.setText(QCoreApplication.translate("Dialog", u"VISA Backend", None))
        self.theme_cb.setItemText(0, QCoreApplication.translate("Dialog", u"Light", None))
        self.theme_cb.setItemText(1, QCoreApplication.translate("Dialog", u"Dark", None))

        self.theme_label.setText(QCoreApplication.translate("Dialog", u"Theme", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general), QCoreApplication.translate("Dialog", u"General", None))
    # retranslateUi

