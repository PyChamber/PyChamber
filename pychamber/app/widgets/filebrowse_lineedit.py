from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFileDialog, QLineEdit


class FileBrowseLineEdit(QLineEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def mousePressEvent(self, _: QMouseEvent) -> None:
        filename, _ = QFileDialog.getOpenFileName(self)
        if filename != "":
            self.setText(filename)
