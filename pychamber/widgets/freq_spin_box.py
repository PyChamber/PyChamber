"""A spinbox that can handle frequencies sensibly."""
from typing import Tuple

import quantiphy
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QAbstractSpinBox, QDoubleSpinBox
from quantiphy import Quantity


class FrequencySpinBox(QDoubleSpinBox):
    """Inherets from QDoubleSpinBox to display / accept frequency strings.

    With this, the user sees formatted strings like "10 MHz," "1.45 GHz", etc.
    and can also type frequency strings.
    """

    def __init__(self, parent=None) -> None:
        """Create the spinbox.

        Arguments:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.setRange(0, 100e9)
        self.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)

    def textFromValue(self, v: float) -> str:
        """Displays value as frequency string.

        Arguments:
            v: float value

        Returns:
            string representation of the value
        """
        return str(Quantity(v, 'Hz'))

    def valueFromText(self, text: str) -> float:
        """Converts frequency string to actual float.

        Arguments:
            text: text to convert

        Returns:
            actual numerical value
        """
        return float(Quantity(text).real)

    def validate(self, text: str, pos: int) -> Tuple[QValidator.State, str, int]:
        """Only accept valid frequency strings.

        Arguments:
            text: the text to validate
            pos: the position of the cursor

        Returns:
            A tuple of (QValidator.State, Validated text, Cursor position)
        """
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
