################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QRect,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QPixmap,
)
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from pychamber.app.widgets import ControlsArea, PlotWidget


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1160, 886)
        self.save_action = QAction(MainWindow)
        self.save_action.setObjectName("save_action")
        self.load_action = QAction(MainWindow)
        self.load_action.setObjectName("load_action")
        self.export_action = QAction(MainWindow)
        self.export_action.setObjectName("export_action")
        self.exit_action = QAction(MainWindow)
        self.exit_action.setObjectName("exit_action")
        self.view_logs_action = QAction(MainWindow)
        self.view_logs_action.setObjectName("view_logs_action")
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout_6 = QVBoxLayout(self.central_widget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.splitter = QSplitter(self.central_widget)
        self.splitter.setObjectName("splitter")
        self.splitter.setAutoFillBackground(False)
        self.splitter.setStyleSheet(
            "QSplitter::handle:horizontal {\n"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
            "    stop:0 #eee, stop:1 #ccc);\n"
            "border: 1px solid #777;\n"
            "width: 13px;\n"
            "margin-left: 2px;\n"
            "margin-right: 2px;\n"
            "border-radius: 4px;\n"
            "}"
        )
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.left_pane = QWidget(self.splitter)
        self.left_pane.setObjectName("left_pane")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left_pane.sizePolicy().hasHeightForWidth())
        self.left_pane.setSizePolicy(sizePolicy)
        self.left_pane.setMinimumSize(QSize(400, 0))
        self.verticalLayout_5 = QVBoxLayout(self.left_pane)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.logo = QWidget(self.left_pane)
        self.logo.setObjectName("logo")
        self.horizontalLayout = QHBoxLayout(self.logo)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(5, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label = QLabel(self.logo)
        self.label.setObjectName("label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMaximumSize(QSize(205, 48))
        self.label.setPixmap(QPixmap(":/images/logo_dark_text.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(5, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout_5.addWidget(self.logo)

        self.experiment_buttons = QWidget(self.left_pane)
        self.experiment_buttons.setObjectName("experiment_buttons")
        self.verticalLayout_4 = QVBoxLayout(self.experiment_buttons)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.full_scan_btn = QPushButton(self.experiment_buttons)
        self.full_scan_btn.setObjectName("full_scan_btn")
        self.full_scan_btn.setEnabled(False)

        self.verticalLayout_4.addWidget(self.full_scan_btn)

        self.az_scan_btn = QPushButton(self.experiment_buttons)
        self.az_scan_btn.setObjectName("az_scan_btn")
        self.az_scan_btn.setEnabled(False)

        self.verticalLayout_4.addWidget(self.az_scan_btn)

        self.el_scan_btn = QPushButton(self.experiment_buttons)
        self.el_scan_btn.setObjectName("el_scan_btn")
        self.el_scan_btn.setEnabled(False)

        self.verticalLayout_4.addWidget(self.el_scan_btn)

        self.abort_btn = QPushButton(self.experiment_buttons)
        self.abort_btn.setObjectName("abort_btn")
        self.abort_btn.setEnabled(False)
        self.abort_btn.setAutoFillBackground(False)
        self.abort_btn.setStyleSheet("background-color: rgb(237, 51, 59)")

        self.verticalLayout_4.addWidget(self.abort_btn)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.total_progress_gb = QGroupBox(self.experiment_buttons)
        self.total_progress_gb.setObjectName("total_progress_gb")
        self.total_progress_gb.setAlignment(Qt.AlignCenter)
        self.total_progress_gb.setFlat(True)
        self.verticalLayout = QVBoxLayout(self.total_progress_gb)
        self.verticalLayout.setObjectName("verticalLayout")
        self.total_progress_bar = QProgressBar(self.total_progress_gb)
        self.total_progress_bar.setObjectName("total_progress_bar")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.total_progress_bar.sizePolicy().hasHeightForWidth())
        self.total_progress_bar.setSizePolicy(sizePolicy2)
        self.total_progress_bar.setValue(0)
        self.total_progress_bar.setAlignment(Qt.AlignCenter)
        self.total_progress_bar.setTextVisible(True)
        self.total_progress_bar.setOrientation(Qt.Horizontal)
        self.total_progress_bar.setTextDirection(QProgressBar.TopToBottom)

        self.verticalLayout.addWidget(self.total_progress_bar)

        self.horizontalLayout_2.addWidget(self.total_progress_gb)

        self.cut_progress_gb = QGroupBox(self.experiment_buttons)
        self.cut_progress_gb.setObjectName("cut_progress_gb")
        self.cut_progress_gb.setEnabled(True)
        self.cut_progress_gb.setAlignment(Qt.AlignCenter)
        self.cut_progress_gb.setFlat(True)
        self.cut_progress_gb.setCheckable(False)
        self.verticalLayout_2 = QVBoxLayout(self.cut_progress_gb)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cut_progress_bar = QProgressBar(self.cut_progress_gb)
        self.cut_progress_bar.setObjectName("cut_progress_bar")
        sizePolicy2.setHeightForWidth(self.cut_progress_bar.sizePolicy().hasHeightForWidth())
        self.cut_progress_bar.setSizePolicy(sizePolicy2)
        self.cut_progress_bar.setValue(0)
        self.cut_progress_bar.setAlignment(Qt.AlignCenter)
        self.cut_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_2.addWidget(self.cut_progress_bar)

        self.horizontalLayout_2.addWidget(self.cut_progress_gb)

        self.time_remaining_gb = QGroupBox(self.experiment_buttons)
        self.time_remaining_gb.setObjectName("time_remaining_gb")
        self.time_remaining_gb.setAlignment(Qt.AlignCenter)
        self.time_remaining_gb.setFlat(True)
        self.verticalLayout_3 = QVBoxLayout(self.time_remaining_gb)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.time_remaining_le = QLineEdit(self.time_remaining_gb)
        self.time_remaining_le.setObjectName("time_remaining_le")
        sizePolicy2.setHeightForWidth(self.time_remaining_le.sizePolicy().hasHeightForWidth())
        self.time_remaining_le.setSizePolicy(sizePolicy2)
        self.time_remaining_le.setAlignment(Qt.AlignCenter)
        self.time_remaining_le.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.time_remaining_le)

        self.horizontalLayout_2.addWidget(self.time_remaining_gb)

        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.verticalLayout_5.addWidget(self.experiment_buttons)

        self.controls_area = ControlsArea(self.left_pane)
        self.controls_area.setObjectName("controls_area")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.controls_area.sizePolicy().hasHeightForWidth())
        self.controls_area.setSizePolicy(sizePolicy3)

        self.verticalLayout_5.addWidget(self.controls_area)

        self.splitter.addWidget(self.left_pane)
        self.plot_widget = PlotWidget(self.splitter)
        self.plot_widget.setObjectName("plot_widget")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.plot_widget.sizePolicy().hasHeightForWidth())
        self.plot_widget.setSizePolicy(sizePolicy4)
        self.splitter.addWidget(self.plot_widget)

        self.verticalLayout_6.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1160, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.save_action)
        self.menuFile.addAction(self.load_action)
        self.menuFile.addAction(self.export_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.exit_action)
        self.menuHelp.addAction(self.view_logs_action)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.save_action.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.load_action.setText(QCoreApplication.translate("MainWindow", "Load", None))
        self.export_action.setText(QCoreApplication.translate("MainWindow", "Export", None))
        self.exit_action.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.view_logs_action.setText(QCoreApplication.translate("MainWindow", "View Logs", None))
        self.label.setText("")
        self.full_scan_btn.setText(QCoreApplication.translate("MainWindow", "Full Scan", None))
        self.az_scan_btn.setText(QCoreApplication.translate("MainWindow", "Scan Azimuth", None))
        self.el_scan_btn.setText(QCoreApplication.translate("MainWindow", "Scan Elevation", None))
        self.abort_btn.setText(QCoreApplication.translate("MainWindow", "Abort", None))
        self.total_progress_gb.setTitle(QCoreApplication.translate("MainWindow", "Total Progress", None))
        self.cut_progress_gb.setTitle(QCoreApplication.translate("MainWindow", "Cut Progress", None))
        self.time_remaining_gb.setTitle(QCoreApplication.translate("MainWindow", "Time Remaining", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", "Tools", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    # retranslateUi
