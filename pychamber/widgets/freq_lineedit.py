from typing import Optional

import quantiphy
from PyQt5.QtWidgets import QLineEdit

from .freq_validator import FrequencyValidator


class FrequencyLineEdit(QLineEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setValidator(FrequencyValidator(self))

    def setText(self, text: Optional[str]) -> None:
        val = quantiphy.Quantity(text, units="Hz")
        return super().setText(val.render())
