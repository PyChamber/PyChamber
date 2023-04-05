# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cal_wizard.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
    QWizard, QWizardPage)

from pyqtgraph import PlotWidget

class Ui_CalWizard(object):
    def setupUi(self, CalWizard):
        if not CalWizard.objectName():
            CalWizard.setObjectName(u"CalWizard")
        CalWizard.resize(638, 560)
        CalWizard.setModal(True)
        CalWizard.setWizardStyle(QWizard.AeroStyle)
        self.intro_pg = QWizardPage()
        self.intro_pg.setObjectName(u"intro_pg")
        self.verticalLayout = QVBoxLayout(self.intro_pg)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.intro_pg)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        CalWizard.addPage(self.intro_pg)
        self.setup_pg = QWizardPage()
        self.setup_pg.setObjectName(u"setup_pg")
        self.verticalLayout_2 = QVBoxLayout(self.setup_pg)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.setup_pg)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_2.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.label_2)

        CalWizard.addPage(self.setup_pg)
        self.notes_pg = QWizardPage()
        self.notes_pg.setObjectName(u"notes_pg")
        self.verticalLayout_3 = QVBoxLayout(self.notes_pg)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_3 = QLabel(self.notes_pg)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setTextFormat(Qt.RichText)
        self.label_3.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.label_3)

        self.notes_pte = QPlainTextEdit(self.notes_pg)
        self.notes_pte.setObjectName(u"notes_pte")

        self.verticalLayout_3.addWidget(self.notes_pte)

        CalWizard.addPage(self.notes_pg)
        self.reference_pg = QWizardPage()
        self.reference_pg.setObjectName(u"reference_pg")
        self.verticalLayout_4 = QVBoxLayout(self.reference_pg)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_4 = QLabel(self.reference_pg)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"QLabel {\n"
