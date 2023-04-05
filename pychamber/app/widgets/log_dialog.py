from qtpy.QtWidgets import QWidget

from pychamber.app.logger import LOG
from pychamber.app.ui.log_dialog import Ui_LogDialog


class LogDialog(QWidget, Ui_LogDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setupUi(self)
        self.connect_signals()

    def connect_signals(self):
        for handler in LOG.handlers:
            if handler.name == "pte_handler":
                LOG.handlers[0].workaround.newLogEntry.connect(self.log_pte.appendHtml)
