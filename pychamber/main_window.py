"""The main PyChamber application window."""
import webbrowser
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Dict

import cloudpickle as pickle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import pychamber.plugins as plugins
from pychamber.logger import LOG
from pychamber.plugins import PyChamberPanelPlugin, PyChamberPlugin, PyChamberPluginError
from pychamber.ui import resources_rc, size_policy  # noqa: F401
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

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

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
        SettingsDialog.display()

    def _on_python_interpreter_triggered(self) -> None:
        LOG.debug("Launching Python interpreter...")

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

        if isinstance(plugin, PyChamberPanelPlugin):
            LOG.debug(f"Adding {plugin.NAME} to panel")
            self.panel_layout.addWidget(plugin)
        elif isinstance(plugin, PyChamberPlugin):
            LOG.debug(f"Adding {plugin.NAME} to right side")
            self.right_side_layout.addWidget(plugin)

    def unregister_plugin(self, plugin: PyChamberPlugin) -> None:
        """Remove a plugin from PyChamber (NOT IMPLEMENTED).

        Arguments:
            plugin: plugin to remove
        """
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

        self.panel_scroll_area = QScrollArea(widgetResizable=True)
        self.panel_widget = QWidget()
        self.panel_scroll_area.setWidget(self.panel_widget)
        self.panel_layout = QVBoxLayout(self.panel_widget)
        self.panel_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.panel_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_side_layout = QVBoxLayout()

        self.main_layout.addWidget(self.panel_scroll_area)
        self.main_layout.addLayout(self.right_side_layout)

        for plugin in self.REQUIRED_PLUGINS:
            self.register_plugin(cast(PyChamberPlugin, plugin(self)))

        to_init = list(self.registered_plugins.values())

        for plugin in to_init:
            plugin._setup()

        self.panel_layout.addStretch()
        self.panel_scroll_area.setFixedWidth(
            self.panel_widget.minimumSizeHint().width()
            + self.panel_scroll_area.verticalScrollBar().sizeHint().width()
        )