import pyqtgraph.opengl as gl
from PySide6.QtWidgets import QWidget

from ..ui.three_d_plot_settings import Ui_ThreeDPlotSettings


class ThreeDPlotSettings(QWidget, Ui_ThreeDPlotSettings):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.set_axis_type("cartesian")
        self.spherical_checkbox.toggled.connect(self.on_spherical_checkbox_toggled)

    def on_spherical_checkbox_toggled(self, state: bool) -> None:
        if state:
            self.set_axis_type("spherical")
        else:
            self.set_axis_type("cartesian")

    def set_axis_type(self, axis_type: str) -> None:
        self.x_var_label.setVisible(axis_type == "cartesian")
        self.x_var_cb.setVisible(axis_type == "cartesian")
        self.y_var_label.setVisible(axis_type == "cartesian")
        self.y_var_cb.setVisible(axis_type == "cartesian")
        self.z_var_label.setVisible(axis_type == "cartesian")
        self.z_var_cb.setVisible(axis_type == "cartesian")
        self.r_var_label.setVisible(axis_type == "spherical")
        self.r_var_cb.setVisible(axis_type == "spherical")

    def create_plot(self, parent: QWidget | None = None) -> gl.GLViewWidget:
        view = gl.GLViewWidget(parent=parent)
        xgrid = gl.GLGridItem()
        ygrid = gl.GLGridItem()
        zgrid = gl.GLGridItem()
        view.addItem(xgrid)
        view.addItem(ygrid)
        view.addItem(zgrid)
        return view
