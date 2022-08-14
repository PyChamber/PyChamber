from typing import Optional

from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from pychamber.logger import log
from pychamber.ui.ui import size_policy

from ..plugins.base import PyChamberPlugin
from .mpl_widget import Mpl3DWidget, MplPolarWidget, MplRectWidget


class PlotsWidget(PyChamberPlugin):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName('plots')
        self.setLayout(QVBoxLayout())
        self.setSizePolicy(size_policy["PREF_PREF"])
        self.setMinimumSize(600, 600)

    def setup(self) -> None:
        log.debug("Creating Plots widget...")
        self.tab_widget = QTabWidget(self)
        self.layout().addWidget(self.tab_widget)

        self.polar_plot_tab = QWidget(self.tab_widget)
        self.rect_plot_tab = QWidget(self.tab_widget)
        self.over_freq_plot_tab = QWidget(self.tab_widget)
        self.three_d_plot_tab = QWidget(self.tab_widget)

        self.tab_widget.addTab(self.polar_plot_tab, "Polar Plot")
        self.tab_widget.addTab(self.rect_plot_tab, "Rectangular Plot")
        self.tab_widget.addTab(self.over_freq_plot_tab, "Over Frequency Plot")
        self.tab_widget.addTab(self.three_d_plot_tab, "3D Plot")

        self._setup_polar_plot_tab()
        self._setup_rect_plot_tab()
        self._setup_over_freq_plot_tab()
        self._setup_3d_plot_tab()

    def _setup_polar_plot_tab(self) -> None:
        tab = self.polar_plot_tab
        layout = QVBoxLayout(tab)

        hlayout = QHBoxLayout()

        pol_label = QLabel("Polarization", tab)
        hlayout.addWidget(pol_label)

        self.polar_pol_combobox = QComboBox(tab)
        self.polar_pol_combobox.addItems(['1', '2'])
        hlayout.addWidget(self.polar_pol_combobox)

        polar_freq_labl = QLabel("Frequency", tab)
        hlayout.addWidget(polar_freq_labl)

        self.polar_freq_lineedit = QLineEdit(tab)
        self.polar_freq_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.polar_freq_lineedit.setMinimumWidth(100)
        hlayout.addWidget(self.polar_freq_lineedit)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        polar_min_label = QLabel("Min", tab)
        hlayout.addWidget(polar_min_label)

        self.polar_min_spinbox = QSpinBox(tab)
        self.polar_min_spinbox.setRange(-100, 100)
        self.polar_min_spinbox.setSingleStep(5)
        hlayout.addWidget(self.polar_min_spinbox)

        polar_max_label = QLabel("Max", tab)
        hlayout.addWidget(polar_max_label)

        self.polar_max_spinbox = QSpinBox(tab)
        self.polar_max_spinbox.setRange(-100, 100)
        self.polar_max_spinbox.setSingleStep(5)
        hlayout.addWidget(self.polar_max_spinbox)

        polar_step_label = QLabel("dB/div", tab)
        hlayout.addWidget(polar_step_label)

        self.polar_step_spinbox = QSpinBox(tab)
        self.polar_step_spinbox.setRange(1, 100)
        self.polar_step_spinbox.setSingleStep(10)
        hlayout.addWidget(self.polar_step_spinbox)

        self.polar_autoscale_btn = QPushButton("Auto Scale", tab)
        hlayout.addWidget(self.polar_autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.polar_plot = MplPolarWidget('tab:blue', tab)
        layout.addWidget(self.polar_plot)

    def _setup_rect_plot_tab(self) -> None:
        tab = self.rect_plot_tab
        layout = QVBoxLayout(tab)

        hlayout = QHBoxLayout()

        rect_pol_label = QLabel("Polarization", tab)
        hlayout.addWidget(rect_pol_label)

        self.rect_pol_combobox = QComboBox(tab)
        self.rect_pol_combobox.addItems(['1', '2'])
        hlayout.addWidget(self.rect_pol_combobox)

        rect_freq_label = QLabel("Frequency", tab)
        hlayout.addWidget(rect_freq_label)

        self.rect_freq_lineedit = QLineEdit(tab)
        self.rect_freq_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.rect_freq_lineedit.setMinimumWidth(100)
        hlayout.addWidget(self.rect_freq_lineedit)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()

        rect_min_label = QLabel("Min", tab)
        hlayout.addWidget(rect_min_label)

        self.rect_min_spinbox = QSpinBox(tab)
        self.rect_min_spinbox.setRange(-100, 100)
        self.rect_min_spinbox.setSingleStep(5)
        hlayout.addWidget(self.rect_min_spinbox)

        rect_max_label = QLabel("Max", tab)
        hlayout.addWidget(rect_max_label)

        self.rect_max_spinbox = QSpinBox(tab)
        self.rect_max_spinbox.setRange(-100, 100)
        self.rect_max_spinbox.setSingleStep(5)
        hlayout.addWidget(self.rect_max_spinbox)

        rect_step_label = QLabel("dB/div", tab)
        hlayout.addWidget(rect_step_label)

        self.rect_step_spinbox = QSpinBox(tab)
        self.rect_step_spinbox.setRange(1, 100)
        self.rect_step_spinbox.setSingleStep(10)
        hlayout.addWidget(self.rect_step_spinbox)

        self.rect_autoscale_btn = QPushButton("Auto Scale", tab)
        hlayout.addWidget(self.rect_autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.rect_plot = MplRectWidget('tab:blue', tab)
        layout.addWidget(self.rect_plot)

    def _setup_over_freq_plot_tab(self) -> None:
        tab = self.over_freq_plot_tab
        layout = QVBoxLayout(tab)

        hlayout = QHBoxLayout()

        over_freq_pol_label = QLabel("Polarization", tab)
        hlayout.addWidget(over_freq_pol_label)

        self.over_freq_pol_combobox = QComboBox(tab)
        self.over_freq_pol_combobox.addItems(['1', '2'])
        hlayout.addWidget(self.over_freq_pol_combobox)

        over_freq_az_label = QLabel("Azimuth", tab)
        hlayout.addWidget(over_freq_az_label)

        self.over_freq_az_spinbox = QDoubleSpinBox(tab)
        hlayout.addWidget(self.over_freq_az_spinbox)

        over_freq_el_label = QLabel("Elevation", tab)
        hlayout.addWidget(over_freq_el_label)

        self.over_freq_el_spinbox = QDoubleSpinBox(tab)
        hlayout.addWidget(self.over_freq_el_spinbox)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        over_freq_min_label = QLabel("Min", tab)
        hlayout.addWidget(over_freq_min_label)

        self.over_freq_min_spinbox = QSpinBox(tab)
        self.over_freq_min_spinbox.setRange(-100, 100)
        self.over_freq_min_spinbox.setSingleStep(5)
        hlayout.addWidget(self.over_freq_min_spinbox)

        over_freq_max_label = QLabel("Max", tab)
        hlayout.addWidget(over_freq_max_label)

        self.over_freq_max_spinbox = QSpinBox(tab)
        self.over_freq_max_spinbox.setRange(-100, 100)
        self.over_freq_max_spinbox.setSingleStep(5)
        hlayout.addWidget(self.over_freq_max_spinbox)

        over_freq_step_label = QLabel("dB/div", tab)
        hlayout.addWidget(over_freq_step_label)

        self.over_freq_step_spinbox = QSpinBox(tab)
        self.over_freq_step_spinbox.setRange(1, 100)
        self.over_freq_step_spinbox.setSingleStep(10)
        hlayout.addWidget(self.over_freq_step_spinbox)

        self.over_freq_autoscale_btn = QPushButton("Auto Scale", tab)
        hlayout.addWidget(self.over_freq_autoscale_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.over_freq_plot = MplRectWidget('tab:blue', tab)
        layout.addWidget(self.over_freq_plot)

    def _setup_3d_plot_tab(self) -> None:
        tab = self.three_d_plot_tab
        layout = QVBoxLayout(tab)

        hlayout = QHBoxLayout()
        self.three_d_pol_label = QLabel("Polarization", tab)
        hlayout.addWidget(self.three_d_pol_label)

        self.three_d_pol_combobox = QComboBox(tab)
        self.three_d_pol_combobox.addItems(['1', '2'])
        hlayout.addWidget(self.three_d_pol_combobox)

        self.three_d_freq_label = QLabel("Frequency", tab)
        hlayout.addWidget(self.three_d_freq_label)

        self.three_d_freq_lineedit = QLineEdit(tab)
        self.three_d_freq_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.three_d_freq_lineedit.setMinimumWidth(100)
        hlayout.addWidget(self.three_d_freq_lineedit)

        self.three_d_refresh_btn = QPushButton("Refresh Plot", tab)
        hlayout.addWidget(self.three_d_refresh_btn)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)

        layout.addLayout(hlayout)

        self.three_d_plot = Mpl3DWidget(tab)
        layout.addWidget(self.three_d_plot)