"	margin-bottom: 15px;\n"
"}")
        self.label_4.setTextFormat(Qt.RichText)
        self.label_4.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.label_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 15)
        self.label_5 = QLabel(self.reference_pg)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout.addWidget(self.label_5)

        self.ref_ant_label = QLabel(self.reference_pg)
        self.ref_ant_label.setObjectName(u"ref_ant_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ref_ant_label.sizePolicy().hasHeightForWidth())
        self.ref_ant_label.setSizePolicy(sizePolicy1)
        self.ref_ant_label.setFrameShape(QFrame.StyledPanel)

        self.horizontalLayout.addWidget(self.ref_ant_label)

        self.ref_ant_browse_btn = QPushButton(self.reference_pg)
        self.ref_ant_browse_btn.setObjectName(u"ref_ant_browse_btn")

        self.horizontalLayout.addWidget(self.ref_ant_browse_btn)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.ref_ant_plot = PlotWidget(self.reference_pg)
        self.ref_ant_plot.setObjectName(u"ref_ant_plot")

        self.verticalLayout_4.addWidget(self.ref_ant_plot)

        CalWizard.addPage(self.reference_pg)
        self.cal_pg = QWizardPage()
        self.cal_pg.setObjectName(u"cal_pg")
        self.verticalLayout_6 = QVBoxLayout(self.cal_pg)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_6 = QLabel(self.cal_pg)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setStyleSheet(u"QLabel {\n"
"	margin-bottom: 5px;\n"
"}")
        self.label_6.setTextFormat(Qt.RichText)
        self.label_6.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.label_6)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_7 = QLabel(self.cal_pg)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_2.addWidget(self.label_7)

        self.pol1_le = QLineEdit(self.cal_pg)
        self.pol1_le.setObjectName(u"pol1_le")

        self.horizontalLayout_2.addWidget(self.pol1_le)

        self.pol1_cb = QComboBox(self.cal_pg)
        self.pol1_cb.setObjectName(u"pol1_cb")
        self.pol1_cb.setMinimumSize(QSize(75, 0))
        self.pol1_cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_2.addWidget(self.pol1_cb)


        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 15)
        self.label_8 = QLabel(self.cal_pg)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_3.addWidget(self.label_8)

        self.pol2_le = QLineEdit(self.cal_pg)
        self.pol2_le.setObjectName(u"pol2_le")

        self.horizontalLayout_3.addWidget(self.pol2_le)

        self.pol2_cb = QComboBox(self.cal_pg)
        self.pol2_cb.setObjectName(u"pol2_cb")
        self.pol2_cb.setMinimumSize(QSize(75, 0))
        self.pol2_cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.horizontalLayout_3.addWidget(self.pol2_cb)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.loss_plot = PlotWidget(self.cal_pg)
        self.loss_plot.setObjectName(u"loss_plot")

        self.horizontalLayout_4.addWidget(self.loss_plot)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.meas_pol1_btn = QPushButton(self.cal_pg)
        self.meas_pol1_btn.setObjectName(u"meas_pol1_btn")
        self.meas_pol1_btn.setEnabled(False)

        self.verticalLayout_5.addWidget(self.meas_pol1_btn)

        self.meas_pol2_btn = QPushButton(self.cal_pg)
        self.meas_pol2_btn.setObjectName(u"meas_pol2_btn")
        self.meas_pol2_btn.setEnabled(False)

        self.verticalLayout_5.addWidget(self.meas_pol2_btn)

        self.save_cal_btn = QPushButton(self.cal_pg)
        self.save_cal_btn.setObjectName(u"save_cal_btn")
        self.save_cal_btn.setEnabled(False)

        self.verticalLayout_5.addWidget(self.save_cal_btn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)


        self.horizontalLayout_4.addLayout(self.verticalLayout_5)


        self.verticalLayout_6.addLayout(self.horizontalLayout_4)

        CalWizard.addPage(self.cal_pg)

        self.retranslateUi(CalWizard)

        QMetaObject.connectSlotsByName(CalWizard)
    # setupUi

    def retranslateUi(self, CalWizard):
        CalWizard.setWindowTitle(QCoreApplication.translate("CalWizard", u"Wizard", None))
        self.intro_pg.setTitle(QCoreApplication.translate("CalWizard", u"Introduction", None))
        self.label.setText(QCoreApplication.translate("CalWizard", u"This wizard will walk you through the procedure for generating a calibration file to offset losses. This is only one way to do a chamber calibration, but it is the only one supported at this time.\n"
"\n"
" This type of calibration works by measuring the response of an antenna with known characteristics and measuring the difference between the manufacurer specified gain and what is actually received. That difference is a determination of the loss in the system over frequency.", None))
        self.setup_pg.setTitle(QCoreApplication.translate("CalWizard", u"Setup", None))
        self.label_2.setText(QCoreApplication.translate("CalWizard", u"First, set up your instrument with the proper configuration (e.g. frequencies, power level, IF bandwidth, etc.).\n"
"\n"
"Next, align your antennas as accurately as possible so they are pointing at each other perfectly. A laser is helpful here. The more accurate your setup, the better your calibration.", None))
        self.notes_pg.setTitle(QCoreApplication.translate("CalWizard", u"Notes", None))
        self.label_3.setText(QCoreApplication.translate("CalWizard", u"Here, you can record some notes detailing the setup. These are optional, but it is highly recommended to take detailed notes on the setup. These notes will be stored in the calibration file. Good things to include: \n"
"<ul>\n"
"<li>Cables used</li>\n"
"Connectors used</li>\n"
"<li>What ports were used for what</li>\n"
"<li>Other equipment present (e.g. amplifiers)</li>\n"
"<li>Links to any relevant datasheets</li>\n"
"</ul>", None))
        self.reference_pg.setTitle(QCoreApplication.translate("CalWizard", u"Reference Antenna", None))
        self.label_4.setText(QCoreApplication.translate("CalWizard", u"<html><head/><body><p>First, load the file containing the gain information of the reference antenna. This must be a csv of <span style=\" font-style:italic;\">frequency [GHz],magnitude [dB]</span></p></body></html>", None))
        self.label_5.setText(QCoreApplication.translate("CalWizard", u"Reference gain file", None))
        self.ref_ant_label.setText("")
        self.ref_ant_browse_btn.setText(QCoreApplication.translate("CalWizard", u"Browse", None))
        self.cal_pg.setTitle(QCoreApplication.translate("CalWizard", u"Calibration", None))
        self.label_6.setText(QCoreApplication.translate("CalWizard", u"<html><head/><body><p>Now we'll capture the data and combine it with the information from the reference gain file to determine the loss of the system.</p><p>You must save the calibration to a file to finish the wizard.</p></body></html>", None))
        self.label_7.setText(QCoreApplication.translate("CalWizard", u"Polarization 1", None))
        self.pol1_le.setPlaceholderText(QCoreApplication.translate("CalWizard", u"Label (e.g. Vertical)", None))
        self.label_8.setText(QCoreApplication.translate("CalWizard", u"Polarization 2", None))
        self.pol2_le.setPlaceholderText(QCoreApplication.translate("CalWizard", u"Label", None))
        self.meas_pol1_btn.setText(QCoreApplication.translate("CalWizard", u"Measure 1", None))
        self.meas_pol2_btn.setText(QCoreApplication.translate("CalWizard", u"Measure 2", None))
        self.save_cal_btn.setText(QCoreApplication.translate("CalWizard", u"Save", None))
    # retranslateUi

