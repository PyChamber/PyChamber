from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from pychamber import ExperimentResult

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from qtpy.QtCore import QPointF, QThreadPool
from qtpy.QtWidgets import QWidget
from skrf import mathFunctions

from pychamber import math_fns
from pychamber.app.logger import LOG
from pychamber.app.task_runner import TaskRunner
from pychamber.settings import CONF

from ..ui.three_d_plot_settings import Ui_ThreeDPlotSettings
from .plot_widget import PlotWidget
from .spherical_grid import GLSphericalGridItem


class ThreeDPlotSettings(QWidget, Ui_ThreeDPlotSettings):
    r_params = [
        ("Magnitude [linear]", mathFunctions.complex_2_magnitude),
        ("Magnitude [dB]", math_fns.clean_complex_to_db),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.postvisible_setup()

    def postvisible_setup(self):
        list_of_maps = pg.colormap.listMaps()
        list_of_maps = sorted(list_of_maps, key=lambda x: x.swapcase())
        self.cmap_cb.clear()
        self.cmap_cb.addItems(list_of_maps)
        for title, var_info in self.r_params:
            self.r_var_cb.addItem(title, userData=var_info)

    @property
    def cmap(self):
        return pg.colormap.get(self.cmap_cb.currentText())


class ThreeDPlotWidget(PlotWidget):
    phi_spacing = 30
    theta_spacing = 30

    def __init__(self, data: ExperimentResult, title: str, parent: QWidget | None = None) -> None:
        plot = gl.GLViewWidget()
        plot.mousePos = QPointF(0, 0)  # Avoids some bug about not having a pressPos attr
        plot.setCameraPosition(distance=300)

        self.sph_grid = GLSphericalGridItem(100)
        plot.addItem(self.sph_grid)
        self.sph_grid.hide()

        self.cartesian_plot = gl.GLSurfacePlotItem(computeNormals=False)
        self.spherical_plot = gl.GLMeshItem()
        plot.addItem(self.cartesian_plot)
        plot.addItem(self.spherical_plot)
        self.spherical_plot.hide()

        controls = ThreeDPlotSettings()

        LOG.debug("Creating contour plot widget")
        super().__init__(plot=plot, controls=controls, data=data, title=title, parent=parent)

        self.legend_item = gl.GLGradientLegendItem(pos=(10, 10), size=(50, 300), gradient=controls.cmap)
        plot.addItem(self.legend_item)

        self.r_min = 0
        self.r_max = 1
        self.theta_grid = None
        self.phi_grid = None

        self.connect_signals()
        self.set_colors()
        self.on_new_data()

    def connect_signals(self):
        LOG.debug("Connecting signals")
        self.controls.title_le.textChanged.connect(self.titleChanged.emit)
        self.controls.spherical_checkbox.toggled.connect(self.on_spherical_checkbox_toggled)
        self.controls.bg_color_btn.sigColorChanged.connect(lambda btn: self.on_bg_color_changed(btn.color()))
        self.controls.r_var_cb.currentIndexChanged.connect(lambda _: self.on_new_data())
        self.controls.min_sb.valueChanged.connect(lambda _: self.on_range_changed())
        self.controls.max_sb.valueChanged.connect(lambda _: self.on_range_changed())
        self.controls.cmap_cb.currentTextChanged.connect(lambda _: self.on_new_data())
        self.controls.cmap_cb.currentTextChanged.connect(
            lambda _: self.legend_item.setData(gradient=self.controls.cmap)
        )
        self.controls.calibrated_checkbox.toggled.connect(lambda _: self.on_new_data())
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)

    def set_colors(self):
        if CONF["theme"] == "Light":
            self.sph_grid.setColors(
                phi_color="#8FBCBBFF",
                theta_color="#B48EADFF",
            )
        else:
            self.sph_grid.setColors(
                phi_color="#73DACAFF",
                theta_color="#BB9AF7FF",
            )

    @property
    def data(self) -> ExperimentResult | None:
        return self._data

    @data.setter
    def data(self, result: ExperimentResult):
        LOG.debug("Setting data")
        self._data = result
        if self.data is not None:
            self.data.dataAppended.connect(self.on_new_data)
            self.init_spherical_plot()
        self.on_new_data()

    def on_spherical_checkbox_toggled(self, state: bool):
        if state:
            LOG.debug("Switching to spherical mode")
            self.sph_grid.show()
            self.cartesian_plot.hide()
            self.spherical_plot.show()
        else:
            LOG.debug("Switching to rectangular mode")
            self.sph_grid.hide()
            self.cartesian_plot.show()
            self.spherical_plot.hide()

    def on_bg_color_changed(self, color):
        self.plot.setBackgroundColor(color)

    def on_range_changed(self):
        self.r_min = self.controls.min_sb.value()
        self.r_max = self.controls.max_sb.value()
        self.on_new_data()

    def init_spherical_plot(self):
        LOG.debug("Initializing spherical plot")
        if self.data is None:
            return

        self.phi = self.data.phis
        self.theta = self.data.thetas
        self.theta_grid, self.phi_grid = np.meshgrid(np.deg2rad(self.theta), np.deg2rad(self.phi))

        # From pyqtgraph.opengl.MeshData.sphere
        rows = len(self.phi) - 1
        cols = len(self.theta)
        faces = np.empty((rows * cols * 2, 3), dtype=np.uint)
        rowtemplate1 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 0]])) % cols) + np.array([[0, 0, cols]])
        rowtemplate2 = ((np.arange(cols).reshape(cols, 1) + np.array([[0, 1, 1]])) % cols) + np.array([[cols, 0, cols]])
        for row in range(rows):
            start = row * cols * 2
            faces[start : start + cols] = rowtemplate1 + row * cols
            faces[start + cols : start + (cols * 2)] = rowtemplate2 + row * cols
        self.faces = faces

    @staticmethod
    def get_data(
        data: ExperimentResult,
        r_func: Callable,
        pol: str,
        f: float,
        calibrated: bool
    ):
        if f is None or pol == "":
            return None

        data.rw_lock.lockForRead()
        vals = data.get_3d_data(pol, f, calibrated=calibrated)
        data.rw_lock.unlock()

        r_data = r_func(vals)

        return r_data

    def on_new_data(self):
        LOG.debug("Got new data")
        if self.data is None:
            return
        if len(self.data) == 0:
            return

        if self.theta_grid is None or self.phi_grid is None:
            self.init_spherical_plot()

        current_pols_list = [self.controls.pol_cb.itemText(i) for i in range(self.controls.pol_cb.count())]
        if set(current_pols_list) != set(self.data.polarizations):
            self.controls.pol_cb.clear()
            self.controls.pol_cb.addItems(self.data.polarizations)

        r_func = self.controls.r_var_cb.currentData()
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
            r_func=r_func,
            pol=pol,
            f=freq,
            calibrated=calibrated
        )
        data_grabber.signals.gotResult.connect(self.on_get_data_result)
        data_grabber.signals.error.connect(lambda e: print(f"{e[0]} {e[1]} {e[2]}"))
        QThreadPool.globalInstance().start(data_grabber)

    def on_get_data_result(self, result: np.ndarray | None):
        LOG.debug("Retrived data. Updating plot")
        if result is None:
            return

        r = result

        r = np.clip(r, self.r_min, self.r_max)
        r_mapped = r + np.abs(self.r_min)
        r_range = np.abs(self.r_max - self.r_min)
        r_cmapped = (r - (self.r_min)) / r_range
        colors = self.controls.cmap.map(r_cmapped, mode="float")

        label_min = round(self.r_min if self.r_min < self.r_max else self.r_max)
        label_max = round(self.r_max if self.r_max > self.r_min else self.r_min)
        legend_labels = np.linspace(label_min, label_max, 5)
        legend_pos = np.linspace(0, 1, 5)
        legend = dict(zip(map(str, legend_labels), legend_pos, strict=True))

        self.legend_item.setData(labels=legend)

        self.update_cartesian_plot(self.phi, self.theta, r_mapped, colors)
        self.update_spherical_plot(r_mapped, self.theta_grid, self.phi_grid, colors)

    def update_cartesian_plot(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, colors: np.ndarray):
        LOG.debug("Updating cartesian plot")
        r_range = np.abs(self.r_max - self.r_min)
        r_scale = 100 / r_range

        self.cartesian_plot.resetTransform()
        self.cartesian_plot.scale(1, 1, r_scale)
        self.cartesian_plot.translate(0, 0, -self.r_min)

        self.cartesian_plot.setData(x, y, z, colors=colors)

    def update_spherical_plot(self, r: np.ndarray, theta: np.ndarray, phi: np.ndarray, colors: np.ndarray):
        LOG.debug("Updating spherical plot")
        x, y, z = math_fns.spherical_to_cartesian(r, theta, phi)
        xyz = np.dstack((x.ravel(), y.ravel(), z.ravel())).squeeze()

        r_range = np.abs(self.r_max - self.r_min)
        r_scale = 100 / r_range

        verts = xyz * r_scale
        md = gl.MeshData(vertexes=verts, faces=self.faces, faceColors=colors.reshape(-1, 4))
        self.spherical_plot.setMeshData(meshdata=md)
