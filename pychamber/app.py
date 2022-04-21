import logging
import sys

from PyQt5.QtWidgets import QApplication

from pychamber.ui.main_window import MainWindow


def run():
    from pychamber.controller import PyChamberCtrl

    app = QApplication(sys.argv)
    view = MainWindow()
    view.setupUi()

    PyChamberCtrl(view=view)
    logging.getLogger('pychamber').addHandler(view.logger)
    logging.getLogger('pychamber').setLevel(logging.INFO)

    view.show()

    sys.exit(app.exec_())
