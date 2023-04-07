# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzer_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

from ..widgets.category_combobox import CategoryComboBox
from ..widgets.frequency_lineedit import FrequencyLineEdit
from ..widgets.toggle import Toggle

class Ui_AnalyzerWidget(object):
    def setupUi(self, AnalyzerWidget):
        if not AnalyzerWidget.objectName():
            AnalyzerWidget.setObjectName(u"AnalyzerWidget")
        AnalyzerWidget.resize(755, 617)
        self.verticalLayout = QVBoxLayout(AnalyzerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.model_label = QLabel(AnalyzerWidget)
        self.model_label.setObjectName(u"model_label")

        self.horizontalLayout.addWidget(self.model_label)

        self.model_cb = CategoryComboBox(AnalyzerWidget)
        self.model_cb.setObjectName(u"model_cb")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model_cb.sizePolicy().hasHeightForWidth())
        self.model_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.model_cb)

        self.address_label = QLabel(AnalyzerWidget)
        self.address_label.setObjectName(u"address_label")

        self.horizontalLayout.addWidget(self.address_label)

        self.address_cb = QComboBox(AnalyzerWidget)
        self.address_cb.setObjectName(u"address_cb")
        sizePolicy.setHeightForWidth(self.address_cb.sizePolicy().hasHeightForWidth())
        self.address_cb.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.address_cb)

        self.connect_btn = QPushButton(AnalyzerWidget)
        self.connect_btn.setObjectName(u"connect_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connect_btn.sizePolicy().hasHeightForWidth())
        self.connect_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton(AnalyzerWidget)
        self.disconnect_btn.setObjectName(u"disconnect_btn")
        self.disconnect_btn.setEnabled(True)

        self.horizontalLayout.addWidget(self.disconnect_btn)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.freq_gb = QGroupBox(AnalyzerWidget)
        self.freq_gb.setObjectName(u"freq_gb")
        self.formLayout = QFormLayout(self.freq_gb)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.freq_start_label = QLabel(self.freq_gb)
        self.freq_start_label.setObjectName(u"freq_start_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.freq_start_label)

        self.freq_start_le = FrequencyLineEdit(self.freq_gb)
        self.freq_start_le.setObjectName(u"freq_start_le")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.freq_start_le)

        self.freq_stop_le = FrequencyLineEdit(self.freq_gb)
        self.freq_stop_le.setObjectName(u"freq_stop_le")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.freq_stop_le)

        self.freq_step_le = FrequencyLineEdit(self.freq_gb)
        self.freq_step_le.setObjectName(u"freq_step_le")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.freq_step_le)

        self.freq_n_points_le = QLineEdit(self.freq_gb)
        self.freq_n_points_le.setObjectName(u"freq_n_points_le")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.freq_n_points_le)

        self.freq_stop_label = QLabel(self.freq_gb)
        self.freq_stop_label.setObjectName(u"freq_stop_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.freq_stop_label)

        self.freq_step_label = QLabel(self.freq_gb)
        self.freq_step_label.setObjectName(u"freq_step_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.freq_step_label)

        self.freq_n_points_label = QLabel(self.freq_gb)
        self.freq_n_points_label.setObjectName(u"freq_n_points_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.freq_n_points_label)


        self.verticalLayout.addWidget(self.freq_gb)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.if_bw_label = QLabel(AnalyzerWidget)
        self.if_bw_label.setObjectName(u"if_bw_label")
        self.if_bw_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.if_bw_label)

        self.if_bw_le = FrequencyLineEdit(AnalyzerWidget)
        self.if_bw_le.setObjectName(u"if_bw_le")

        self.horizontalLayout_2.addWidget(self.if_bw_le)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.freq_start_label_2 = QLabel(AnalyzerWidget)
        self.freq_start_label_2.setObjectName(u"freq_start_label_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.freq_start_label_2.sizePolicy().hasHeightForWidth())
        self.freq_start_label_2.setSizePolicy(sizePolicy2)
        self.freq_start_label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.freq_start_label_2)

        self.avg_toggle = Toggle(AnalyzerWidget)
        self.avg_toggle.setObjectName(u"avg_toggle")
        self.avg_toggle.setEnabled(True)

        self.horizontalLayout_3.addWidget(self.avg_toggle)

        self.freq_start_label_3 = QLabel(AnalyzerWidget)
        self.freq_start_label_3.setObjectName(u"freq_start_label_3")
        sizePolicy2.setHeightForWidth(self.freq_start_label_3.sizePolicy().hasHeightForWidth())
        self.freq_start_label_3.setSizePolicy(sizePolicy2)
        self.freq_start_label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.freq_start_label_3)

        self.n_avgs_sb = QSpinBox(AnalyzerWidget)
        self.n_avgs_sb.setObjectName(u"n_avgs_sb")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.n_avgs_sb.sizePolicy().hasHeightForWidth())
        self.n_avgs_sb.setSizePolicy(sizePolicy3)
        self.n_avgs_sb.setMinimum(1)
        self.n_avgs_sb.setMaximum(100)

        self.horizontalLayout_3.addWidget(self.n_avgs_sb)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(AnalyzerWidget)

        QMetaObject.connectSlotsByName(AnalyzerWidget)
    # setupUi

    def retranslateUi(self, AnalyzerWidget):
        AnalyzerWidget.setWindowTitle(QCoreApplication.translate("AnalyzerWidget", u"Form", None))
        self.model_label.setText(QCoreApplication.translate("AnalyzerWidget", u"Model", None))
        self.address_label.setText(QCoreApplication.translate("AnalyzerWidget", u"Address", None))
        self.connect_btn.setText(QCoreApplication.translate("AnalyzerWidget", u"Connect", None))
        self.disconnect_btn.setText(QCoreApplication.translate("AnalyzerWidget", u"Disconnect", None))
        self.freq_gb.setTitle(QCoreApplication.translate("AnalyzerWidget", u"Frequency", None))
        self.freq_start_label.setText(QCoreApplication.translate("AnalyzerWidget", u"Start", None))
        self.freq_stop_label.setText(QCoreApplication.translate("AnalyzerWidget", u"Stop", None))
        self.freq_step_label.setText(QCoreApplication.translate("AnalyzerWidget", u"Step", None))
        self.freq_n_points_label.setText(QCoreApplication.translate("AnalyzerWidget", u"Num. of Points", None))
        self.if_bw_label.setText(QCoreApplication.translate("AnalyzerWidget", u"IF Bandwidth", None))
        self.freq_start_label_2.setText(QCoreApplication.translate("AnalyzerWidget", u"Averaging", None))
#if QT_CONFIG(tooltip)
        self.avg_toggle.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.avg_toggle.setText("")
        self.freq_start_label_3.setText(QCoreApplication.translate("AnalyzerWidget", u"Number of Samples", None))
    # retranslateUi

