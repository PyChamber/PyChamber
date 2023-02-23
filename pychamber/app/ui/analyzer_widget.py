################################################################################
## Form generated from reading UI file 'analyzer_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    Qt,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from ..widgets.category_combobox import CategoryComboBox
from ..widgets.frequency_lineedit import FrequencyLineEdit


class Ui_AnalyzerWidget:
    def setupUi(self, AnalyzerWidget):
        if not AnalyzerWidget.objectName():
            AnalyzerWidget.setObjectName("AnalyzerWidget")
        AnalyzerWidget.resize(455, 265)
        self.verticalLayout = QVBoxLayout(AnalyzerWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.model_label = QLabel(AnalyzerWidget)
        self.model_label.setObjectName("model_label")

        self.horizontalLayout.addWidget(self.model_label)

        self.model_cb = CategoryComboBox(AnalyzerWidget)
        self.model_cb.setObjectName("model_cb")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model_cb.sizePolicy().hasHeightForWidth())
        self.model_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.model_cb)

        self.address_label = QLabel(AnalyzerWidget)
        self.address_label.setObjectName("address_label")

        self.horizontalLayout.addWidget(self.address_label)

        self.address_cb = QComboBox(AnalyzerWidget)
        self.address_cb.setObjectName("address_cb")
        sizePolicy.setHeightForWidth(self.address_cb.sizePolicy().hasHeightForWidth())
        self.address_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.address_cb)

        self.connect_btn = QPushButton(AnalyzerWidget)
        self.connect_btn.setObjectName("connect_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connect_btn.sizePolicy().hasHeightForWidth())
        self.connect_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton(AnalyzerWidget)
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.setEnabled(True)

        self.horizontalLayout.addWidget(self.disconnect_btn)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.freq_gb = QGroupBox(AnalyzerWidget)
        self.freq_gb.setObjectName("freq_gb")
        self.formLayout = QFormLayout(self.freq_gb)
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.freq_start_label = QLabel(self.freq_gb)
        self.freq_start_label.setObjectName("freq_start_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.freq_start_label)

        self.freq_start_le = FrequencyLineEdit(self.freq_gb)
        self.freq_start_le.setObjectName("freq_start_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.freq_start_le)

        self.freq_stop_le = FrequencyLineEdit(self.freq_gb)
        self.freq_stop_le.setObjectName("freq_stop_le")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.freq_stop_le)

        self.freq_step_le = FrequencyLineEdit(self.freq_gb)
        self.freq_step_le.setObjectName("freq_step_le")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.freq_step_le)

        self.freq_n_points_le = QLineEdit(self.freq_gb)
        self.freq_n_points_le.setObjectName("freq_n_points_le")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.freq_n_points_le)

        self.freq_stop_label = QLabel(self.freq_gb)
        self.freq_stop_label.setObjectName("freq_stop_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.freq_stop_label)

        self.freq_step_label = QLabel(self.freq_gb)
        self.freq_step_label.setObjectName("freq_step_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.freq_step_label)

        self.freq_n_points_label = QLabel(self.freq_gb)
        self.freq_n_points_label.setObjectName("freq_n_points_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.freq_n_points_label)

        self.verticalLayout.addWidget(self.freq_gb)

        self.retranslateUi(AnalyzerWidget)

        QMetaObject.connectSlotsByName(AnalyzerWidget)

    # setupUi

    def retranslateUi(self, AnalyzerWidget):
        AnalyzerWidget.setWindowTitle(QCoreApplication.translate("AnalyzerWidget", "Form", None))
        self.model_label.setText(QCoreApplication.translate("AnalyzerWidget", "Model", None))
        self.address_label.setText(QCoreApplication.translate("AnalyzerWidget", "Address", None))
        self.connect_btn.setText(QCoreApplication.translate("AnalyzerWidget", "Connect", None))
        self.disconnect_btn.setText(QCoreApplication.translate("AnalyzerWidget", "Disconnect", None))
        self.freq_gb.setTitle(QCoreApplication.translate("AnalyzerWidget", "Frequency", None))
        self.freq_start_label.setText(QCoreApplication.translate("AnalyzerWidget", "Start", None))
        self.freq_stop_label.setText(QCoreApplication.translate("AnalyzerWidget", "Stop", None))
        self.freq_step_label.setText(QCoreApplication.translate("AnalyzerWidget", "Step", None))
        self.freq_n_points_label.setText(QCoreApplication.translate("AnalyzerWidget", "Num. of Points", None))

    # retranslateUi
