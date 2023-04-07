from qtpy.QtCore import QEvent, QObject, Qt
from qtpy.QtWidgets import QAbstractSpinBox, QComboBox, QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from pychamber.app.logger import LOG

from .analyzer_controls import AnalyzerControls
from .experiment_controls import ExperimentControls
from .positioner_controls import PositionerControls
from .section_button import SectionButton


class ControlsArea(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        LOG.debug("Creating controls area")

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(0)
        self.tree.setAnimated(True)
        self.tree.setVerticalScrollMode(QTreeView.ScrollPerPixel)
        self.tree.setStyleSheet(
            "QTreeWidget {padding: 0px; border: 2px groove #54687A;} "
            "QTreeWidget::item { background-color: transparent; }"
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)

        self.experiment_controls = ExperimentControls()
        self.analyzer_controls = AnalyzerControls()
        self.positioner_controls = PositionerControls()

        self.add_section("Experiment", self.experiment_controls)
        self.add_section("Analyzer", self.analyzer_controls)
        self.add_section("Positioner", self.positioner_controls)

        self.install_wheel_filters()

    def add_section(self, title: str, widget: QWidget) -> None:
        LOG.debug(f"Adding section {title}")
        button_item = QTreeWidgetItem()
        content_item = QTreeWidgetItem(button_item)
        content_item.setDisabled(True)
        section_btn = SectionButton(button_item, text=title)

        self.tree.addTopLevelItem(button_item)
        self.tree.setItemWidget(button_item, 0, section_btn)
        self.tree.setItemWidget(content_item, 0, widget)
        button_item.addChild(content_item)

        if self.tree.topLevelItemCount() == 1:
            normal_style = section_btn.styleSheet()
            new_style = normal_style[:-1] + "border-top-left-radius: 4px; border-top-right-radius: 4px;}"
            section_btn.setStyleSheet(new_style)

    def install_wheel_filters(self):
        LOG.debug("Setting controls widgets to ignore wheel scrolling")

        class ScrollIgnorer(QObject):
            def eventFilter(self, watched: QObject, event: QEvent) -> bool:
                if event.type() == QEvent.Wheel:
                    if watched.focusPolicy() == Qt.WheelFocus:
                        event.accept()
                        return False
                    else:
                        event.ignore()
                        return True
                elif event.type() == QEvent.FocusIn:
                    watched.setFocusPolicy(Qt.WheelFocus)
                elif event.type() == QEvent.FocusOut:
                    watched.setFocusPolicy(Qt.StrongFocus)

                return super().eventFilter(watched, event)

        scroll_ignorer = ScrollIgnorer(self)
        for sb in self.findChildren(QAbstractSpinBox):
            sb.setFocusPolicy(Qt.StrongFocus)
            sb.installEventFilter(scroll_ignorer)
        for cb in self.findChildren(QComboBox):
            cb.setFocusPolicy(Qt.StrongFocus)
            cb.installEventFilter(scroll_ignorer)
