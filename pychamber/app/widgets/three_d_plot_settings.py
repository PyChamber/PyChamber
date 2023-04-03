from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from pychamber import ExperimentResult

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QWidget
from skrf import mathFunctions

from pychamber.app.task_runner import TaskRunner

from ..ui.three_d_plot_settings import Ui_ThreeDPlotSettings
from .plot_widget import PlotWidget


class ThreeDPlotSettings(QWidget, Ui_ThreeDPlotSettings):
    z_params = [
        ("Magnitude [linear]", mathFunctions.complex_2_magnitude),
        ("Magnitude [dB]", lambda data: mathFunctions.complex_2_db(np.where(data == 0, 1e-20, data))),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.connect_signals()
        self.postvisible_setup()

    def connect_signals(self):
        self.spherical_checkbox.toggled.connect(self.on_spherical_checkbox_toggled)

    def postvisible_setup(self):
        self.on_spherical_checkbox_toggled(False)
        list_of_maps = pg.colormap.listMaps()
        list_of_maps = sorted(list_of_maps, key=lambda x: x.swapcase())
        self.cmap_cb.clear()
        self.cmap_cb.addItems(list_of_maps)
        for title, var_info in self.z_params:
            self.r_var_cb.addItem(title, userData=var_info)
            self.z_var_cb.addItem(title, userData=var_info)

    def on_spherical_checkbox_toggled(self, state: bool) -> None:
        cart_ctrls = (self.z_var_label, self.z_var_cb)
        sph_ctrls = (self.r_var_label, self.r_var_cb)

        for widget in cart_ctrls:
            widget.setHidden(state)
        for widget in sph_ctrls:
            widget.setVisible(state)

    @property
    def cmap(self):
        return pg.colormap.get(self.cmap_cb.currentText())


class ThreeDPlotWidget(PlotWidget):
    phi_spacing = 30
    theta_spacing = 30

    def __init__(self, data: ExperimentResult, parent: QWidget | None = None) -> None:
        plot = gl.GLViewWidget()
        self.gz = gl.GLGridItem()
        self.gz.setSize(180, 360, 1)
        self.gz.setSpacing(self.phi_spacing, self.theta_spacing, 1)
        plot.addItem(self.gz)
        plot.setCameraPosition(distance=300)

        self.cartesian_plot = gl.GLSurfacePlotItem(computeNormals=False)
        self.spherical_plot = gl.GLVolumeItem(np.zeros((1, 1, 1, 1)))
        plot.addItem(self.cartesian_plot)
        plot.addItem(self.spherical_plot)
        self.spherical_plot.hide()

        controls = ThreeDPlotSettings()

        super().__init__(plot=plot, controls=controls, data=data, parent=parent)

        self.connect_signals()

    def connect_signals(self):
        self.controls.spherical_checkbox.toggled.connect(self.on_spherical_checkbox_toggled)
        self.controls.bg_color_btn.sigColorChanged.connect(lambda btn: self.on_bg_color_changed(btn.color()))
        self.controls.z_var_cb.currentIndexChanged.connect(lambda _: self.on_new_data())
        self.controls.r_var_cb.currentIndexChanged.connect(lambda _: self.on_new_data())
        self.controls.cmap_cb.currentTextChanged.connect(lambda _: self.on_new_data())
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)

    def postvisible_setup(self):
        pass

    @property
    def data(self) -> ExperimentResult | None:
        return self._data

    @data.setter
    def data(self, result: ExperimentResult):
        self._data = result
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)
        self.on_new_data()

    def on_spherical_checkbox_toggled(self, state: bool):
        if state:
            self.gz.hide()
            self.cartesian_plot.hide()
            self.spherical_plot.show()
        else:
            self.gz.show()
            self.cartesian_plot.show()
            self.spherical_plot.hide()

    def on_bg_color_changed(self, color):
        self.plot.setBackgroundColor(color)

    @staticmethod
    def get_data(data: ExperimentResult, z_func: Callable, pol: str, f: float):
        if f is None or pol == "":
            return None

        data.rw_lock.lockForRead()
        x_data = data.phis
        y_data = data.thetas
        vals = data.get_2d_cut(pol, f)
        data.rw_lock.unlock()

        z_data = z_func(vals)

        return (x_data, y_data, z_data)

    def on_new_data(self):
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

        data_grabber = TaskRunner(
            self.get_data,
            data=self.data,
            z_func=z_func,
            pol=pol,
            f=freq,
        )
        data_grabber.signals.gotResult.connect(self.on_get_data_result)
        data_grabber.signals.error.connect(lambda e: print(f"{e[0]} {e[1]} {e[2]}"))
        QThreadPool.globalInstance().start(data_grabber)

    def on_get_data_result(self, result: tuple[np.ndarray, np.ndarray, np.ndarray] | None):
        # TODO: ability to turn off autoscaling
        if result is None:
            return

        x = result[0]
        y = result[1]
        z = result[2] - np.amin(result[2])

        self.z_min = np.amin(z)
        self.z_max = np.amax(z)
        z_range = np.abs(self.z_max - self.z_min)
        scale = 100 / z_range
        z_cmapped = (z - (self.z_min)) / z_range
        colors = self.controls.cmap.map(z_cmapped, mode="float")

        self.gz.resetTransform()
        self.gz.translate(0, 0, -self.z_min)

        self.cartesian_plot.resetTransform()
        self.cartesian_plot.scale(1, 1, scale)
        self.cartesian_plot.translate(0, 0, -self.z_min)

        self.cartesian_plot.setData(x, y, z, colors=colors)
