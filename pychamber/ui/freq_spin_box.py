from typing import Tuple

from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QDoubleSpinBox
from quantiphy import Quantity


class FrequencySpinBox(QDoubleSpinBox):
    def textFromValue(self, v: float) -> str:
        return str(Quantity(v, 'Hz'))

    def valueFromText(self, text: str) -> float:
        return Quantity(text).real

    def validate(self, input: str, pos: int) -> Tuple[QValidator.State, str, int]:
        return super().validate(input, pos)
