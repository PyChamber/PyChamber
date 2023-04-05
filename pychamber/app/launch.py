import logging
import os
import sys


def main() -> None:
    os.environ["QT_API"] = "pyside6"
    os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

    from pychamber.api import PluginManager
    from pychamber.app import app
    from pychamber.app.logger import LOG

    manager = PluginManager()
    manager.load_plugins()

    args = {}
    LOG.setLevel(logging.DEBUG)

    sys.exit(app.run(args))


if __name__ == "__main__":
    main()
