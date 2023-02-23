################################################################################
## Form generated from reading UI file 'experiment_widget.ui'
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
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from ..widgets.filebrowse_lineedit import FileBrowseLineEdit
from ..widgets.toggle import Toggle


class Ui_ExperimentWidget:
    def setupUi(self, ExperimentWidget):
        if not ExperimentWidget.objectName():
            ExperimentWidget.setObjectName("ExperimentWidget")
        ExperimentWidget.resize(311, 483)
        self.verticalLayout = QVBoxLayout(ExperimentWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.extents_gb = QGroupBox(ExperimentWidget)
        self.extents_gb.setObjectName("extents_gb")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.extents_gb.sizePolicy().hasHeightForWidth())
        self.extents_gb.setSizePolicy(sizePolicy)
        self.extents_gb.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.extents_gb.setFlat(False)
        self.gridLayout = QGridLayout(self.extents_gb)
        self.gridLayout.setObjectName("gridLayout")
        self.el_label = QLabel(self.extents_gb)
        self.el_label.setObjectName("el_label")
        sizePolicy.setHeightForWidth(self.el_label.sizePolicy().hasHeightForWidth())
        self.el_label.setSizePolicy(sizePolicy)
        self.el_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.el_label, 0, 2, 1, 1)

        self.step_label = QLabel(self.extents_gb)
        self.step_label.setObjectName("step_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.step_label.sizePolicy().hasHeightForWidth())
        self.step_label.setSizePolicy(sizePolicy1)
        self.step_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.step_label, 3, 0, 1, 1)

        self.az_stop_dsb = QDoubleSpinBox(self.extents_gb)
        self.az_stop_dsb.setObjectName("az_stop_dsb")
        self.az_stop_dsb.setMinimum(-180.000000000000000)
        self.az_stop_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.az_stop_dsb, 2, 1, 1, 1)

        self.el_start_dsb = QDoubleSpinBox(self.extents_gb)
        self.el_start_dsb.setObjectName("el_start_dsb")
        self.el_start_dsb.setMinimum(-180.000000000000000)
        self.el_start_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.el_start_dsb, 1, 2, 1, 1)

        self.az_step_dsb = QDoubleSpinBox(self.extents_gb)
        self.az_step_dsb.setObjectName("az_step_dsb")
        self.az_step_dsb.setMinimum(-180.000000000000000)
        self.az_step_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.az_step_dsb, 3, 1, 1, 1)

        self.stop_label = QLabel(self.extents_gb)
        self.stop_label.setObjectName("stop_label")
        sizePolicy1.setHeightForWidth(self.stop_label.sizePolicy().hasHeightForWidth())
        self.stop_label.setSizePolicy(sizePolicy1)
        self.stop_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.stop_label, 2, 0, 1, 1)

        self.az_label = QLabel(self.extents_gb)
        self.az_label.setObjectName("az_label")
        sizePolicy.setHeightForWidth(self.az_label.sizePolicy().hasHeightForWidth())
        self.az_label.setSizePolicy(sizePolicy)
        self.az_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.az_label, 0, 1, 1, 1)

        self.el_stop_dsb = QDoubleSpinBox(self.extents_gb)
        self.el_stop_dsb.setObjectName("el_stop_dsb")
        self.el_stop_dsb.setMinimum(-180.000000000000000)
        self.el_stop_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.el_stop_dsb, 2, 2, 1, 1)

        self.el_step_dsb = QDoubleSpinBox(self.extents_gb)
        self.el_step_dsb.setObjectName("el_step_dsb")
        self.el_step_dsb.setMinimum(-180.000000000000000)
        self.el_step_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.el_step_dsb, 3, 2, 1, 1)

        self.start_label = QLabel(self.extents_gb)
        self.start_label.setObjectName("start_label")
        sizePolicy1.setHeightForWidth(self.start_label.sizePolicy().hasHeightForWidth())
        self.start_label.setSizePolicy(sizePolicy1)
        self.start_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.start_label, 1, 0, 1, 1)

        self.az_start_dsb = QDoubleSpinBox(self.extents_gb)
        self.az_start_dsb.setObjectName("az_start_dsb")
        self.az_start_dsb.setMinimum(-180.000000000000000)
        self.az_start_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.az_start_dsb, 1, 1, 1, 1)

        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)

        self.verticalLayout.addWidget(self.extents_gb)

        self.polarizations_gb = QGroupBox(ExperimentWidget)
        self.polarizations_gb.setObjectName("polarizations_gb")
        self.verticalLayout_2 = QVBoxLayout(self.polarizations_gb)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pol1_label = QLabel(self.polarizations_gb)
        self.pol1_label.setObjectName("pol1_label")

        self.horizontalLayout.addWidget(self.pol1_label)

        self.pol1_le = QLineEdit(self.polarizations_gb)
        self.pol1_le.setObjectName("pol1_le")

        self.horizontalLayout.addWidget(self.pol1_le)

        self.pol1_cb = QComboBox(self.polarizations_gb)
        self.pol1_cb.setObjectName("pol1_cb")

        self.horizontalLayout.addWidget(self.pol1_cb)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pol2_label = QLabel(self.polarizations_gb)
        self.pol2_label.setObjectName("pol2_label")

        self.horizontalLayout_2.addWidget(self.pol2_label)

        self.pol2_le = QLineEdit(self.polarizations_gb)
        self.pol2_le.setObjectName("pol2_le")

        self.horizontalLayout_2.addWidget(self.pol2_le)

        self.pol2_cb = QComboBox(self.polarizations_gb)
        self.pol2_cb.setObjectName("pol2_cb")

        self.horizontalLayout_2.addWidget(self.pol2_cb)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout.addWidget(self.polarizations_gb)

        self.cal_gb = QGroupBox(ExperimentWidget)
        self.cal_gb.setObjectName("cal_gb")
        self.verticalLayout_3 = QVBoxLayout(self.cal_gb)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cal_file_label = QLabel(self.cal_gb)
        self.cal_file_label.setObjectName("cal_file_label")

        self.horizontalLayout_3.addWidget(self.cal_file_label)

        self.cal_file_le = FileBrowseLineEdit(self.cal_gb)
        self.cal_file_le.setObjectName("cal_file_le")

        self.horizontalLayout_3.addWidget(self.cal_file_le)

        self.cal_file_toggle = Toggle(self.cal_gb)
        self.cal_file_toggle.setObjectName("cal_file_toggle")
        self.cal_file_toggle.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.cal_file_toggle)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.cal_wizard_btn = QPushButton(self.cal_gb)
        self.cal_wizard_btn.setObjectName("cal_wizard_btn")

        self.horizontalLayout_4.addWidget(self.cal_wizard_btn)

        self.view_cal_btn = QPushButton(self.cal_gb)
        self.view_cal_btn.setObjectName("view_cal_btn")
        self.view_cal_btn.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.view_cal_btn)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.verticalLayout.addWidget(self.cal_gb)

        self.retranslateUi(ExperimentWidget)

        QMetaObject.connectSlotsByName(ExperimentWidget)

    # setupUi

    def retranslateUi(self, ExperimentWidget):
        ExperimentWidget.setWindowTitle(QCoreApplication.translate("ExperimentWidget", "Form", None))
        self.extents_gb.setTitle(QCoreApplication.translate("ExperimentWidget", "Extents", None))
        self.el_label.setText(QCoreApplication.translate("ExperimentWidget", "Elevation", None))
        self.step_label.setText(QCoreApplication.translate("ExperimentWidget", "Step", None))
        self.stop_label.setText(QCoreApplication.translate("ExperimentWidget", "Stop", None))
        self.az_label.setText(QCoreApplication.translate("ExperimentWidget", "Azimuth", None))
        self.start_label.setText(QCoreApplication.translate("ExperimentWidget", "Start", None))
        self.polarizations_gb.setTitle(QCoreApplication.translate("ExperimentWidget", "Polarizations", None))
        self.pol1_label.setText(QCoreApplication.translate("ExperimentWidget", "Polarization 1", None))
        self.pol1_le.setPlaceholderText(QCoreApplication.translate("ExperimentWidget", "Label (e.g. Vertical)", None))
        self.pol2_label.setText(QCoreApplication.translate("ExperimentWidget", "Polarization 2", None))
        self.pol2_le.setPlaceholderText(QCoreApplication.translate("ExperimentWidget", "Label", None))
        self.cal_gb.setTitle(QCoreApplication.translate("ExperimentWidget", "Calibration", None))
        self.cal_file_label.setText(QCoreApplication.translate("ExperimentWidget", "Calibration File", None))
        # if QT_CONFIG(tooltip)
        self.cal_file_toggle.setToolTip(
            QCoreApplication.translate(
                "ExperimentWidget", " Turn calibration on/off. Disabled unless a calibration file is loaded", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cal_file_toggle.setText("")
        self.cal_wizard_btn.setText(QCoreApplication.translate("ExperimentWidget", "Calibration Wizard", None))
        self.view_cal_btn.setText(QCoreApplication.translate("ExperimentWidget", "View", None))

    # retranslateUi
