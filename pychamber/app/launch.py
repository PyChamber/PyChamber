import logging
import sys

from pychamber.api import PluginManager
from pychamber.app import app
from pychamber.app.logger import LOG


def main() -> None:
    manager = PluginManager()
    manager.load_plugins()

    args = {}
    LOG.setLevel(logging.DEBUG)

    sys.exit(app.run(args))


if __name__ == "__main__":
    main()
