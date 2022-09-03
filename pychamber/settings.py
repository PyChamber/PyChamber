"""Persistent application-wide settings.

Defines the SETTINGS global that can be accessed throughout the application.

Each plugin gets its own section e.g. the positioner plugin settings will be:

SETTINGS["positioner/az-start"]
SETTINGS["positioner/az-stop"]
...

The defaults are defined per plugin and populate the global defaults when registered.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict
    from pychamber.plugins.base import PyChamberPlugin

from PyQt5.QtCore import QSettings, pyqtSignal

from pychamber.logger import LOG

ORG_NAME = "PyChamber"
APP_NAME = "PyChamber"


class Settings(QSettings):
    """The actual settings object.

    Attributes:
        settings_changed: Signal
    """

    settings_changed = pyqtSignal(str)
    _defaults: Dict = {"theme": "Dark"}

    def __init__(self, parent=None) -> None:
        """Create the settings object.

        Arguments:
            parent: parent QWidget
        """
        super().__init__(ORG_NAME, APP_NAME, parent)

    def __getitem__(self, index: str) -> Any:
        """Retrieve a setting or its default if not set.

        Arguments:
            index: setting name
        """
        return self.value(index, self._defaults[index])

    def __setitem__(self, key: str, value: Any) -> None:
        """Change a setting. Emits a settings_changed signal.

        Arguments:
            key: setting name
            value: new value
        """
        LOG.debug(f"Updating setting: {key} = {value}")
        self.setValue(key, value)
        self.settings_changed.emit(key)

    def __contains__(self, elem: str) -> bool:
        """Enable 'in' operator.

        Arguments:
            elem: element to check existence of
        """
        return elem in self.childGroups()

    def setval(self, key: str, value: Any) -> None:
        """This is needed to connect setting changes to signals with a lambda.

        Arguments:
            key: setting name
            value: new value
        """
        self[key] = value

    def register_plugin(self, plugin: PyChamberPlugin) -> None:
        """Creatings a settings entry for a new plugin and populates defaults.

        If the setting already exists, it is set in the plugin, otherwise
        the default value FROM the plugin's defined defaults is saved to
        the application settings.

        Arguments:
            plugin: The plugin to register
        """
        assert plugin.NAME is not None
        LOG.debug(f"Registering plugin: {plugin.NAME}")
        self.beginGroup(plugin.NAME)
        for key, val in plugin.CONFIG.items():
            self._defaults[plugin.NAME + "/" + key] = val
            if self.contains(key):
                plugin.CONFIG[key] = self.value(key)
        self.endGroup()


SETTINGS = Settings()
