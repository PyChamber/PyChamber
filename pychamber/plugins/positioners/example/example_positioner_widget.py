################################################################################
## Form generated from reading UI file 'example_positioner.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout


class Ui_ExamplePositionerWidget:
    def setupUi(self, ExamplePositionerWidget):
        if not ExamplePositionerWidget.objectName():
            ExamplePositionerWidget.setObjectName("ExamplePositionerWidget")
        ExamplePositionerWidget.resize(400, 124)
        self.verticalLayout = QVBoxLayout(ExamplePositionerWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(ExamplePositionerWidget)
        self.label.setObjectName("label")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(ExamplePositionerWidget)

        QMetaObject.connectSlotsByName(ExamplePositionerWidget)

    # setupUi

    def retranslateUi(self, ExamplePositionerWidget):
        ExamplePositionerWidget.setWindowTitle(QCoreApplication.translate("ExamplePositionerWidget", "Form", None))
        self.label.setText(
            QCoreApplication.translate(
                "ExamplePositionerWidget",
                "Example Positioner!\n"
                "With regular positioners, settings specific to the particular model would appear here",
                None,
            )
        )

    # retranslateUi
