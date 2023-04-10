from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from pychamber import ExperimentResult

import numpy as np
import pyqtgraph as pg
from qtpy.QtCore import QThreadPool
from qtpy.QtWidgets import QWidget
from skrf import mathFunctions

from pychamber import math_fns
from pychamber.app.logger import LOG
from pychamber.app.task_runner import TaskRunner

from ..ui.contour_plot_settings import Ui_ContourPlotSettings
from .contour_plot import ContourPlot
from .plot_widget import PlotWidget


class ContourPlotSettings(QWidget, Ui_ContourPlotSettings):
    z_params = [
        ("Magnitude [linear]", mathFunctions.complex_2_magnitude),
        ("Magnitude [dB]", math_fns.clean_complex_to_db),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        LOG.debug("Creating contour plot settings")
        self.setupUi(self)

        self.connect_signals()
        self.postvisible_setup()

    def connect_signals(self):
        self.autoscale_checkbox.toggled.connect(lambda state: self.min_sb.setDisabled(state))
        self.autoscale_checkbox.toggled.connect(lambda state: self.max_sb.setDisabled(state))

    def postvisible_setup(self) -> None:
        list_of_maps = pg.colormap.listMaps()
        list_of_maps = sorted(list_of_maps, key=lambda x: x.swapcase())
        self.cmap_cb.clear()
        self.cmap_cb.addItems(list_of_maps)
        for title, var_info in self.z_params:
            self.z_var_cb.addItem(title, userData=var_info)

    def on_new_z_bounds(self, z_min, z_max):
        to_block = [self.min_sb, self.max_sb]
        for widget in to_block:
            widget.blockSignals(True)

        self.min_sb.setValue(z_min)
        self.max_sb.setValue(z_max)

        for widget in to_block:
            widget.blockSignals(False)

    @property
    def cmap(self) -> str:
        return self.cmap_cb.currentText()


class ContourPlotWidget(PlotWidget):
    def __init__(self, data: ExperimentResult, title: str, parent: QWidget | None = None) -> None:
        controls = ContourPlotSettings()
        plot = ContourPlot(cmap=controls.cmap_cb.currentText(), draw_isos=controls.isolines_checkbox.isChecked())
        super().__init__(plot=plot, controls=controls, data=data, title=title, parent=parent)
        LOG.debug("Creating contour plot widget")
        self.plot.setTitle(title)

        self.connect_signals()
        self.postvisible_setup()

    def connect_signals(self) -> None:
        self.controls.title_le.textChanged.connect(self.titleChanged.emit)
        self.controls.title_le.textChanged.connect(self.plot.setTitle)
        self.controls.min_sb.valueChanged.connect(self.plot.setZMin)
        self.controls.max_sb.valueChanged.connect(self.plot.setZMax)
        self.controls.autoscale_checkbox.toggled.connect(lambda state: self.plot.setAutoScale(state))
        self.controls.isolines_checkbox.toggled.connect(lambda state: self.plot.setDrawIsolines(state))
        self.controls.bg_color_btn.sigColorChanged.connect(lambda btn: self.on_bg_color_changed(btn.color()))
        self.controls.z_var_cb.currentIndexChanged.connect(lambda _: self.on_new_data())
        self.controls.cmap_cb.currentTextChanged.connect(self.plot.setCmap)
        self.controls.calibrated_checkbox.toggled.connect(lambda _: self.on_new_data())
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)

        self.plot.newZBounds.connect(self.controls.on_new_z_bounds)

    def postvisible_setup(self):
        self.plot.setXLabel("Azimuth (Phi)", "°")
        self.plot.setYLabel("Elevation (Theta)", "°")
        self.on_new_data()

    @property
    def data(self) -> ExperimentResult | None:
        return self._data

    @data.setter
    def data(self, result: ExperimentResult):
        LOG.debug("Setting data")
        self._data = result
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)
        self.on_new_data()

    def on_bg_color_changed(self, color):
        self.plot.setBackground(color)

    @staticmethod
    def get_data(
        data: ExperimentResult,
        z_func: Callable,
        pol: str,
        f: float,
        calibrated: bool
    ):
        if f is None or pol == "":
            return None

        data.rw_lock.lockForRead()
        x_data = data.phis
        y_data = data.thetas
        vals = data.get_3d_data(pol, f, calibrated=calibrated)
        data.rw_lock.unlock()

        z_data = z_func(vals)

        return (x_data, y_data, z_data)

    def on_new_data(self):
        LOG.debug("Got new data")
        if self.data is None:
            return
        if len(self.data) == 0:
            return

        current_pols_list = [self.controls.pol_cb.itemText(i) for i in range(self.controls.pol_cb.count())]
        if set(current_pols_list) != set(self.data.polarizations):
            self.controls.pol_cb.clear()
            self.controls.pol_cb.addItems(self.data.polarizations)

        z_func = self.controls.z_var_cb.currentData()
        pol = self.controls.pol_cb.currentText()
        freq = self.controls.freq_le.value()
        if freq is None:
            self.controls.freq_le.setText(self.data.f[0])
            freq = self.controls.freq_le.value()
        calibrated = self.controls.calibrated_checkbox.isChecked()
        self.controls.calibrated_checkbox.setVisible(self.data.has_calibrated_data)
        if not self.data.has_calibrated_data:
            calibrated = False

        data_grabber = TaskRunner(
            self.get_data,
            data=self.data,
            z_func=z_func,
            pol=pol,
            f=freq,
            calibrated=calibrated
        )
        data_grabber.signals.gotResult.connect(self.on_get_data_result)
        QThreadPool.globalInstance().start(data_grabber)

    def on_get_data_result(self, result: tuple[np.ndarray, np.ndarray, np.ndarray] | None):
        LOG.debug("Extracted result. Setting plot data")
        if result is None:
            return

        self.plot.setData(result[0], result[1], result[2])
