from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict
    from pychamber.plugins.base import PyChamberPlugin

from PyQt5.QtCore import QSettings, pyqtSignal

from pychamber.logger import log

ORG_NAME = "PyChamber"
APP_NAME = "PyChamber"


class Settings(QSettings):
    settings_changed = pyqtSignal(str)
    _defaults: Dict = {}

    # _defaults = {
    #     "python-theme": "nightowl-light",
    #     "cal-file": "",
    # }

    def __init__(self, parent=None) -> None:
        super().__init__(ORG_NAME, APP_NAME, parent)

    def __getitem__(self, index: str) -> Any:
        return self.value(index, self._defaults[index])

    def __setitem__(self, key: str, value: Any) -> None:
        log.debug(f"Updating setting: {key} = {value}")
        self.setValue(key, value)
        self.settings_changed.emit(key)

    def __contains__(self, elem: str) -> bool:
        return elem in self.childGroups()

    def setval(self, key: str, value: Any) -> None:
        # needed to call from a lambda in `controller`
        self[key] = value

    def register_plugin(self, plugin: PyChamberPlugin) -> None:
        assert plugin.NAME is not None
        log.debug(f"Registering plugin: {plugin.NAME}")
        self.beginGroup(plugin.NAME)
        for key, val in plugin.CONFIG.items():
            self._defaults[plugin.NAME + "/" + key] = val
            if self.contains(key):
                plugin.CONFIG[key] = self.value(key)
        self.endGroup()


SETTINGS = Settings()
