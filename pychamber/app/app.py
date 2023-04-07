from qtpy.QtCore import QCoreApplication, Qt
from qtpy.QtWidgets import QApplication

import pychamber
from pychamber.api import PluginManager
from pychamber.app import MainWindow
from pychamber.app.logger import LOG


def run(args: dict) -> None:
    QCoreApplication.setAttribute(
        Qt.AA_ShareOpenGLContexts
    )  # needed to suppress annoying terminal output. See https://stackoverflow.com/questions/56159475/qt-webengine-seems-to-be-initialized

    LOG.info("Creating application")
    app = QApplication(["PyChamber"])
    app.setOrganizationName("pychamber")
    app.setApplicationName("pychamber")
    app.setApplicationVersion(pychamber.__version__)

    LOG.info("Loading plugins")
    manager = PluginManager()
    manager.load_plugins()

    main = MainWindow()
    main.show()
    main.center()
    main.post_visible_setup()

    try:
        app.exec_()
    except Exception as e:
        print(e)
        raise e
