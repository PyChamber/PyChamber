from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

from qtpy.QtWidgets import QSpinBox


class ListSpinBox(QSpinBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._vals = []

    def setValues(self, vals):
        was_empty = len(self._vals) == 0
        self._vals = list(vals)
        self.setRange(0, len(vals) - 1)
        if was_empty:
            self.setValue(0)

    def getValue(self):
        return self._vals[self.value()]

    def textFromValue(self, val: int) -> str:
        if len(self._vals) == 0:
            return ""
        return str(self._vals[val])

    def valueFromText(self, text: str) -> int:
        try:
            val = float(text)
        except ValueError:
            return 0

        nearest = min(self._vals, key=lambda x: abs(x - val))
        return self._vals.index(nearest)
