"""The main PyChamber application window."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pychamber.settings import SETTINGS

if TYPE_CHECKING:
    from typing import Dict

import textwrap
import webbrowser

import cloudpickle as pickle
import qdarkstyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from pyqtgraph.console import ConsoleWidget

import pychamber.plugins as plugins
from pychamber.logger import LOG
from pychamber.plugins import PyChamberPanelPlugin, PyChamberPlugin, PyChamberPluginError
from pychamber.ui import resources_rc, size_policy, font  # noqa: F401
from pychamber.widgets import AboutPyChamberDialog, LogViewer, SettingsDialog


class MainWindow(QMainWindow):
    """PyChamber.

    This is the main window of PyChamber. It is responsible for handling user
    interactions, managing plugins, and providing a menu and status bar.
    """

    REQUIRED_PLUGINS = [
        plugins.AnalyzerPlugin,
        plugins.CalibrationPlugin,
        plugins.ExperimentPlugin,
        plugins.PositionerPlugin,
        plugins.PlotsPlugin,
    ]
    """list(PyChamberPlugin): List of minimum plugins required to run PyChamber"""

    def __init__(self, *args) -> None:
        """Create the PyChamber main window.

        Does some basic initialization, but expects the launching (in app.py) to
        call methods to do the actual setup.
        """
        super().__init__(*args)
        LOG.debug("Constructing MainWindow...")

        self.setWindowTitle("PyChamber")
        self.setWindowIcon(QIcon(":/logo.png"))
        self.app = QApplication.instance()

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.settings_dialog = SettingsDialog(self)

        self.registered_plugins: Dict[str, PyChamberPlugin] = {}

    def _on_save_triggered(self) -> None:
        LOG.debug("Launching save dialog...")
        experiment = cast(plugins.ExperimentPlugin, self.get_plugin("experiment"))
        ntwk_model = experiment.ntwk_model
        if len(ntwk_model) == 0:
            QMessageBox.warning(
                self, "No data", "No data to save. Run an experiment first."
            )
            return
        to_save = ntwk_model.data()

        save_name, _ = QFileDialog.getSaveFileName()
        if save_name != "":
            with open(save_name, 'wb') as save_file:
                pickle.dump(to_save, save_file)

    def _on_load_triggered(self) -> None:
        # TODO: Handle NetworkModel.data_loaded
        LOG.debug("Launching load dialog...")
        experiment = cast(plugins.ExperimentPlugin, self.get_plugin("experiment"))
        ntwk_model = experiment.ntwk_model
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            try:
                LOG.debug(f"Loading {file_name}")
                with open(file_name, 'rb') as ff:
                    data = pickle.load(ff)
                    ntwk_model.load_data(data)
            except Exception:
                QMessageBox.critical(
                    self, "Invalid File", "The specified file is invalid"
                )
                return

    def _on_settings_triggered(self) -> None:
        LOG.debug("Launching settings dialog...")
        self.settings_dialog.populate(self.registered_plugins.copy())
        self.settings_dialog.exec_()

    def _on_python_interpreter_triggered(self) -> None:
        LOG.debug("Launching Python interpreter...")

        namespace = self.registered_plugins.copy()

        banner = textwrap.dedent(
            f"""
                This is PyChamber's interactive console. The namespace has been
                populated with all plugins active when the console was loaded.

                The currently loaded plugins are: {list(self.registered_plugins.keys())}
            """
        )
        console = ConsoleWidget(namespace=namespace, text=banner)
        console.show()
        console.setWindowTitle("PyChamber - Console")

    def setup(self) -> None:
        """Setup the window's menu and widgets."""
        self._setup_menu()
        self._add_widgets()

    def post_visible_setup(self) -> None:
        """Initialize registered plugins."""
        LOG.debug("Running post-visible setups")
        to_init = list(self.registered_plugins.values())
        for plugin in to_init:
            plugin._post_visible_setup()

        self.apply_theme(SETTINGS["theme"])

        self.settings_dialog.main_theme_changed.connect(self.apply_theme)
        self.statusBar().showMessage("Welcome to PyChamber!", 2000)

    def center(self) -> None:
        """Center the window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        """Warn the user on close.

        Arguments:
            event: the event that triggered the close.
        """
        LOG.debug("Close event triggered")
        warning = QMessageBox()
        warning.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        warning.setDefaultButton(QMessageBox.Cancel)
        warning.setText("Are you sure you want to quit?\n(Any unsaved data will be LOST)")

        resp = warning.exec_()
        if resp == QMessageBox.Yes:
            LOG.debug("Close event accepted")
            del self.settings  # Saves settings
            super().closeEvent(event)
        else:
            LOG.debug("Close event canceled")
            event.ignore()

    def register_plugin(self, plugin: PyChamberPlugin) -> None:
        """Register a plugin.

        This registers the plugin with the application (including settings). All
        panel plugins are added to the left-side scrolling panel and any other
        plugins are added to the main layout. This might change for plugins the
        may not want to be in either place (e.g. tools accessible from the menu)

        For more information about creating plugins, see the plugins module documentation.

        Arguments:
            plugin: plugin to register
        """
        assert plugin.NAME is not None
        if plugin.NAME in self.registered_plugins:
            raise PyChamberPluginError(
                f"A plugin is already registered with {plugin.NAME}"
            )
        plugin._register()
        self.registered_plugins[plugin.NAME] = plugin

        if plugin.NAME == "experiment":
            LOG.debug(f"Adding {plugin.NAME} to left side")
            self.left_side_layout.insertWidget(0, plugin)
        elif plugin.NAME == "plots":
            LOG.debug(f"Adding {plugin.NAME} to right side")
            self.right_side_layout.addWidget(plugin)
        else:
            if isinstance(plugin, PyChamberPanelPlugin):
                LOG.debug(f"Adding {plugin.NAME} to panel")
                self.panel_layout.addWidget(plugin)
            elif isinstance(plugin, PyChamberPlugin):
                pass

    def unregister_plugin(self, name: str) -> None:
        """Remove a plugin from PyChamber (NOT IMPLEMENTED).

        Arguments:
            plugin: plugin to remove
        """
        if name in [plugin.NAME for plugin in self.REQUIRED_PLUGINS]:  # type: ignore
            QMessageBox.critical(
                self, "Required Plugin", f"{name} is a core plugin and cannot be removed"
            )
        elif name not in self.registered_plugins.keys():
            LOG.debug("This plugin isn't activated. How did you get here...?")
        else:
            raise NotImplementedError

    def get_plugin(self, plugin_name: str) -> PyChamberPlugin:
        """Retrieve plugin instance.

        All plugins are registered in the MainWindow and have a reference to it.
        Plugins that need to interoperate with other plugins can use this
        function to retrieve those plugin instances.

        Arguments:
            plugin_name: name of the plugin. This is defined by each plugin.
        """
        return self.registered_plugins[plugin_name]

    def _setup_menu(self) -> None:
        LOG.debug("Setting up menu...")
        self.menu = self.menuBar()

        self.file = self.menu.addMenu("File")
        self.save = self.file.addAction("Save")
        self.load = self.file.addAction("Load")
        self.file.addSeparator()
        self.settings = self.file.addAction("Settings")
        self.file.addSeparator()
        self.quit = self.file.addAction("Quit")

        self.save.triggered.connect(self._on_save_triggered)
        self.load.triggered.connect(self._on_load_triggered)
        self.settings.triggered.connect(self._on_settings_triggered)
        self.quit.triggered.connect(self.close)

        self.tools = self.menu.addMenu("Tools")
        self.python_interpreter = self.tools.addAction("Python Terminal")

        self.python_interpreter.triggered.connect(self._on_python_interpreter_triggered)

        self.help = self.menu.addMenu("Help")
        self.bug = self.help.addAction("Submit a Bug")
        self.help.addSeparator()
        self.about = self.help.addAction("About")
        self.log = self.help.addAction("View Log")

        bug_report_url = "https://github.com/HRG-Lab/PyChamber/issues/new"
        self.bug.triggered.connect(lambda: webbrowser.open(bug_report_url))
        self.about.triggered.connect(AboutPyChamberDialog.display)
        self.log.triggered.connect(LogViewer.display)

    def _add_widgets(self) -> None:
        LOG.debug("Setting up widgets...")

        self.panel_groupbox = QGroupBox("Plugins")
        self.panel_groupbox.setFont(font["BOLD_12"])
        self.panel_scroll_area = QScrollArea(widgetResizable=True)
        self.panel_scroll_area.setStyleSheet("QScrollArea {border: none;}")
        self.panel_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.panel_widget = QWidget()
        self.panel_scroll_area.setWidget(self.panel_widget)

        self.panel_layout = QVBoxLayout(self.panel_widget)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_groupbox.setLayout(QVBoxLayout())
        self.panel_groupbox.layout().addWidget(self.panel_scroll_area)

        self.left_side_layout = QVBoxLayout()
        self.right_side_layout = QVBoxLayout()

        self.left_side_layout.addWidget(self.panel_groupbox)

        self.main_layout.addLayout(self.left_side_layout, stretch=2)
        self.main_layout.addLayout(self.right_side_layout, stretch=5)

        for plugin in self.REQUIRED_PLUGINS:
            self.register_plugin(cast(PyChamberPlugin, plugin(self)))

        to_init = list(self.registered_plugins.values())

        for plugin in to_init:
            plugin._setup()

        self.panel_layout.addStretch()
        self.panel_groupbox.setMinimumWidth(500)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet(
            "QLabel {padding-top: 5px; margin-bottom: 0px;"
            "padding-left: 10px; padding-right: 10px;}"
        )
        self.left_side_layout.insertWidget(0, self.logo_label)

    def apply_theme(self, theme: str) -> None:
        from qdarkstyle.light.palette import LightPalette

        if theme.lower() == "light":
            logo = QPixmap(":/logo_with_txt_light.png")
            self.logo_label.setPixmap(logo.scaledToWidth(350))
            self.app.setStyleSheet(
                qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette)
            )

        elif theme.lower() == "dark":
            logo = QPixmap(":/logo_with_txt_dark.png")
            self.logo_label.setPixmap(logo.scaledToWidth(350))
            self.app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        else:
            QMessageBox.critical(self, "Unrecognized theme", "Unrecognized color theme.")
            return

        SETTINGS["theme"] = theme

        for plugin in self.registered_plugins.values():
            plugin.apply_theme(theme)
