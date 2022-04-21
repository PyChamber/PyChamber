import logging

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPlainTextEdit


class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR: ("[{levelname:^8s}] {message}", QColor("red")),
        logging.DEBUG: ("[{levelname:^8s}] {message}", QColor("green")),
        logging.INFO: ("[{levelname:^8s}] {message}", QColor("gray")),
        logging.WARNING: ('[{levelname:^8s}] {message}', QColor(128, 128, 0)),
    }

    def format(self, record):
        last_fmt = self._style._fmt
        opt = self.FORMATS.get(record.levelno)
        if opt:
            fmt, color = opt
            self._style._fmt = "<pre><font color=\"{}\">{}</font></pre>".format(
                QColor(color).name(), fmt
            )
        res = logging.Formatter.format(self, record)
        self._style._fmt = last_fmt
        return res


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendHtml)
        self.setFormatter(ColorFormatter(style='{'))

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)
