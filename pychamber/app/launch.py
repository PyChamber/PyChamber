import logging
import os
import sys


def main() -> None:
    os.environ["QT_API"] = "pyside6"
    os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

    from pychamber.api import PluginManager
    from pychamber.app import app
    from pychamber.app.logger import LOG

    LOG.info("Loading plugins")
    manager = PluginManager()
    manager.load_plugins()

    args = {}
    LOG.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter("[%(levelname)s] %(filename)s:%(lineno)s - %(message)s"))
    LOG.addHandler(stderr_handler)

    LOG.info("Running PyChamber")
    sys.exit(app.run(args))


if __name__ == "__main__":
    main()
