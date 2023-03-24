import functools

import pyqtgraph as pg
import qtawesome as qta
from PySide6.QtWidgets import QWidget

from ..ui.rect_plot_settings import Ui_RectPlotSettings
from ..ui.rect_trace_settings import Ui_RectTraceSettings


class RectTraceSettings(QWidget, Ui_RectTraceSettings):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        x_icon = qta.icon("fa5s.times-circle")
        self.remove_trace_btn.setIcon(x_icon)
        self.trace_color_btn.update_text = False


class RectPlotSettings(QWidget, Ui_RectPlotSettings):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.connect_signals()

    def connect_signals(self) -> None:
        self.add_trace_btn.pressed.connect(self.on_add_trace_btn_pressed)

    def on_remove_trace_btn_pressed(self, tr: RectTraceSettings) -> None:
        self.layout().removeWidget(tr)
        tr.deleteLater()

        if self.layout().count() < 6:  # 4 traces + button + spacer
            self.add_trace_btn.show()

    def on_add_trace_btn_pressed(self) -> None:
        tr = RectTraceSettings(self)
        tr.remove_trace_btn.pressed.connect(functools.partial(self.on_remove_trace_btn_pressed, tr))
        self.layout().insertWidget(0, tr)
        if self.layout().count() >= 6:  # 4 traces + button + spacer
            self.add_trace_btn.hide()

    def create_plot(self, parent: QWidget | None = None) -> pg.PlotWidget:
        return pg.PlotWidget(parent=parent)
