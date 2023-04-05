from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

import importlib
import pkgutil
import sys
from typing import cast

import pychamber.plugins


class PluginNameCollisionError(RuntimeError):
    def __init__(self, name: str, module: str) -> None:
        super().__init__(f"{name} already exists in {module}")


class PluginInterface:
    """Interface for plugins to adhere to."""

    @staticmethod
    def initialize() -> None:
        """Initialize the plugin"""


class PluginManager:
    """Manage plugins"""

    def __init__(self) -> None:
        self.plugins = set()
        self.plugin_dirs = []  # TODO make this a configuration option

        self.plugins |= self.get_local_plugins()
        self.plugins |= self.get_user_plugins()

    def iter_namespace(self, ns_pkg) -> Iterator[pkgutil.ModuleInfo]:
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    def get_local_plugins(self) -> set[str]:
        return {name for _, name, _ in self.iter_namespace(pychamber.plugins)}

    def get_user_plugins(self) -> set[str]:
        return set()

    def import_plugin(self, name: str) -> PluginInterface:
        """Import a plugin module"""
        return cast(PluginInterface, importlib.import_module(name))

    def load_plugins(self) -> None:
        """Initialize the registered plugins"""

        for plugin_name in self.plugins:
            plugin = self.import_plugin(plugin_name)
            plugin.initialize()

    def register_class_with_module(cls: type, module_name: str) -> None:
        module = sys.modules[module_name]

        if module.get(cls.__name__) is None:
            setattr(module, cls.__name__, cls)
        else:
            raise PluginNameCollisionError(cls.__name__, module_name)
