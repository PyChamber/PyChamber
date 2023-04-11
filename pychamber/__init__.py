from . import plugins, positioner
from .calibration import Calibration
from .experiment import Experiment
from .experiment_result import ExperimentResult

from .api import PluginManager

PluginManager().load_plugins()

__version__ = "0.1.0"
