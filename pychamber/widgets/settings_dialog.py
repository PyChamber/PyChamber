from __future__ import annotations

from typing import TYPE_CHECKING

from pychamber.settings import SETTINGS

if TYPE_CHECKING:
    from typing import Dict

    from pychamber.main_window import MainWindow
    from pychamber.plugins.base import PyChamberPlugin

"""Defines a window to change application settings."""
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from pychamber.logger import LOG
from pychamber.widgets import HorizontalTabWidget
from pychamber.ui import font


class SettingsDialog(QDialog):
    """A dialog of user-editable settings.

    This may change soon to enable per-plugin settings.
    """

    main_theme_changed = pyqtSignal(str)

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        self._setup()
        self.plugins: Dict[str, PyChamberPlugin] = {}

    def populate(self, plugins: Dict[str, PyChamberPlugin]) -> None:
        for name, plugin in plugins.items():
            if name in self.plugins:
                continue
            name = name.capitalize()

            widget = QWidget()
            _ = QFormLayout(widget)
            self.settings_tab_widget.addTab(widget, name)
            self._load_plugin_settings(plugin, widget)

        self.plugins = plugins

    def _setup(self) -> None:
        """Add the control widgets and dialog buttons."""
        self._add_widgets()
        self._setup_buttons()

    def sizeHint(self) -> QSize:
        return QSize(600, 400)

    def _add_widgets(self) -> None:
        self.main_layout = QVBoxLayout()

        self.settings_tab_widget = HorizontalTabWidget()
        widget = QWidget()
        _ = QFormLayout(widget)
        self._load_general_settings(widget)
        self.settings_tab_widget.addTab(widget, "General")
        self.main_layout.addWidget(self.settings_tab_widget)

        self.settings_tab_widget.tabBar().setFont(font["BOLD_10"])
        self.settings_tab_widget.tabBar().setStyleSheet(
            "QTabBar::tab {"
            "    padding-top: 10px;"
            "    padding-bottom: 10px;"
            "    padding-left: 5px;"
            "    padding-right: 5px;"
            "}"
        )

        self.setLayout(self.main_layout)

    def _setup_buttons(self) -> None:
        _buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(_buttons)
        self.button_box.button(QDialogButtonBox.Ok).clicked.connect(self.close)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

    def _add_plugin(self) -> None:
        QMessageBox.warning(
            self,
            "Not Implemented.",
            "Optional plugins are not yet supported. Stay tuned!",
        )

    def _remove_plugin(self) -> None:
        raise NotImplementedError

    def _load_plugin_settings(self, plugin: PyChamberPlugin, parent) -> None:
        LOG.debug(f"{parent=}")

        settings = plugin._user_settings()
        for setting in settings:
            parent.layout().addRow(setting[1], setting[2])

    def _load_general_settings(self, parent) -> None:
        theme_label = QLabel("Theme")
        theme_combobox = QComboBox()
        theme_combobox.addItems(["Light", "Dark"])
        theme_combobox.setCurrentText(SETTINGS["theme"])

        parent.layout().addRow(theme_label, theme_combobox)

        theme_combobox.currentTextChanged.connect(self.main_theme_changed.emit)
