from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from pychamber import ExperimentResult

import functools

import numpy as np
import pyqtgraph as pg
import qtawesome as qta
from qtpy.QtCore import QThreadPool, Signal
from qtpy.QtWidgets import QWidget
from skrf import mathFunctions

from pychamber import math_fns
from pychamber.app.logger import LOG
from pychamber.app.task_runner import TaskRunner

from ..ui.polar_plot_settings import Ui_PolarPlotSettings
from ..ui.polar_trace_settings import Ui_PolarTraceSettings
from .plot_widget import PlotWidget
from .polar_plot import PolarPlot, PolarPlotDataItem


class PolarTraceSettings(QWidget, Ui_PolarTraceSettings):
    requestRedraw = Signal(PolarPlotDataItem)

    def __init__(
        self,
        plot_item: pg.PlotDataItem,
        data: ExperimentResult,
        ang_param: str,
        r_func: Callable,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        LOG.debug("Creating polar trace settings")
        self.setupUi(self)

        self.plot_item = plot_item
        self.data = data
        self._ang_param = ang_param
        self._r_func = r_func
        self.set_ang_mode(self.ang_param)

        x_icon = qta.icon("fa5s.times-circle")
        self.remove_polar_trace.setIcon(x_icon)
        self.connect_signals()
        self.on_new_data()

    def connect_signals(self):
        LOG.debug("Connecting signals")
        self.trace_color_btn.sigColorChanged.connect(self.on_pen_settings_changed)
        self.trace_width_dsb.valueChanged.connect(self.on_pen_settings_changed)
        self.freq_le.editingFinished.connect(self.on_new_data)
        self.pol_cb.activated.connect(self.on_new_data)
        self.theta_lsb.valueChanged.connect(self.on_new_data)
        self.phi_lsb.valueChanged.connect(self.on_new_data)
        self.calibrated_checkbox.toggled.connect(lambda _: self.on_new_data())
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)

    def on_pen_settings_changed(self):
        pen = pg.mkPen(self.trace_color_btn.color(), width=self.trace_width_dsb.value())
        self.plot_item.data_item.setPen(pen)

    def set_ang_mode(self, param: str):
        self.phi_widget.setHidden(param == "phis")
        self.theta_widget.setVisible(param == "phis")

    @staticmethod
    def get_data(
        data: ExperimentResult,
        ang_param: str,
        r_func: Callable,
        pol: str,
        f: float,
        theta: float,
        phi: float,
        calibrated: bool
    ):
        if f is None or pol == "":
            return None

        data.rw_lock.lockForRead()
        if ang_param == "thetas":
            ang_data = data.thetas
            vals = data.get_theta_cut(pol, f, phi, calibrated=calibrated)
        elif ang_param == "phis":
            ang_data = data.phis
            vals = data.get_phi_cut(pol, f, theta, calibrated=calibrated)
        data.rw_lock.unlock()

        r_data = r_func(vals)

        return (ang_data, r_data)

    def on_get_data_result(self, result: tuple[np.ndarray, np.ndarray] | None):
        LOG.debug("Data retrived. Updating plot")
        if result is None:
            return

        self.plot_item.theta = result[0]
        self.plot_item.r = result[1]
        self.requestRedraw.emit(self.plot_item)

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

        ang_param = self.ang_param
        r_func = self.r_func
        pol = self.polarization
        freq = self.freq_le.value()
        if freq is None:
            self.freq_le.setText(self.data.f[0])
            freq = self.freq_le.value()
        phi = float(self.phi_lsb.getValue())
        theta = float(self.theta_lsb.getValue())
        calibrated = self.calibrated_checkbox.isChecked()
        LOG.debug(f"retriving {'un' if not calibrated else ''}calibrated data")
        self.calibrated_checkbox.setVisible(self.data.has_calibrated_data)
        if not self.data.has_calibrated_data:
            calibrated = False

        data_grabber = TaskRunner(
            self.get_data,
            data=self.data,
            ang_param=ang_param,
            r_func=r_func,
            pol=pol,
            f=freq,
            phi=phi,
            theta=theta,
            calibrated=calibrated
        )
        data_grabber.signals.gotResult.connect(self.on_get_data_result)
        QThreadPool.globalInstance().start(data_grabber)

    @property
    def ang_param(self) -> str:
        return self._ang_param

    @ang_param.setter
    def ang_param(self, param: str) -> None:
        self._ang_param = param
        self.set_ang_mode(param)
        self.on_new_data()

    @property
    def r_func(self) -> str:
        return self._r_func

    @r_func.setter
    def r_func(self, func: Callable) -> None:
        self._r_func = func
        self.on_new_data()

    @property
    def polarization(self) -> str:
        return self.pol_cb.currentText()


