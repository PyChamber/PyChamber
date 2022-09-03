from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from PyQt5.QtWidgets import QLayout

from PyQt5.QtCore import (
    QAbstractAnimation,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
)
from PyQt5.QtWidgets import QFrame, QGridLayout, QScrollArea, QToolButton, QWidget

from pychamber.ui import font, size_policy


class CollapsibleSection(QWidget):
    def __init__(
        self,
        title: str = "",
        animation_duration: int = 100,
        parent: Optional[QWidget] = None,
    ) -> None:
        QWidget.__init__(self, parent)
        self.toggle_button = QToolButton(self)
        self.toggle_button.setStyleSheet("QToolButton {border: none;}")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setFont(font["BOLD_12"])
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.header_line = QFrame(self)
        self.header_line.setFrameShape(QFrame.HLine)
        self.header_line.setSizePolicy(size_policy['EXP_MAX'])

        self.content_area = QScrollArea(self)
        self.content_area.setStyleSheet("QScrollArea {border-top: none;}")
        self.content_area.setSizePolicy(size_policy["EXP_FIX"])
        self.content_area.setMinimumHeight(0)
        self.content_area.setMaximumHeight(0)

        self.animation_duration = animation_duration
        self.toggle_animation = QParallelAnimationGroup(self)
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self.content_area, b"maximumHeight")
        )

        self.main_layout = QGridLayout(self)
        self.main_layout.setVerticalSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.toggle_button, 0, 0, 1, 1, Qt.AlignLeft)
        self.main_layout.addWidget(self.header_line, 0, 2, 1, 1)
        self.main_layout.addWidget(self.content_area, 1, 0, 1, 3)
        self.setLayout(self.main_layout)

        self.toggle_button.toggled.connect(self.toggle)

    def set_content_layout(self, content_layout: QLayout) -> None:
        layout = self.content_area.layout()
        del layout
        self.content_area.setLayout(content_layout)
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = content_layout.sizeHint().height()

        for i in range(0, self.toggle_animation.animationCount() - 1):
            section_animation = self.toggle_animation.animationAt(i)
            section_animation.setDuration(self.animation_duration)
            section_animation.setStartValue(collapsed_height)
            section_animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(self.animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

    def toggle(self, collapsed: bool) -> None:
        if collapsed:
            self.toggle_button.setArrowType(Qt.DownArrow)
            self.toggle_animation.setDirection(QAbstractAnimation.Forward)
        else:
            self.toggle_button.setArrowType(Qt.RightArrow)
            self.toggle_animation.setDirection(QAbstractAnimation.Backward)
        self.toggle_animation.start()
