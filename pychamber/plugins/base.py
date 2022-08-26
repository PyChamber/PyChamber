"""Defines the basic plugin classes."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from pychamber.main_window import MainWindow

from PyQt5.QtWidgets import QWidget


class PyChamberPluginError(Exception):
    """An exception specific to the plugin system of PyChamber."""

    pass


class PyChamberPlugin(QWidget):
    """A basic plugin.

    A PyChamberPlugin is a widget that takes the main PyChamber window as its
    parent.

    It must define NAME at a minimum which MUST be unique. If PyChamber
    tries to load to plugins with the same name, it will raise a
    PyChamberPluginError.

    If a plugin doesn't define a name, it will raise a PyChamberPluginError.

    Currently the REQUIRED attribute is not used, but may be used later to allow
    PyChamber to manage plugin dependencies.

    CONFIG defines the configuration settings of the plugin along with their defaults.
    """

    NAME: Optional[str] = None
    CONFIG: Dict = dict()
    REQUIRED: List[PyChamberPlugin] = []

    def __init__(self, main_window: MainWindow) -> None:
        """Instantiate the plugin.

        Arguments:
            main_window: this MUST be the PyChamber main window to allow the
                plugin to communicate with other plugins
        """
        super().__init__(main_window)

        self.main = main_window

    def _register(self) -> None:
        from pychamber.settings import SETTINGS

        if self.NAME is None:
            raise PyChamberPluginError("Plugin must define NAME")

        SETTINGS.register_plugin(self)

    def _unregister(self) -> None:
        self.main.unregister_plugin(self)

    def _setup(self) -> None:
        """The minimum setup necessary to display the plugin.

        This and _post_visible_setup must be defined in any plugin. Even if they
        are just pass. These functions are called in PyChamber's main window
        setup and post_visible_setup functions (or later if plugins are added
        after the initial setup).

        Code that is not necessary to display the actual plugin widget should be
        in _post_visible_setup

        Seperating this from _post_visible_setup makes it seem like PyChamber is
        loading faster as backends can be configured after the visible bits are shown.
        """
        ...

    def _post_visible_setup(self) -> None:
        """Code run after the plugin widget is shown."""
        ...


class PyChamberPanelPlugin(PyChamberPlugin):
    """A plugin that should be added to the PyChamber panel.

    This is exactly the same as a PyChamberPlugin, except subclassing from this
    tells PyChamber it should add the plugin to the plugin panel in the main
    window (the scrollable area on the left).
    """

    pass
