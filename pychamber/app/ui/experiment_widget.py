# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'experiment_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from ..widgets.toggle import Toggle

class Ui_ExperimentWidget(object):
    def setupUi(self, ExperimentWidget):
        if not ExperimentWidget.objectName():
            ExperimentWidget.setObjectName(u"ExperimentWidget")
        ExperimentWidget.resize(260, 477)
        self.verticalLayout_5 = QVBoxLayout(ExperimentWidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.extents_gb = QGroupBox(ExperimentWidget)
        self.extents_gb.setObjectName(u"extents_gb")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.extents_gb.sizePolicy().hasHeightForWidth())
        self.extents_gb.setSizePolicy(sizePolicy)
        self.extents_gb.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.extents_gb.setFlat(False)
        self.gridLayout = QGridLayout(self.extents_gb)
        self.gridLayout.setObjectName(u"gridLayout")
        self.theta_label = QLabel(self.extents_gb)
        self.theta_label.setObjectName(u"theta_label")
        sizePolicy.setHeightForWidth(self.theta_label.sizePolicy().hasHeightForWidth())
        self.theta_label.setSizePolicy(sizePolicy)
        self.theta_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.theta_label, 0, 2, 1, 1)

        self.step_label = QLabel(self.extents_gb)
        self.step_label.setObjectName(u"step_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.step_label.sizePolicy().hasHeightForWidth())
        self.step_label.setSizePolicy(sizePolicy1)
        self.step_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.step_label, 3, 0, 1, 1)

        self.phi_stop_dsb = QDoubleSpinBox(self.extents_gb)
        self.phi_stop_dsb.setObjectName(u"phi_stop_dsb")
        self.phi_stop_dsb.setMinimum(-180.000000000000000)
        self.phi_stop_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.phi_stop_dsb, 2, 1, 1, 1)

        self.theta_start_dsb = QDoubleSpinBox(self.extents_gb)
        self.theta_start_dsb.setObjectName(u"theta_start_dsb")
        self.theta_start_dsb.setMinimum(-180.000000000000000)
        self.theta_start_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.theta_start_dsb, 1, 2, 1, 1)

        self.phi_step_dsb = QDoubleSpinBox(self.extents_gb)
        self.phi_step_dsb.setObjectName(u"phi_step_dsb")
        self.phi_step_dsb.setMinimum(-180.000000000000000)
        self.phi_step_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.phi_step_dsb, 3, 1, 1, 1)

        self.stop_label = QLabel(self.extents_gb)
        self.stop_label.setObjectName(u"stop_label")
        sizePolicy1.setHeightForWidth(self.stop_label.sizePolicy().hasHeightForWidth())
        self.stop_label.setSizePolicy(sizePolicy1)
        self.stop_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.stop_label, 2, 0, 1, 1)

        self.phi_label = QLabel(self.extents_gb)
        self.phi_label.setObjectName(u"phi_label")
        sizePolicy.setHeightForWidth(self.phi_label.sizePolicy().hasHeightForWidth())
        self.phi_label.setSizePolicy(sizePolicy)
        self.phi_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.phi_label, 0, 1, 1, 1)

        self.theta_stop_dsb = QDoubleSpinBox(self.extents_gb)
        self.theta_stop_dsb.setObjectName(u"theta_stop_dsb")
        self.theta_stop_dsb.setMinimum(-180.000000000000000)
        self.theta_stop_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.theta_stop_dsb, 2, 2, 1, 1)

        self.theta_step_dsb = QDoubleSpinBox(self.extents_gb)
        self.theta_step_dsb.setObjectName(u"theta_step_dsb")
        self.theta_step_dsb.setMinimum(-180.000000000000000)
        self.theta_step_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.theta_step_dsb, 3, 2, 1, 1)

        self.start_label = QLabel(self.extents_gb)
        self.start_label.setObjectName(u"start_label")
        sizePolicy1.setHeightForWidth(self.start_label.sizePolicy().hasHeightForWidth())
        self.start_label.setSizePolicy(sizePolicy1)
        self.start_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.start_label, 1, 0, 1, 1)

        self.phi_start_dsb = QDoubleSpinBox(self.extents_gb)
        self.phi_start_dsb.setObjectName(u"phi_start_dsb")
        self.phi_start_dsb.setMinimum(-180.000000000000000)
        self.phi_start_dsb.setMaximum(180.000000000000000)

        self.gridLayout.addWidget(self.phi_start_dsb, 1, 1, 1, 1)

        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)

        self.verticalLayout_5.addWidget(self.extents_gb)

        self.polarizations_gb = QGroupBox(ExperimentWidget)
        self.polarizations_gb.setObjectName(u"polarizations_gb")
        self.verticalLayout_2 = QVBoxLayout(self.polarizations_gb)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pol1_label = QLabel(self.polarizations_gb)
        self.pol1_label.setObjectName(u"pol1_label")

        self.horizontalLayout.addWidget(self.pol1_label)

        self.pol1_le = QLineEdit(self.polarizations_gb)
        self.pol1_le.setObjectName(u"pol1_le")

        self.horizontalLayout.addWidget(self.pol1_le)

        self.pol1_cb = QComboBox(self.polarizations_gb)
        self.pol1_cb.setObjectName(u"pol1_cb")

        self.horizontalLayout.addWidget(self.pol1_cb)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pol2_label = QLabel(self.polarizations_gb)
        self.pol2_label.setObjectName(u"pol2_label")

        self.horizontalLayout_2.addWidget(self.pol2_label)

        self.pol2_le = QLineEdit(self.polarizations_gb)
        self.pol2_le.setObjectName(u"pol2_le")

        self.horizontalLayout_2.addWidget(self.pol2_le)

        self.pol2_cb = QComboBox(self.polarizations_gb)
        self.pol2_cb.setObjectName(u"pol2_cb")

        self.horizontalLayout_2.addWidget(self.pol2_cb)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout_5.addWidget(self.polarizations_gb)

        self.cal_gb = QGroupBox(ExperimentWidget)
        self.cal_gb.setObjectName(u"cal_gb")
        self.verticalLayout = QVBoxLayout(self.cal_gb)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.cal_file_label = QLabel(self.cal_gb)
        self.cal_file_label.setObjectName(u"cal_file_label")

        self.horizontalLayout_3.addWidget(self.cal_file_label)

        self.cal_file_le = QLineEdit(self.cal_gb)
        self.cal_file_le.setObjectName(u"cal_file_le")
        self.cal_file_le.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.cal_file_le)

        self.cal_file_browse_btn = QPushButton(self.cal_gb)
        self.cal_file_browse_btn.setObjectName(u"cal_file_browse_btn")
        self.cal_file_browse_btn.setStyleSheet(u"QPushButton {\n"
"	padding-left: 5px;\n"
"	padding-right: 5px;\n"
"	padding-top: 2px;\n"
"	padding-bottom: 3px;\n"
"}")
        self.cal_file_browse_btn.setIconSize(QSize(16, 16))
        self.cal_file_browse_btn.setFlat(False)

        self.horizontalLayout_3.addWidget(self.cal_file_browse_btn)

        self.cal_file_toggle = Toggle(self.cal_gb)
        self.cal_file_toggle.setObjectName(u"cal_file_toggle")
        self.cal_file_toggle.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.cal_file_toggle)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.cal_wizard_btn = QPushButton(self.cal_gb)
        self.cal_wizard_btn.setObjectName(u"cal_wizard_btn")

        self.horizontalLayout_4.addWidget(self.cal_wizard_btn)

        self.view_cal_btn = QPushButton(self.cal_gb)
        self.view_cal_btn.setObjectName(u"view_cal_btn")
        self.view_cal_btn.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.view_cal_btn)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.cal_pol1_widget = QWidget(self.cal_gb)
        self.cal_pol1_widget.setObjectName(u"cal_pol1_widget")
        self.verticalLayout_3 = QVBoxLayout(self.cal_pol1_widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_4 = QLabel(self.cal_pol1_widget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_6.addWidget(self.label_4)

        self.cal_pol1_label = QLabel(self.cal_pol1_widget)
        self.cal_pol1_label.setObjectName(u"cal_pol1_label")

        self.horizontalLayout_6.addWidget(self.cal_pol1_label)

        self.cal_pol2_label_3 = QLabel(self.cal_pol1_widget)
        self.cal_pol2_label_3.setObjectName(u"cal_pol2_label_3")

        self.horizontalLayout_6.addWidget(self.cal_pol2_label_3)

        self.cal_pol1_cb = QComboBox(self.cal_pol1_widget)
        self.cal_pol1_cb.setObjectName(u"cal_pol1_cb")

        self.horizontalLayout_6.addWidget(self.cal_pol1_cb)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)


        self.verticalLayout.addWidget(self.cal_pol1_widget)

        self.cal_pol2_widget = QWidget(self.cal_gb)
        self.cal_pol2_widget.setObjectName(u"cal_pol2_widget")
        self.verticalLayout_4 = QVBoxLayout(self.cal_pol2_widget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_5 = QLabel(self.cal_pol2_widget)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.cal_pol2_label = QLabel(self.cal_pol2_widget)
        self.cal_pol2_label.setObjectName(u"cal_pol2_label")

        self.horizontalLayout_7.addWidget(self.cal_pol2_label)

        self.cal_pol2_label_4 = QLabel(self.cal_pol2_widget)
        self.cal_pol2_label_4.setObjectName(u"cal_pol2_label_4")

        self.horizontalLayout_7.addWidget(self.cal_pol2_label_4)

        self.cal_pol2_cb = QComboBox(self.cal_pol2_widget)
        self.cal_pol2_cb.setObjectName(u"cal_pol2_cb")

        self.horizontalLayout_7.addWidget(self.cal_pol2_cb)


        self.verticalLayout_4.addLayout(self.horizontalLayout_7)


        self.verticalLayout.addWidget(self.cal_pol2_widget)


        self.verticalLayout_5.addWidget(self.cal_gb)


        self.retranslateUi(ExperimentWidget)

        QMetaObject.connectSlotsByName(ExperimentWidget)
    # setupUi

    def retranslateUi(self, ExperimentWidget):
        ExperimentWidget.setWindowTitle(QCoreApplication.translate("ExperimentWidget", u"Form", None))
        self.extents_gb.setTitle(QCoreApplication.translate("ExperimentWidget", u"Extents", None))
        self.theta_label.setText(QCoreApplication.translate("ExperimentWidget", u"Theta", None))
        self.step_label.setText(QCoreApplication.translate("ExperimentWidget", u"Step", None))
        self.stop_label.setText(QCoreApplication.translate("ExperimentWidget", u"Stop", None))
        self.phi_label.setText(QCoreApplication.translate("ExperimentWidget", u"Phi", None))
        self.start_label.setText(QCoreApplication.translate("ExperimentWidget", u"Start", None))
        self.polarizations_gb.setTitle(QCoreApplication.translate("ExperimentWidget", u"Polarizations", None))
        self.pol1_label.setText(QCoreApplication.translate("ExperimentWidget", u"Polarization 1", None))
        self.pol1_le.setPlaceholderText(QCoreApplication.translate("ExperimentWidget", u"Label (e.g. Vertical)", None))
        self.pol2_label.setText(QCoreApplication.translate("ExperimentWidget", u"Polarization 2", None))
        self.pol2_le.setPlaceholderText(QCoreApplication.translate("ExperimentWidget", u"Label", None))
        self.cal_gb.setTitle(QCoreApplication.translate("ExperimentWidget", u"Calibration", None))
        self.cal_file_label.setText(QCoreApplication.translate("ExperimentWidget", u"Calibration File", None))
        self.cal_file_browse_btn.setText(QCoreApplication.translate("ExperimentWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.cal_file_toggle.setToolTip(QCoreApplication.translate("ExperimentWidget", u" Turn calibration on/off. Disabled unless a calibration file is loaded", None))
#endif // QT_CONFIG(tooltip)
        self.cal_file_toggle.setText("")
        self.cal_wizard_btn.setText(QCoreApplication.translate("ExperimentWidget", u"Calibration Wizard", None))
        self.view_cal_btn.setText(QCoreApplication.translate("ExperimentWidget", u"View", None))
        self.label_4.setText(QCoreApplication.translate("ExperimentWidget", u"Apply", None))
        self.cal_pol1_label.setText(QCoreApplication.translate("ExperimentWidget", u"Pol 1", None))
        self.cal_pol2_label_3.setText(QCoreApplication.translate("ExperimentWidget", u"to", None))
        self.label_5.setText(QCoreApplication.translate("ExperimentWidget", u"Apply", None))
        self.cal_pol2_label.setText(QCoreApplication.translate("ExperimentWidget", u"Pol 2", None))
        self.cal_pol2_label_4.setText(QCoreApplication.translate("ExperimentWidget", u"to", None))
    # retranslateUi

