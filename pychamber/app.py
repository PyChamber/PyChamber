from typing import Dict

from PyQt5.QtWidgets import QApplication, QMessageBox

import pychamber
from pychamber.logger import log, set_log_level
from pychamber.main_window import MainWindow


def run(args: Dict):
    set_log_level(args['loglevel'])
    log.info(f"Starting PyChamber (v{pychamber.__version__})")

    app = QApplication(['PyChamber'])
    app.setOrganizationName("pychamber")
    app.setApplicationName("pychamber")
    app.setApplicationVersion(pychamber.__version__)

    main = MainWindow()
    main.setup()
    main.show()
    main.center()
    main.post_visible_setup()

    try:
        app.exec_()
    except Exception as e:
        QMessageBox.critical(
            None,
            "Unhandled Error",
            (
                f"An error occurred that was unhandled. Please file a bug report."
                f"\nERROR: {e}"
            ),
        )
        raise e
