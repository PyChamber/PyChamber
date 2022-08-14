from PyQt5.QtWidgets import QLineEdit

from .freq_validator import FrequencyValidator


class FrequencyLineEdit(QLineEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setValidator(FrequencyValidator(self))
