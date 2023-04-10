from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from pychamber import ExperimentResult

import functools

import numpy as np
import pyqtgraph as pg
import qtawesome as qta
from qtpy.QtCore import QThreadPool
from qtpy.QtWidgets import QWidget
from skrf import mathFunctions

from pychamber.app.logger import LOG
from pychamber.app.task_runner import TaskRunner

from ..ui.rect_plot_settings import Ui_RectPlotSettings
from ..ui.rect_trace_settings import Ui_RectTraceSettings
from .plot_widget import PlotWidget


class RectTraceSettings(QWidget, Ui_RectTraceSettings):
    def __init__(
        self,
        plot_item: pg.PlotDataItem,
        data: ExperimentResult,
        x_param: str,
        y_func: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        LOG.debug("Creating rectangular trace settings")
        self.setupUi(self)

        self.plot_item = plot_item
        self.data = data
        self._x_param = x_param
        self._y_func = y_func

        x_icon = qta.icon("fa5s.times-circle")
        self.remove_rect_trace.setIcon(x_icon)
        self.connect_signals()
        self.on_new_data()

    def connect_signals(self):
        LOG.debug("Connecting signals")
        self.trace_color_btn.sigColorChanged.connect(self.on_pen_settings_changed)
        self.trace_width_dsb.valueChanged.connect(self.on_pen_settings_changed)
        self.freq_le.editingFinished.connect(self.on_new_data)
        self.phi_lsb.valueChanged.connect(self.on_new_data)
        self.theta_lsb.valueChanged.connect(self.on_new_data)
        self.pol_cb.activated.connect(self.on_new_data)
        self.calibrated_checkbox.toggled.connect(lambda _: self.on_new_data())
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)

    def on_pen_settings_changed(self):
        pen = pg.mkPen(self.trace_color_btn.color(), width=self.trace_width_dsb.value())
        self.plot_item.setPen(pen)

    def set_frequency_mode(self):
        self.freq_widget.hide()
        self.phi_widget.show()
        self.theta_widget.show()

    def set_ang_mode(self, param: str):
        self.freq_widget.show()
        self.phi_widget.setHidden(param == "phis")
        self.theta_widget.setVisible(param == "phis")

    @staticmethod
    def get_data(
        data: ExperimentResult,
        x_param: str,
        y_func: Callable,
        pol: str,
        f: float,
        phi: float,
        theta: float,
        calibrated: bool
    ):
        if f is None or pol == "":
            return None

        data.rw_lock.lockForRead()
        if x_param == "f":
            x_data = data.f
            vals = data.get_over_freq_vals(pol, theta, phi, calibrated=calibrated)
        elif x_param == "thetas":
            x_data = data.thetas
            vals = data.get_theta_cut(pol, f, phi, calibrated=calibrated)
        elif x_param == "phis":
            x_data = data.phis
            vals = data.get_phi_cut(pol, f, theta, calibrated=calibrated)
        data.rw_lock.unlock()

        y_data = y_func(vals)

        return (x_data, y_data)

    def on_get_data_result(self, result: tuple[np.ndarray, np.ndarray] | None):
        LOG.debug("Data retrived. Updating plot")
        if result is None:
            return

        self.plot_item.setData(result[0], result[1])

    def on_new_data(self):
        LOG.debug("Got new data")
        if self.data is None:
            return
        if len(self.data) == 0:
            return

        current_pols_list = [self.pol_cb.itemText(i) for i in range(self.pol_cb.count())]
        if set(current_pols_list) != set(self.data.polarizations):
            self.pol_cb.clear()
            self.pol_cb.addItems(self.data.polarizations)

        self.phi_lsb.setValues(self.data.phis)
        self.theta_lsb.setValues(self.data.thetas)

        x_param = self.x_param
        y_func = self.y_func
        pol = self.polarization
        freq = self.freq_le.value()
        if freq is None:
            self.freq_le.setText(self.data.f[0])
            freq = self.freq_le.value()
        phi = float(self.phi_lsb.getValue())
        theta = float(self.theta_lsb.getValue())
        calibrated = self.calibrated_checkbox.isChecked()
        self.calibrated_checkbox.setVisible(self.data.has_calibrated_data)
        if not self.data.has_calibrated_data:
            calibrated = False

        data_grabber = TaskRunner(
            self.get_data,
            data=self.data,
            x_param=x_param,
            y_func=y_func,
            pol=pol,
            f=freq,
            phi=phi,
            theta=theta,
            calibrated=calibrated
        )
        data_grabber.signals.gotResult.connect(self.on_get_data_result)
        QThreadPool.globalInstance().start(data_grabber)

    @property
    def x_param(self) -> str:
        return self._x_param

    @x_param.setter
    def x_param(self, param: str) -> None:
        self._x_param = param
        if param == "f":
            self.set_frequency_mode()
        else:
            self.set_ang_mode(param)
        self.on_new_data()

    @property
    def y_func(self) -> Callable:
        return self._y_func

    @y_func.setter
    def y_func(self, func: Callable) -> None:
        self._y_func = func
        self.on_new_data()

    @property
    def polarization(self) -> str:
        return self.pol_cb.currentText()


