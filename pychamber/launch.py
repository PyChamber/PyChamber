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

    return app.run(args)


if __name__ == "__main__":
    main()
