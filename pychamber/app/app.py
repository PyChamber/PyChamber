from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication

import pychamber
from pychamber.app import MainWindow


def run(args: dict) -> None:
    QCoreApplication.setAttribute(
        Qt.AA_ShareOpenGLContexts
    )  # needed to suppress annoying terminal output. See https://stackoverflow.com/questions/56159475/qt-webengine-seems-to-be-initialized

    app = QApplication(["pychamber"])
    app.setOrganizationName("pychamber")
    app.setApplicationName("pychamber")
    app.setApplicationVersion(pychamber.__version__)

    main = MainWindow()
    main.show()

    try:
        app.exec_()
    except Exception as e:
        raise e
