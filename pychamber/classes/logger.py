import logging
import logging.handlers
import pathlib
import sys
import tempfile
from datetime import datetime


class StreamFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        source = getattr(record, "source", "")
        return bool(source != "stream")


logging.basicConfig()
log = logging.getLogger(__name__)

log_path = (
    pathlib.Path(tempfile.gettempdir())
    / f"pychamber_{datetime.now().strftime('%y%m%d_%H%M')}.log"
)
_formatter = logging.Formatter("[%(levelname)s] - %(module)s: %(message)s")

_stderr_handler = logging.StreamHandler(sys.stderr)
_stderr_handler.setFormatter(_formatter)
_file_handler = logging.handlers.RotatingFileHandler(
    log_path, mode='w', encoding="utf-8", maxBytes=5 * 1024 * 1024, backupCount=3
)
_file_handler.setFormatter(_formatter)

log.addHandler(_stderr_handler)
log.addHandler(_file_handler)

log.propagate = False


def set_log_level(level: str) -> None:
    log.setLevel(level.upper())
