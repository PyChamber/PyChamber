"""Defines a frequency validator for use in LineEdits."""

import quantiphy
from qtpy.QtGui import QValidator


class FrequencyValidator(QValidator):
    """Validates frequency strings."""

    def validate(self, text: str, pos: int) -> tuple["QValidator.State", str, int]:
        """Do the validation.
        Arguments:
            text: the text to validate
            pos: the position of the cursor
        Returns:
            A tuple of (QValidator.State, Validated text, Cursor position)
        """
        if text == "":
            return (QValidator.Intermediate, text, pos)
        else:
            try:
                ret = quantiphy.Quantity(text)
                if ret.units == "" or ret.units == "h" or ret.units == "H":
                    return (QValidator.Intermediate, text, pos)
                elif ret.units != "Hz":
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
