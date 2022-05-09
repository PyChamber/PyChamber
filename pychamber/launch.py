import click


@click.command()
@click.option(
    '--loglevel',
    type=click.Choice(
        ['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False
    ),
    default="warning",
)
def main(loglevel: str) -> None:
    import sys

    import pychamber
    from pychamber.classes.logger import log, set_log_level

    set_log_level(loglevel)
    log.info("Starting PyChamber:")
    log.info(f"\tVersion: {pychamber.__version__}")

    from pychamber.classes import app

    app = app.PyChamberApp([sys.argv[0]])
    app.setApplicationName('pychamber')
    app.setApplicationVersion(pychamber.__version__)
    app.gui()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
