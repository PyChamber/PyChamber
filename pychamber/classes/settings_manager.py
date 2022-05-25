from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QSettings, pyqtSignal

ORG_NAME = "PyChamber"
APP_NAME = "PyChamber"


class SettingsManager(QSettings):
    settingsChanged = pyqtSignal()

    _defaults = {
        "backend": "pyvisa-py",
    }

    def __init__(self, parent=None) -> None:
        super().__init__(ORG_NAME, APP_NAME, parent)

    def __getitem__(self, index: str) -> Any:
        return self.value(index, self._defaults[index])

    def __setitem__(self, key: str, value: Any) -> None:
        self.setValue(key, value)
        self.settingsChanged.emit()
