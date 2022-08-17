from typing import Optional

from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pychamber.logger import log
from pychamber.ui import size_policy

from .base import PyChamberPlugin


class CalibrationPlugin(PyChamberPlugin):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName('calibration')
        self.setLayout(QVBoxLayout())

    def setup(self) -> None:
        self._add_widgets()

    def _add_widgets(self) -> None:
        log.debug("Creating Calibration widget...")
        self.groupbox = QGroupBox("Calibration", self)
        self.layout().addWidget(self.groupbox)

        layout = QVBoxLayout(self.groupbox)

        hlayout = QHBoxLayout()
        cal_file_label = QLabel("Cal file:", self.groupbox)
        hlayout.addWidget(cal_file_label)

        self.cal_file_lineedit = QLineEdit(self.groupbox)
        self.cal_file_lineedit.setReadOnly(True)
        hlayout.addWidget(self.cal_file_lineedit)

        self.cal_file_filebrowse_btn = QPushButton("Browse", self.groupbox)
        hlayout.addWidget(self.cal_file_filebrowse_btn)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.calibration_btn = QPushButton("Generate Cal File", self.groupbox)
        hlayout.addWidget(self.calibration_btn)

        self.calibration_view_btn = QPushButton("View Cal File", self.groupbox)
        self.calibration_view_btn.setEnabled(False)
        hlayout.addWidget(self.calibration_view_btn)

        layout.addLayout(hlayout)
