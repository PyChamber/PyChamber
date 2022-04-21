import logging

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QPlainTextEdit


class ColorFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_fmt = "[%(levelname)s]-%(module)s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + log_fmt + reset,
        logging.INFO: grey + log_fmt + reset,
        logging.WARNING: yellow + log_fmt + reset,
        logging.ERROR: red + log_fmt + reset,
        logging.CRITICAL: bold_red + log_fmt + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)
