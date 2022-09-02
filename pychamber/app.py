"""Starts the application instance."""
from typing import Dict

from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen

import pychamber
from pychamber.logger import LOG, set_log_level
from pychamber.main_window import MainWindow


def run(args: Dict):
    """Start PyChamber.

    Arguments:
        args: dictionary of parsed command-line arguments
    """
    set_log_level(args['loglevel'])
    LOG.info(f"Starting PyChamber (v{pychamber.__version__})")

    LOG.debug("Creating application...")
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
        LOG.critical(f"{e}")
        raise e


def create_splash() -> QSplashScreen:
    pm = QPixmap(":/splash.png")
    painter = QPainter()
    painter.drawPixmap(0, 0, 500, 400, pm)

    splash = QSplashScreen(pm)
    splash_font = splash.font()
    splash_font.setPixelSize(14)
    splash.setFont(splash_font)

    return splash
