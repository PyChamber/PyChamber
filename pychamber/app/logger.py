import logging
from functools import cached_property
from logging import LogRecord

from qtpy.QtCore import QObject, Signal


class LogSignalWorkaround(QObject):
    # See https://stackoverflow.com/questions/66664542/conflicting-names-between-logging-emit-function-and-qt-emit-signal/66664679#66664679
    newLogEntry = Signal(str)


class QLogHandler(logging.Handler):
    @cached_property
    def workaround(self):
        return LogSignalWorkaround()

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        self.workaround.newLogEntry.emit(msg)


class QLogFormatter(logging.Formatter):
    def color(self, loglevel):
        return ["grey", "grey", "yellow", "orange", "red"][(loglevel // 10) - 1]

    def format(self, record):  # noqa: A003
        fmt = (
            f"<span style='color:{self.color(record.levelno)}'>[%(levelname)s]</span> <span style='color:"
            " gray'>(%(filename)s:%(lineno)s)</span> %(message)s"
        )
        formatter = logging.Formatter(fmt, datefmt="%m/%d/%y %I:%M:%S %p")
        return formatter.format(record)


LOG = logging.getLogger(__name__)
fmt = QLogFormatter()

pte_handler = QLogHandler()
pte_handler.setFormatter(fmt)
pte_handler.name = "pte_handler"

LOG.addHandler(pte_handler)
