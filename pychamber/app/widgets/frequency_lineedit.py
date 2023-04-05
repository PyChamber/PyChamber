"""A lineedit that only accepts valid frequency strings."""

import quantiphy
from qtpy.QtWidgets import QLineEdit

from .frequency_validator import FrequencyValidator


class FrequencyLineEdit(QLineEdit):
    """A QLineEdit that only accepts valid frequency strings."""

    def __init__(self, parent=None) -> None:
        """Create the text box.
        Arguments:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.setValidator(FrequencyValidator(self))

    def setText(self, text: str | None) -> None:
        """Set the text but convert to a frequency string first.
        Arguments:
            text: the text to convert.
        """
        val = quantiphy.Quantity(text, units="Hz")
        return super().setText(val.render())

    def value(self) -> quantiphy.Quantity | None:
        if self.text() == "" or not self.hasAcceptableInput():
            return None
        val = quantiphy.Quantity(self.text(), units="Hz")
        return val
