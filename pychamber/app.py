import logging
import sys

from PyQt5.QtWidgets import QApplication

from pychamber.ui.main_window import MainWindow

log = logging.getLogger(__name__)


def run():
    from pychamber.controller import PyChamberCtrl

    app = QApplication(sys.argv)
    view = MainWindow()
    view.setupUi()
    PyChamberCtrl(view=view)
    view.show()

    log.addHandler(view.logger)
    log.setLevel(logging.INFO)

    sys.exit(app.exec_())
