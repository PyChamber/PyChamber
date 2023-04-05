from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qtpy.QtWidgets import QLayout

from qtpy.QtWidgets import QVBoxLayout, QWidget

from .collapsible_section import CollapsibleSection


class CollapsibleWidget(QWidget):
    def __init__(self, parent: QWidget | None = None, name: str = "") -> None:
        super().__init__(parent)

        self.section = CollapsibleSection(self, name)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.addStretch()
        layout.addWidget(self.section)

        self.content_layout = QVBoxLayout()

    def addLayout(self, layout: QLayout) -> None:
        self.content_layout.addLayout(layout)

    def addWidget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)

    def recalculateSize(self) -> None:
        self.section.set_content_layout(self.content_layout)
