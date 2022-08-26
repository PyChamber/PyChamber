from typing import Tuple

import quantiphy
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QAbstractSpinBox, QDoubleSpinBox
from quantiphy import Quantity


class FrequencySpinBox(QDoubleSpinBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRange(0, 100e9)
        self.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)

    def textFromValue(self, v: float) -> str:
        return str(Quantity(v, 'Hz'))

    def valueFromText(self, text: str) -> float:
        return float(Quantity(text).real)

    def validate(self, text: str, pos: int) -> Tuple[QValidator.State, str, int]:
        if text == '':
            return (QValidator.Intermediate, text, pos)
        else:
            try:
                ret = quantiphy.Quantity(text)
                if ret.units == '' or ret.units == 'h' or ret.units == 'H':
                    return (QValidator.Intermediate, text, pos)
                elif ret.units != 'Hz':
                    return (QValidator.Invalid, text, pos)
                else:
                    return (QValidator.Acceptable, text, pos)
            except (
                quantiphy.IncompatiblePreferences,
                quantiphy.InvalidNumber,
                quantiphy.InvalidRecognizer,
                quantiphy.UnknownConversion,
                quantiphy.UnknownScaleFactor,
            ):
                return (QValidator.Invalid, text, pos)
