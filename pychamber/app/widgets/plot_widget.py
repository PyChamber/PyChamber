from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import pyqtgraph.functions as fn
import qtawesome as qta
from pyqtgraph import getConfigOption
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from pychamber import ExperimentResult


class PlotWidget(QWidget):
    titleChanged = Signal(str)

    def __init__(self, plot, controls, data: ExperimentResult, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.title = title
        self.plot = plot
        self.callbacks = []
        self._data = data
        self.controls = controls

        self.setupUi()

    def setupUi(self) -> None:
        self.controls.title_le.setText(self.title)
        current_bg_color = fn.mkColor(getConfigOption("background"))
        self.controls.bg_color_btn.setColor(current_bg_color)

        self.ctrls_drawer = QFrame()
        ctrls_layout = QVBoxLayout(self.ctrls_drawer)
        ctrls_layout.addWidget(self.controls)
        ctrls_layout.setContentsMargins(0, 0, 0, 0)

        self.drawer_btn = QPushButton()
        self.drawer_btn.setStyleSheet("QPushButton::flat { background-color: #9b9b9b; border: none;}")
        self.drawer_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.drawer_btn.setFixedWidth(10)
        self.drawer_btn.setFlat(True)
        self.drawer_close_icon = qta.icon("fa5s.caret-right")
        self.drawer_open_icon = qta.icon("fa5s.caret-left")
        self.drawer_btn.setIcon(self.drawer_close_icon)
        self.drawer_btn.pressed.connect(self.on_drawer_btn_pressed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(self.plot)
        layout.addWidget(self.drawer_btn)
        layout.addWidget(self.ctrls_drawer)
        layout.setStretch(0, 1)
        layout.setSpacing(2)

    def on_drawer_btn_pressed(self) -> None:
        self.ctrls_drawer.setVisible(not self.ctrls_drawer.isVisible())
        if self.ctrls_drawer.isVisible():
            self.drawer_btn.setIcon(self.drawer_close_icon)
        else:
            self.drawer_btn.setIcon(self.drawer_open_icon)
            self.drawer_btn.setIcon(self.drawer_open_icon)
