import functools
from operator import setitem

from PySide6.QtWidgets import QWidget

from pychamber.app.ui.experiment_widget import Ui_ExperimentWidget
from pychamber.settings import CONF

from .collapsible_widget import CollapsibleWidget


class ExperimentWidget(QWidget, Ui_ExperimentWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)


class ExperimentControls(CollapsibleWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, name="Experiment")

        self.setupUi()
        self.postvisible_setup()
        self.connect_signals()

    def setupUi(self) -> None:
        self.widget = ExperimentWidget(self)
        self.addWidget(self.widget)
        self.recalculateSize()

    def connect_signals(self) -> None:
        self.widget.az_start_dsb.valueChanged.connect(functools.partial(setitem, CONF, "az_start"))
        self.widget.az_stop_dsb.valueChanged.connect(functools.partial(setitem, CONF, "az_stop"))
        self.widget.az_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "az_step"))
        self.widget.el_start_dsb.valueChanged.connect(functools.partial(setitem, CONF, "el_start"))
        self.widget.el_stop_dsb.valueChanged.connect(functools.partial(setitem, CONF, "el_stop"))
        self.widget.el_step_dsb.valueChanged.connect(functools.partial(setitem, CONF, "el_step"))

    def postvisible_setup(self) -> None:
        widget_map = {
            "az_start": (self.widget.az_start_dsb, 0, float),
            "az_stop": (self.widget.az_stop_dsb, 90, float),
            "az_step": (self.widget.az_step_dsb, 1, float),
            "el_start": (self.widget.el_start_dsb, 0, float),
            "el_stop": (self.widget.el_stop_dsb, 90, float),
            "el_step": (self.widget.el_step_dsb, 1, float),
        }
        CONF.register_widgets(widget_map)
