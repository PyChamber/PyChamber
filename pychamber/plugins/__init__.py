"""The plugin system of PyChamber as well as the default plugins.

The functionality of PyChamber is made through a set of plugins with the
potential for users to add new plugins in the future.
"""
from .analyzer import AnalyzerPlugin
from .base import PyChamberPanelPlugin, PyChamberPlugin, PyChamberPluginError
from .calibration import CalibrationPlugin
from .experiment import ExperimentPlugin
from .plots import PlotsPlugin
from .positioner import PositionerPlugin
