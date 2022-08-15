from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QSettings, pyqtSignal

from pychamber.logger import log

ORG_NAME = "PyChamber"
APP_NAME = "PyChamber"


class Settings(QSettings):
    settings_changed = pyqtSignal(str)

    _defaults = {
        "backend": "pyvisa-py",
        "python-theme": "nightowl-light",
        "analyzer-model": "",
        "analyzer-addr": "",
        "positioner-model": "",
        "positioner-port": "",
        "positioner-az-pos": 0.0,
        "positioner-el-pos": 0.0,
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
        "jog-az-step": 0.0,
        "jog-el-step": 0.0,
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
        log.debug(f"Updating setting: {key} = {value}")
        self.setValue(key, value)
        self.settings_changed.emit(key)

    def setval(self, key: str, value: Any) -> None:
        # needed to call from a lambda in `controller`
        self[key] = value


SETTINGS = Settings()
