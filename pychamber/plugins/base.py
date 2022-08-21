from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from pychamber.main_window import MainWindow

from PyQt5.QtWidgets import QWidget


class PyChamberPluginError(Exception):
    pass


class PyChamberPlugin(QWidget):
    NAME: Optional[str] = None
    CONFIG: Dict = dict()
    REQUIRED: List[PyChamberPlugin] = []

    def __init__(self, main_window: MainWindow) -> None:
        super().__init__(main_window)

        self.main = main_window

    def _register(self) -> None:
        from pychamber.settings import SETTINGS

        if self.NAME is None:
            raise PyChamberPluginError("Plugin must define NAME")

        SETTINGS.register_plugin(self)

    def _unregister(self) -> None:
        self.main.unregister_plugin(self)

    def _setup(self) -> None:
        ...

    def _post_visible_setup(self) -> None:
        ...


class PyChamberPanelPlugin(PyChamberPlugin):
    pass
