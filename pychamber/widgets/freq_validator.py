from typing import Tuple

import quantiphy
from PyQt5.QtGui import QValidator


class FrequencyValidator(QValidator):
    def validate(self, text: str, pos: int) -> Tuple['QValidator.State', str, int]:
        try:
            ret = quantiphy.Quantity(text)
            if ret.units != 'Hz':
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
