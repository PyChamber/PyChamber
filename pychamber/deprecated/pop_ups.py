from __future__ import annotations

from enum import Enum, auto

from PyQt5.QtWidgets import QMessageBox


class MsgLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class PopUpMessage(QMessageBox):
    def __init__(self, msg: str, level: MsgLevel = MsgLevel.INFO) -> None:
        super(PopUpMessage, self).__init__(parent=None)
        if level == MsgLevel.INFO:
            self.setIcon(QMessageBox.Information)
            self.setWindowTitle("PyChamber - Information")
        elif level == MsgLevel.WARNING:
            self.setIcon(QMessageBox.Warning)
            self.setWindowTitle("PyChamber - Warning")
        elif level == MsgLevel.ERROR:
            self.setIcon(QMessageBox.Critical)
            self.setWindowTitle("PyChamber - Error")

        self.setText(msg)
        self.exec_()
