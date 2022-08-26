"""A lineedit that only accepts valid frequency strings."""
from typing import Optional

import quantiphy
from PyQt5.QtWidgets import QLineEdit

from .freq_validator import FrequencyValidator


class FrequencyLineEdit(QLineEdit):
    """A QLineEdit that only accepts valid frequency strings."""

    def __init__(self, parent=None) -> None:
        """Create the text box.

        Arguments:
            parent: parent QWidget
        """
        super().__init__(parent)
        self.setValidator(FrequencyValidator(self))

    def setText(self, text: Optional[str]) -> None:
        """Set the text but convert to a frequency string first.

        Arguments:
            text: the text to convert.
        """
        val = quantiphy.Quantity(text, units="Hz")
        return super().setText(val.render())
