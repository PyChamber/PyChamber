import sys

import click

import pychamber
from pychamber.classes import app
from pychamber.classes.logger import log, set_log_level


@click.command()
@click.option(
    '--loglevel',
    type=click.Choice(
        ['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False
    ),
    default="warning",
)
def main(loglevel: str) -> None:
    set_log_level(loglevel)
    log.info("Starting PyChamber:")
    log.info(f"\tVersion: {pychamber.__version__}")

    pychamber_app = app.PyChamberApp([sys.argv[0]])
    pychamber_app.setApplicationName('pychamber')
    pychamber_app.setApplicationVersion(pychamber.__version__)
    pychamber_app.gui()

    sys.exit(pychamber_app.exec_())


if __name__ == "__main__":
    main()