class PolarPlotSettings(QWidget, Ui_PolarPlotSettings):
    ang_params = [
        ("Phi (Azimuth)", ("phis", "°")),
        ("Theta (Elevation)", ("thetas", "°")),
    ]
    r_params = [
        ("Magnitude [linear]", (mathFunctions.complex_2_magnitude, "")),
        ("Magnitude [dB]", (math_fns.clean_complex_to_db, "dB")),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        LOG.debug("Creating polar plot settings")
        self.setupUi(self)

        self.postvisible_setup()

    def postvisible_setup(self):
        for name, var_info in self.ang_params:
            self.ang_var_cb.addItem(name, userData=var_info)
        for name, var_info in self.r_params:
            self.r_var_cb.addItem(name, userData=var_info)

    def on_new_r_bounds(self, r_min, r_max, r_step):
        to_block = [self.min_sb, self.max_sb, self.step_sb]
        for widget in to_block:
            widget.blockSignals(True)

        self.min_sb.setValue(r_min)
        self.max_sb.setValue(r_max)
        self.step_sb.setValue(r_step)

        for widget in to_block:
            widget.blockSignals(False)


class PolarPlotWidget(PlotWidget):
    def __init__(self, data: ExperimentResult, title: str, parent: QWidget | None = None) -> None:
        plot = PolarPlot()
        controls = PolarPlotSettings()
        LOG.debug("Creating polar plot widget")
        super().__init__(plot=plot, controls=controls, data=data, title=title, parent=parent)

        self.plot.setTitle(title)

        self._traces = []
        self.connect_signals()
        self.postvisible_setup()

    def connect_signals(self) -> None:
        LOG.debug("Connecting signals")
        self.controls.title_le.textChanged.connect(self.titleChanged.emit)
        self.controls.title_le.textChanged.connect(self.plot.setTitle)
        self.controls.add_trace_btn.pressed.connect(self.on_add_trace_btn_pressed)
        self.controls.ang_var_cb.currentIndexChanged.connect(lambda _: self.on_angvar_changed())
        self.controls.r_var_cb.currentIndexChanged.connect(lambda _: self.on_rvar_changed())
        self.controls.min_sb.valueChanged.connect(self.plot.set_r_min)
        self.controls.max_sb.valueChanged.connect(self.plot.set_r_max)
        self.controls.step_sb.valueChanged.connect(self.plot.set_r_step)
        self.controls.autoscale_checkbox.toggled.connect(lambda state: self.on_autoscale_toggled(state))
        self.controls.theta_zero_ang_dsb.valueChanged.connect(self.plot.set_angle_zero_location)
        self.controls.bg_color_btn.sigColorChanged.connect(lambda btn: self.on_bg_color_changed(btn.color()))
        self.plot.rRangeUpdated.connect(self.controls.on_new_r_bounds)

    def postvisible_setup(self):
        self.on_angvar_changed()
        self.on_rvar_changed()

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

    def on_angvar_changed(self):
        ang_param = self.controls.ang_var_cb.currentData()
        for tr in self._traces:
            tr.ang_param = ang_param[0]

    def on_rvar_changed(self):
        r_param = self.controls.r_var_cb.currentData()
        for tr in self._traces:
            tr.r_func = r_param[0]

    def on_autoscale_toggled(self, state: bool):
        self.controls.min_label.setHidden(state)
        self.controls.min_sb.setHidden(state)
        self.controls.max_label.setHidden(state)
        self.controls.max_sb.setHidden(state)
        self.controls.step_label.setHidden(state)
        self.controls.step_sb.setHidden(state)
        self.plot.setAutoScale(state)
        if not state:
            r_min = self.controls.min_sb.value()
            r_max = self.controls.max_sb.value()
            r_step = self.controls.step_sb.value()
            self.plot.set_r_range(r_min, r_max, r_step)

    def on_remove_trace_btn_pressed(self, tr: PolarTraceSettings) -> None:
        LOG.debug("Removing trace")
        self.plot.removeTrace(tr.plot_item)
        self.controls.layout().removeWidget(tr)
        self._traces.remove(tr)
        tr.deleteLater()

        if len(self._traces) < 4:
            self.controls.add_trace_btn.show()

    def on_add_trace_btn_pressed(self) -> None:
        LOG.debug("Adding trace")
        plot_item = self.plot.plot()
        initial_ang_param = self.controls.ang_var_cb.currentData()[0]
        initial_r_func = self.controls.r_var_cb.currentData()[0]
        tr = PolarTraceSettings(plot_item, self.data, ang_param=initial_ang_param, r_func=initial_r_func, parent=self)
        tr.remove_polar_trace.pressed.connect(functools.partial(self.on_remove_trace_btn_pressed, tr))
        tr.requestRedraw.connect(self.plot.redrawItem)
        self._traces.append(tr)
        self.controls.layout().insertWidget(self.controls.layout().count() - 2, tr)

        if len(self._traces) >= 4:
            self.controls.add_trace_btn.hide()
