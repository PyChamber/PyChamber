"""Contains all of the widgets used in PyChamber.

Plugins can use these widgets but any widgets specific to a plugin should local
to that plugin.
"""
from .about import AboutPyChamberDialog
from .collapsible_section import CollapsibleSection
from .freq_lineedit import FrequencyLineEdit
from .freq_spin_box import FrequencySpinBox
from .freq_validator import FrequencyValidator
from .horz_tab_widget import HorizontalTabWidget
from .log_viewer import LogViewer
from .mpl_widget import MplPolarWidget, MplRectWidget, MplWidget, PlotLimits
from .settings_dialog import SettingsDialog
