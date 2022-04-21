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


class ClearDataWarning(QMessageBox):
    def __init__(self, msg: str) -> None:
        super(ClearDataWarning, self).__init__(parent=None)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Cancel)
        self.setText(msg)

    def warn(self) -> bool:
        ret = self.exec_()
        if ret == QMessageBox.Yes:
            return True
        else:
            return False


class WhichPol(QMessageBox):
    def __init__(self) -> None:
        super(WhichPol, self).__init__()
        self.addButton("1", QMessageBox.NoRole)
        self.addButton("2", QMessageBox.YesRole)
        self.setText("Which Polarization?")

    @classmethod
    def ask(cls) -> int:
        instance = WhichPol()
        ret = instance.exec_()
        if ret == QMessageBox.No:
            return 0
        else:
            return 1
