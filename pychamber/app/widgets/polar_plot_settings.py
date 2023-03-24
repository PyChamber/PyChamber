import functools

import qtawesome as qta
from PySide6.QtWidgets import QWidget

from ..ui.polar_plot_settings import Ui_PolarPlotSettings
from ..ui.polar_trace_settings import Ui_PolarTraceSettings
from .polar_plot import PolarPlotWidget


class PolarTraceSettings(QWidget, Ui_PolarTraceSettings):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        x_icon = qta.icon("fa5s.times-circle")
        self.remove_trace_btn.setIcon(x_icon)
        self.trace_color_btn.update_text = False


class PolarPlotSettings(QWidget, Ui_PolarPlotSettings):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.connect_signals()

    def connect_signals(self) -> None:
        self.add_trace_btn.pressed.connect(self.on_add_trace_btn_pressed)

    def on_remove_trace_btn_pressed(self, tr: PolarTraceSettings) -> None:
        self.layout().removeWidget(tr)
        tr.deleteLater()

        if self.layout().count() < 6:  # 4 traces + button + spacer
            self.add_trace_btn.show()

    def on_add_trace_btn_pressed(self) -> None:
        tr = PolarTraceSettings(self)
        tr.remove_trace_btn.pressed.connect(functools.partial(self.on_remove_trace_btn_pressed, tr))
        self.layout().insertWidget(0, tr)
        if self.layout().count() >= 6:  # 4 traces + button + spacer
            self.add_trace_btn.hide()

    def create_plot(self, parent: QWidget | None = None) -> PolarPlotWidget:
        return PolarPlotWidget(parent=parent)
