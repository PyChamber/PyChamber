from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QSettings

ORG_NAME = "PyChamber"
APP_NAME = "PyChamber"


class SettingsManager(QSettings):
    _defaults = {
        "backend": "py",
    }

    def __init__(self, parent=None) -> None:
        super().__init__(ORG_NAME, APP_NAME, parent)

    def __getitem__(self, index: str) -> Any:
        return self.value(index, self._defaults[index])

    def __setitem__(self, key: str, value: Any) -> None:
        self.setValue(key, value)

    def update_widgets_from_settings(self) -> None:
        pass

    def update_settings_from_widgets(self) -> None:
        pass
