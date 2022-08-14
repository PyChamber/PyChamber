import functools
from enum import Enum, auto
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pychamber.logger import log
from pychamber.ui.ui import font, size_policy

from ..plugins.base import PyChamberPlugin


class ExperimentType(Enum):
    AZIMUTH = auto()
    ELEVATION = auto()
    FULL = auto()


class ExperimentWidget(PyChamberPlugin):
    # Signals
    start_experiment = pyqtSignal(object)
    experiment_done = pyqtSignal()
    abort_clicked = pyqtSignal()
    progress_updated = pyqtSignal(int)
    cut_progress_updated = pyqtSignal(int)
    data_acquired = pyqtSignal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName('experiment')
        self.setLayout(QVBoxLayout())

    def setup(self) -> None:
        self._add_widgets()

    def post_visible_setup(self) -> None:
        self._connect_signals()

    def _add_widgets(self) -> None:
        log.debug("Creating Experiment widget...")
        self.groupbox = QGroupBox("Experiment", self)
        self.layout().addWidget(self.groupbox)

        layout = QHBoxLayout(self.groupbox)

        vlayout = QVBoxLayout()

        self.full_scan_btn = QPushButton("Full Scan", self.groupbox)
        self.full_scan_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.full_scan_btn.setFont(font["BOLD_12"])
        vlayout.addWidget(self.full_scan_btn)

        self.az_scan_btn = QPushButton("Scan Azimuth", self.groupbox)
        self.az_scan_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.az_scan_btn.setFont(font["BOLD_12"])
        vlayout.addWidget(self.az_scan_btn)

        self.el_scan_btn = QPushButton("Scan Elevation", self.groupbox)
        self.el_scan_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.el_scan_btn.setFont(font["BOLD_12"])
        vlayout.addWidget(self.el_scan_btn)

        self.abort_btn = QPushButton("ABORT", self.groupbox)
        self.abort_btn.setStyleSheet("background-color: rgb(237, 51, 59)")
        self.abort_btn.setSizePolicy(size_policy["EXP_PREF"])
        self.abort_btn.setFont(font["BOLD_12"])
        self.abort_btn.setEnabled(False)
        vlayout.addWidget(self.abort_btn)

        layout.addLayout(vlayout)

        vlayout = QVBoxLayout()

        total_progress_label = QLabel("Total Progress", self.groupbox)
        total_progress_label.setSizePolicy(size_policy["PREF_PREF"])
        total_progress_label.setFont(font["BOLD_12"])
        total_progress_label.setAlignment(Qt.AlignHCenter)
        vlayout.addWidget(total_progress_label)

        self.total_progressbar = QProgressBar(self.groupbox)
        self.total_progressbar.setSizePolicy(size_policy["EXP_PREF"])
        vlayout.addWidget(self.total_progressbar)

        self.cut_progress_label = QLabel("Cut Progress", self.groupbox)
        self.cut_progress_label.setSizePolicy(size_policy["PREF_PREF"])
        self.cut_progress_label.setFont(font["BOLD_12"])
        self.cut_progress_label.setAlignment(Qt.AlignHCenter)
        vlayout.addWidget(self.cut_progress_label)

        self.cut_progressbar = QProgressBar(self.groupbox)
        self.cut_progressbar.setSizePolicy(size_policy["EXP_PREF"])
        vlayout.addWidget(self.cut_progressbar)

        time_remaining_label = QLabel("Time Remaining Estimate", self.groupbox)
        time_remaining_label.setSizePolicy(size_policy["PREF_PREF"])
        time_remaining_label.setFont(font["BOLD_12"])
        time_remaining_label.setAlignment(Qt.AlignHCenter)
        vlayout.addWidget(time_remaining_label)

        self.time_remaining_lineedit = QLineEdit(self.groupbox)
        self.time_remaining_lineedit.setSizePolicy(size_policy["EXP_PREF"])
        vlayout.addWidget(self.time_remaining_lineedit)

        layout.addLayout(vlayout)

        self.groupbox.setEnabled(False)
        self.cut_progress_label.hide()
        self.cut_progressbar.hide()

    def _connect_signals(self) -> None:
        self.az_scan_btn.clicked.connect(
            functools.partial(self.start_experiment.emit, ExperimentType.AZIMUTH)
        )

        self.el_scan_btn.clicked.connect(
            functools.partial(self.start_experiment.emit, ExperimentType.ELEVATION)
        )

        self.full_scan_btn.clicked.connect(
            functools.partial(self.start_experiment.emit, ExperimentType.FULL)
        )

        self.start_experiment.connect(self._on_start_experiment)
        self.experiment_done.connect(self._on_experiment_done)
        self.progress_updated.connect(self._on_progress_updated)
        self.cut_progress_updated.connect(self._on_cut_progress_updated)

    def _on_start_experiment(self) -> None:
        self.az_scan_btn.setEnabled(False)
        self.el_scan_btn.setEnabled(False)
        self.full_scan_btn.setEnabled(False)
        self.abort_btn.setEnabled(True)

    def _on_experiment_done(self) -> None:
        self.az_scan_btn.setEnabled(True)
        self.el_scan_btn.setEnabled(True)
        self.full_scan_btn.setEnabled(True)
        self.abort_btn.setEnabled(False)

    def _on_progress_updated(self, progress: int) -> None:
        self.total_progressbar.setValue(progress)

    def _on_cut_progress_updated(self, progress: int) -> None:
        self.cut_progressbar.setValue(progress)