class RectPlotSettings(QWidget, Ui_RectPlotSettings):
    x_params = [
        ("Frequency", ("Frequency", "f", "Hz")),
        ("Phi (Azimuth)", ("Phi", "phis", "°")),
        ("Theta (Elevation)", ("Theta", "thetas", "°")),
    ]

    y_params = [
        ("Magnitude [linear]", ("Magnitude", mathFunctions.complex_2_magnitude, "")),
        (
            "Magnitude [dB]",
            ("Magnitude", lambda data: mathFunctions.complex_2_db(np.where(data == 0, 1e-20, data)), "dB"),
        ),
        ("Phase", ("Phase", mathFunctions.complex_2_degree, "°")),
        (
            "Unwrapped Phase",
            (
                "Phase [unwrapped]",
                lambda data: np.unwrap(np.deg2rad(mathFunctions.complex_2_degree(data)), axis=0),
                "°",
            ),
        ),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        LOG.debug("Creating rectangular plot settings")
        self.setupUi(self)

        self.postvisible_setup()

    def postvisible_setup(self):
        for name, var_info in self.x_params:
            self.x_var_cb.addItem(name, userData=var_info)
        for name, var_info in self.y_params:
            self.y_var_cb.addItem(name, userData=var_info)


class RectPlotWidget(PlotWidget):
    def __init__(self, data: ExperimentResult, title: str, parent: QWidget | None = None) -> None:
        plot = pg.PlotWidget()
        controls = RectPlotSettings()
        LOG.debug("Creating rectangular plot widget")
        super().__init__(plot=plot, controls=controls, data=data, title=title, parent=parent)

        self.plot.getPlotItem().setTitle(title)

        self._traces = []
        self.connect_signals()
        self.postvisible_setup()

    def connect_signals(self) -> None:
        LOG.debug("Connecting signals")
        self.controls.title_le.textChanged.connect(self.titleChanged.emit)
        self.controls.title_le.textChanged.connect(self.plot.getPlotItem().setTitle)
        self.controls.add_trace_btn.pressed.connect(self.on_add_trace_btn_pressed)
        self.controls.bg_color_btn.sigColorChanged.connect(lambda btn: self.on_bg_color_changed(btn.color()))
        self.controls.x_var_cb.currentIndexChanged.connect(lambda _: self.on_xvar_changed())
        self.controls.y_var_cb.currentIndexChanged.connect(lambda _: self.on_yvar_changed())
        self.controls.min_sb.valueChanged.connect(lambda val: self.on_y_range_changed(ymin=val))
        self.controls.max_sb.valueChanged.connect(lambda val: self.on_y_range_changed(ymax=val))
        self.controls.autoscale_checkbox.toggled.connect(self.on_autoscale_toggled)

    def postvisible_setup(self):
        self.on_xvar_changed()
        self.on_yvar_changed()
        self.plot.enableAutoRange(axis="x")
        self.plot.enableAutoRange(axis="y", enable=self.controls.autoscale_checkbox.isChecked())
        self.plot.setMouseEnabled(x=False, y=True)

    @property
    def data(self) -> ExperimentResult | None:
        return self._data

    @data.setter
    def data(self, result: ExperimentResult):
        LOG.debug("Setting data")
        self._data = result
        for trace in self._traces:
            trace.data = self._data
            if self.data is not None:
                self.data.dataAppended.connect(trace.on_new_data)
            trace.on_new_data()

    def on_bg_color_changed(self, color):
        self.plot.setBackground(color)

    def on_y_range_changed(self, ymin=None, ymax=None):
        ymin = ymin if ymin is not None else self.controls.min_sb.value()
        ymax = ymax if ymax is not None else self.controls.max_sb.value()
        self.plot.setYRange(ymin, ymax)

    def on_xvar_changed(self):
        x_param = self.controls.x_var_cb.currentData()
        for tr in self._traces:
            tr.x_param = x_param[1]

        label_params = {"text": x_param[0]}
        label_params["units"] = x_param[2]

        self.plot.getPlotItem().getAxis("bottom").setLabel(**label_params)

    def on_yvar_changed(self):
        y_param = self.controls.y_var_cb.currentData()
        for tr in self._traces:
            tr.y_func = y_param[1]

        label_params = {"text": y_param[0]}
        label_params["units"] = y_param[2]

        self.plot.getPlotItem().getAxis("left").setLabel(**label_params)

    def on_autoscale_toggled(self, state: bool):
        self.plot.enableAutoRange(axis="y", enable=state)
        self.controls.min_label.setHidden(state)
        self.controls.min_sb.setHidden(state)
        self.controls.max_label.setHidden(state)
        self.controls.max_sb.setHidden(state)
        if state:
            self.plot.autoRange()
        else:
            self.on_y_range_changed(self.controls.min_sb.value(), self.controls.max_sb.value())

    def on_remove_trace_btn_pressed(self, tr: RectTraceSettings) -> None:
        LOG.debug("Removing trace")
        self.plot.removeItem(tr.plot_item)
        self.controls.layout().removeWidget(tr)
        self._traces.remove(tr)
        tr.deleteLater()

        if len(self._traces) < 4:
            self.controls.add_trace_btn.show()

    def on_add_trace_btn_pressed(self) -> None:
        LOG.debug("Adding trace")
        plot_item = self.plot.plot()
        initial_x_param = self.controls.x_var_cb.currentData()[1]
        initial_y_func = self.controls.y_var_cb.currentData()[1]
        tr = RectTraceSettings(plot_item, self.data, x_param=initial_x_param, y_func=initial_y_func, parent=self)
        tr.remove_rect_trace.pressed.connect(functools.partial(self.on_remove_trace_btn_pressed, tr))
        self._traces.append(tr)
        self.controls.layout().insertWidget(self.controls.layout().count() - 2, tr)

        # TODO: Figure out QScrollArea. It's annoying
        if len(self._traces) >= 2:
            self.controls.add_trace_btn.hide()
