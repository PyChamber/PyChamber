import qtawesome as qta
from qtpy.QtWidgets import QPushButton, QWidget


class SectionButton(QPushButton):
    def __init__(self, item, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.section = item
        self.clicked.connect(self.on_clicked)

        self.closed_icon = qta.icon("fa5s.caret-right")
        self.setIcon(self.closed_icon)
        self.open_icon = qta.icon("fa5s.caret-down")

        self.setStyleSheet(
            "SectionButton::item:hover {background-color:transparent;} SectionButton {font-size: 12pt; text-align:"
            " left; border-bottom: 2px groove #60798B; border-radius: 0px; show-decoration-selected: 0;"
            " selection-background-color: none;}"
        )

    def on_clicked(self):
        if self.section.isExpanded():
            self.section.setExpanded(False)
        else:
            self.section.setExpanded(True)
