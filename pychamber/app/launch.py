import logging
import os
import sys


def main() -> None:
    os.environ["QT_API"] = "pyside6"
    os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

    from pychamber.app import app
    from pychamber.app.logger import LOG

    args = {}
    LOG.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter("[%(levelname)s] %(filename)s:%(lineno)s - %(message)s"))
    LOG.addHandler(stderr_handler)

    LOG.info("Running PyChamber")
    sys.exit(app.run(args))


if __name__ == "__main__":
    try:
        # When running from a PyInstaller executable, the bootloader has to do a
        # lot of loading / importing before we can even load our splash screen.
        # This is a splash screen provided by PyInstaller we can use. The
        # update_text function doesn't really do anything, so we only load it
        # here to close once the bootloader is done. Actually launching
        # PyChamber is quite quick so no splash screen is needed for the main program.
        import pyi_splash

        pyi_splash.close()
    except ImportError:
        pass

    main()
