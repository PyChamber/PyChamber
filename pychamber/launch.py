import sys

import click

from pychamber import app


@click.command()
@click.option(
    '--loglevel',
    type=click.Choice(
        ['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False
    ),
    default="warning",
)
def main(loglevel: str) -> None:
    args = {'loglevel': loglevel}

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
