from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from .analyzer_controls import AnalyzerControls
from .experiment_controls import ExperimentControls
from .positioner_controls import PositionerControls


class ControlsArea(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.layout.addWidget(self.scroll_area)

        self.content = QWidget()
        self.scroll_area.setWidget(self.content)

        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.experiment_controls = ExperimentControls()
        self.content_layout.addWidget(self.experiment_controls)
        self.content_layout.setAlignment(self.experiment_controls, Qt.AlignTop)

        self.analyzer_controls = AnalyzerControls()
        self.content_layout.addWidget(self.analyzer_controls)
        self.content_layout.setAlignment(self.analyzer_controls, Qt.AlignTop)

        self.positioner_controls = PositionerControls()
        self.content_layout.addWidget(self.positioner_controls)
        self.content_layout.setAlignment(self.positioner_controls, Qt.AlignTop)

        self.content_layout.addStretch()
