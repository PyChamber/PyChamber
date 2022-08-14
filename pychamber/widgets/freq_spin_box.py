from typing import Tuple

from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QSpinBox
from quantiphy import Quantity


class FrequencySpinBox(QSpinBox):
    def textFromValue(self, v: int) -> str:
        return str(Quantity(v, 'Hz'))

    def valueFromText(self, text: str) -> int:
        return int(Quantity(text).real)

    def validate(self, input: str, pos: int) -> Tuple[QValidator.State, str, int]:
        return super().validate(input, pos)
