import logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    import sys

    from pychamber import app

    logging.basicConfig(level=logging.INFO)
    log.info("Starting PyChamber")

    sys.exit(app.run())
