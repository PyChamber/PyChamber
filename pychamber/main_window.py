import webbrowser
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Dict

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

import cloudpickle as pickle
import pychamber.plugins as plugins
from pychamber.logger import log
from pychamber.plugins import PyChamberPanelPlugin, PyChamberPlugin, PyChamberPluginError
from pychamber.ui import resources_rc, size_policy  # noqa: F401
from pychamber.widgets import AboutPyChamberDialog, SettingsDialog


class MainWindow(QMainWindow):
    REQUIRED_PLUGINS = [
        plugins.AnalyzerPlugin,
        plugins.CalibrationPlugin,
        plugins.ExperimentPlugin,
        plugins.PositionerPlugin,
        plugins.PlotsPlugin,
    ]

    def __init__(self, *args) -> None:
        super().__init__(*args)
        log.debug("Constructing MainWindow...")

        self.setWindowTitle("PyChamber")
        self.setWindowIcon(QIcon(":/logo.png"))

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.registered_plugins: Dict[str, PyChamberPlugin] = {}

    def _on_save_triggered(self) -> None:
        log.debug("Launching save dialog...")
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
        log.debug("Launching load dialog...")
        experiment = cast(plugins.ExperimentPlugin, self.get_plugin("experiment"))
        plots = cast(plugins.PlotsPlugin, self.get_plugin("plots"))
        ntwk_model = experiment.ntwk_model
        file_name, _ = QFileDialog.getOpenFileName()
        if file_name != "":
            try:
                log.debug(f"Loading {file_name}")
                with open(file_name, 'rb') as ff:
                    data = pickle.load(ff)

                    ntwk_model.load_data(data)
            except Exception:
                QMessageBox.critical(
                    self, "Invalid File", "The specified file is invalid"
                )
                return

    def _on_settings_triggered(self) -> None:
        log.debug("Launching settings dialog...")
        SettingsDialog.display()

    def _on_python_interpreter_triggered(self) -> None:
        log.debug("Launching Python interpreter...")

    def _on_about_triggered(self) -> None:
        log.debug("Launching about window...")

    def _on_log_triggered(self) -> None:
        log.debug("Launching log viewer...")

    def setup(self) -> None:
        self._setup_menu()
        self._add_widgets()

    def post_visible_setup(self) -> None:
        log.debug("Running post-visible setups")
        to_init = list(self.registered_plugins.values())
        for plugin in to_init:
            plugin._post_visible_setup()

        self.statusBar().showMessage("Welcome to PyChamber!", 2000)

    def center(self) -> None:
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        log.debug("Close event triggered")
        warning = QMessageBox()
        warning.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        warning.setDefaultButton(QMessageBox.Cancel)
        warning.setText("Are you sure you want to quit?\n(Any unsaved data will be LOST)")

        resp = warning.exec_()
        if resp == QMessageBox.Yes:
            log.debug("Close event accepted")
            del self.settings  # Saves settings
            super().closeEvent(event)
        else:
            log.debug("Close event canceled")
            event.ignore()

    def register_plugin(self, plugin: PyChamberPlugin) -> None:
        assert plugin.NAME is not None
        if plugin.NAME in self.registered_plugins:
            raise PyChamberPluginError(
                f"A plugin is already registered with {plugin.NAME}"
            )
        plugin._register()
        self.registered_plugins[plugin.NAME] = plugin

        if isinstance(plugin, PyChamberPanelPlugin):
            log.debug(f"Adding {plugin.NAME} to panel")
            self.panel_layout.addWidget(plugin)
        elif isinstance(plugin, PyChamberPlugin):
            log.debug(f"Adding {plugin.NAME} to right side")
            self.right_side_layout.addWidget(plugin)

    def unregister_plugin(self, plugin: PyChamberPlugin) -> None:
        pass

    def get_plugin(self, plugin_name: str) -> PyChamberPlugin:
        return self.registered_plugins[plugin_name]

    def _setup_menu(self) -> None:
        log.debug("Setting up menu...")
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
        self.log.triggered.connect(self._on_log_triggered)

    def _add_widgets(self) -> None:
        log.debug("Setting up widgets...")

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
