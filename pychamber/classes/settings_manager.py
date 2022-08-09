from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QSettings, pyqtSignal

ORG_NAME = "PyChamber"
APP_NAME = "PyChamber"


class SettingsManager(QSettings):
    settingsChanged = pyqtSignal(str)

    _defaults = {
        "backend": "pyvisa-py",
        "python-theme": "nightowl-light",
        "analyzer-model": "",
        "analyzer-addr": "",
        "positioner-model": "",
        "positioner-port": "",
        "pol1-label": "",
        "pol1-param": "S21",
        "pol2-label": "",
        "pol2-param": "S21",
        "az-start": -90,
        "az-stop": 90,
        "az-step": 5,
        "el-start": -90,
        "el-stop": 90,
        "el-step": 5,
        "cal-file": "",
        "polar-autoscale": True,
        "rect-autoscale": True,
        "overfreq-autoscale": True,
    }

    def __init__(self, parent=None) -> None:
        super().__init__(ORG_NAME, APP_NAME, parent)

    def __getitem__(self, index: str) -> Any:
        return self.value(index, self._defaults[index])

    def __setitem__(self, key: str, value: Any) -> None:
        self.setValue(key, value)
        self.settingsChanged.emit(key)

    def setval(self, key: str, value: Any) -> None:
        # needed to call from a lambda in `controller`
        self[key] = value
