"""Defines the PositionerPlugin."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from pychamber.main_window import MainWindow

import functools

import numpy as np
import qtawesome as qta
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from serial.tools import list_ports

from pychamber.logger import LOG
from pychamber.plugins import PyChamberPanelPlugin
from pychamber.settings import SETTINGS
from pychamber.ui import font, size_policy
from pychamber.widgets import CollapsibleSection

from .positioner import JogAxis, JogDir, Positioner


class PositionerPlugin(PyChamberPanelPlugin):
    """The Positioner plugin.

    Attributes:
        positioner_connected: Signal raised when a positioner is successfully
            connected
        jog_started: Signal raised to announce the start of a jog movement
        jog_complete: Signal raised to announce a jog movement has completed
    """

    NAME = "positioner"
    CONFIG = {
        "model": "",
        "port": "",
        "az-pos": 0.0,
        "el-pos": 0.0,
        "az-start": -90,
        "az-stop": 90,
        "az-step": 5,
        "el-start": -90,
        "el-stop": 90,
        "el-step": 5,
        "jog-az-step": 0.0,
        "jog-el-step": 0.0,
    }

    # Signals
    positioner_connected = pyqtSignal()
    jog_started = pyqtSignal()
    jog_complete = pyqtSignal()

    def __init__(self, main_window: MainWindow) -> None:
        """Instantiate the plugin.

        Arguments:
            parent: the PyChamber main window
        """
        assert self.NAME is not None
        PyChamberPanelPlugin.__init__(self, main_window=main_window)
        self.section = CollapsibleSection(title=self.NAME.capitalize(), parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.section)
        self.setLayout(layout)

        self.setObjectName('positioner')

        self._positioner: Optional[Positioner] = None

        self.jog_az_to: float = 0.0
        self.jog_el_to: float = 0.0

        self.jog_thread: QThread = QThread(None)
        self.jog_thread.started.connect(self.jog_started.emit)

        self.listen_to_jog_complete_signals = True  # FIXME: This is gross

    def _setup(self) -> None:
        LOG.debug("Creating Positioner widget...")
        self._add_widgets()

    def _post_visible_setup(self) -> None:
        LOG.debug("Post-visible setup...")
        self._init_inputs()
        self._connect_signals()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensures jog threads are closed and stores current position."""
        if self._positioner is not None:
            SETTINGS["polarization/az-pos"] = self._positioner.current_azimuth
            SETTINGS["polarization/el-pos"] = self._positioner.current_elevation
        self.jog_thread.quit()
        self.jog_thread.wait()
        super().closeEvent(event)

    def _add_widgets(self) -> None:
        self._layout = QVBoxLayout()

        hlayout = QHBoxLayout()

        model_label = QLabel("Model", self.section)
        hlayout.addWidget(model_label)

        self.model_combobox = QComboBox(self.section)
        hlayout.addWidget(self.model_combobox)

        port_label = QLabel("Port", self.section)
        hlayout.addWidget(port_label)

        self.port_combobox = QComboBox(self.section)
        hlayout.addWidget(self.port_combobox)

        self.connect_btn = QPushButton("Connect", self.section)
        self.connect_btn.setSizePolicy(size_policy["PREF_PREF"])
        hlayout.addWidget(self.connect_btn)

        self._layout.addLayout(hlayout)

        self.extents_groupbox = QGroupBox(self.section)
        self.extents_layout = QHBoxLayout(self.extents_groupbox)
        self._setup_az_extent_widget()
        self._setup_el_extent_widget()
        self._layout.addWidget(self.extents_groupbox)

        self.jog_groupbox = QGroupBox(self.section)
        self.jog_layout = QVBoxLayout(self.jog_groupbox)
        self._setup_jog_box()
        self._layout.addWidget(self.jog_groupbox)

        self.section.set_content_layout(self._layout)

    def _init_inputs(self) -> None:
        LOG.debug("Populating models...")
        self.model_combobox.clear()
        self.model_combobox.addItems(Positioner.model_names())

        LOG.debug("Populating addrs...")
        self.port_combobox.clear()
        ports = [p.device for p in list_ports.comports()]
        self.port_combobox.addItems(ports)

        LOG.debug("Updating inputs from settings...")
        self.model_combobox.setCurrentText(SETTINGS['positioner/model'])
        self.port_combobox.setCurrentText(SETTINGS['positioner/port'])
        self.az_start_spinbox.setValue(float(SETTINGS["positioner/az-start"]))
        self.az_stop_spinbox.setValue(float(SETTINGS["positioner/az-stop"]))
        self.az_step_spinbox.setValue(float(SETTINGS["positioner/az-step"]))
        self.el_start_spinbox.setValue(float(SETTINGS["positioner/el-start"]))
        self.el_stop_spinbox.setValue(float(SETTINGS["positioner/el-stop"]))
        self.el_step_spinbox.setValue(float(SETTINGS["positioner/el-step"]))

    def _connect_signals(self) -> None:
        self.model_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("positioner/model", text)
        )
        self.port_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("positioner/port", text)
        )
        self.connect_btn.clicked.connect(self._on_connect_clicked)

        self.az_start_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/az-start", val)
        )
        self.az_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/az-step", val)
        )
        self.az_stop_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/az-stop", val)
        )

        self.el_start_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/el-start", val)
        )
        self.el_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/el-step", val)
        )
        self.el_stop_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/el-stop", val)
        )

        self.jog_az_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/jog-az-step", val)
        )
        self.jog_el_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("positioner/jog-el-step", val)
        )

        self.jog_az_to_lineedit.editingFinished.connect(self._on_jog_az_to_changed)
        self.jog_el_to_lineedit.editingFinished.connect(self._on_jog_el_to_changed)

        self.jog_az_left_btn.clicked.connect(
            functools.partial(
                self._jog, axis=JogAxis.AZIMUTH, direction=JogDir.MINUS, relative=True
            )
        )
        self.jog_az_zero_btn.clicked.connect(
            functools.partial(
                self._jog, axis=JogAxis.AZIMUTH, direction=JogDir.ZERO, relative=False
            )
        )
        self.jog_az_right_btn.clicked.connect(
            functools.partial(
                self._jog, axis=JogAxis.AZIMUTH, direction=JogDir.PLUS, relative=True
            )
        )
        self.jog_el_ccw_btn.clicked.connect(
            functools.partial(
                self._jog, axis=JogAxis.ELEVATION, direction=JogDir.MINUS, relative=True
            )
        )
        self.jog_el_zero_btn.clicked.connect(
            functools.partial(
                self._jog, axis=JogAxis.ELEVATION, direction=JogDir.ZERO, relative=False
            )
        )
        self.jog_el_cw_btn.clicked.connect(
            functools.partial(
                self._jog, axis=JogAxis.ELEVATION, direction=JogDir.PLUS, relative=True
            )
        )
        self.ret_to_zero_btn.clicked.connect(self._on_ret_to_zero_clicked)

        self.set_zero_btn.clicked.connect(self._on_set_zero_clicked)
        self.positioner_connected.connect(self._on_positioner_connected)

        self.jog_started.connect(lambda: self.main.statusBar().showMessage("Jogging..."))
        self.jog_complete.connect(self._on_jog_complete)
        self.jog_complete.connect(
            lambda: self.main.statusBar().showMessage("Jog complete", 500)
        )

    def _on_jog_az_to_changed(self) -> None:
        val = self.jog_az_to_lineedit.text()
        self.jog_az_to = float(val)

    def _on_jog_el_to_changed(self) -> None:
        val = self.jog_el_to_lineedit.text()
        self.jog_el_to = float(val)

    def _on_connect_clicked(self) -> None:
        model = self.model_combobox.currentText()
        port = self.port_combobox.currentText()

        self.connect(model, port)

    def _on_set_zero_clicked(self) -> None:
        if not self._positioner:
            QMessageBox.warning(self, "Connection Error", "Positioner not connected")
            return

        # TODO: Should we just make positioner emit a signal when the position changes
        self._positioner.zero()
        self.az_pos_lineedit.setText("0.0")
        self.el_pos_lineedit.setText("0.0")

    def _on_ret_to_zero_clicked(self) -> None:
        move_spy = QSignalSpy(self.jog_complete)
        self._jog(axis=JogAxis.ELEVATION, direction=JogDir.ZERO, relative=False)
        move_spy.wait()
        self._jog(axis=JogAxis.AZIMUTH, direction=JogDir.ZERO, relative=False)

    def _on_az_move_complete(self) -> None:
        assert self._positioner is not None
        SETTINGS["positioner/az-pos"] = self._positioner.current_azimuth
        self.az_pos_lineedit.setText(str(SETTINGS["positioner/az-pos"]))
        self.jog_complete.emit()

    def _on_el_move_complete(self) -> None:
        assert self._positioner is not None
        SETTINGS["positioner/el-pos"] = self._positioner.current_elevation
        self.el_pos_lineedit.setText(str(SETTINGS["positioner/el-pos"]))
        self.jog_complete.emit()

    def _on_positioner_connected(self) -> None:
        assert self._positioner is not None
        self.set_enabled(True)
        self.az_pos_lineedit.setText(str(SETTINGS["positioner/az-pos"]))
        self.el_pos_lineedit.setText(str(SETTINGS["positioner/el-pos"]))
        self._positioner.az_move_complete.connect(self._on_az_move_complete)
        self._positioner.el_move_complete.connect(self._on_el_move_complete)

    def _on_jog_complete(self) -> None:
        LOG.debug("Jog complete")
        self.set_enabled(True and self.listen_to_jog_complete_signals)

    def _setup_az_extent_widget(self) -> None:
        layout = QVBoxLayout()

        az_extent_label = QLabel("Azimuth", self.extents_groupbox)
        az_extent_label.setFont(font["BOLD_14"])
        az_extent_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(az_extent_label)

        hlayout = QHBoxLayout()
        az_start_label = QLabel("Start", self.extents_groupbox)
        hlayout.addWidget(az_start_label)
        self.az_start_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.az_start_spinbox.setRange(-180.0, 180.0)
        self.az_start_spinbox.setSingleStep(1.0)
        self.az_start_spinbox.setDecimals(2)
        hlayout.addWidget(self.az_start_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        az_stop_label = QLabel("Stop", self.extents_groupbox)
        self.az_stop_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.az_stop_spinbox.setRange(-180.0, 180.0)
        self.az_stop_spinbox.setSingleStep(1.0)
        self.az_stop_spinbox.setDecimals(2)
        hlayout.addWidget(az_stop_label)
        hlayout.addWidget(self.az_stop_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        az_step_label = QLabel("Step", self.extents_groupbox)
        self.az_step_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.az_step_spinbox.setRange(-180.0, 180.0)
        self.az_step_spinbox.setSingleStep(1.0)
        self.az_step_spinbox.setDecimals(2)
        hlayout.addWidget(az_step_label)
        hlayout.addWidget(self.az_step_spinbox)
        layout.addLayout(hlayout)

        self.extents_layout.addLayout(layout)

    def _setup_el_extent_widget(self) -> None:
        layout = QVBoxLayout()

        el_extent_label = QLabel("Elevation", self.extents_groupbox)
        el_extent_label.setAlignment(Qt.AlignHCenter)
        el_extent_label.setFont(font["BOLD_14"])
        layout.addWidget(el_extent_label)

        hlayout = QHBoxLayout()
        el_start_label = QLabel("Start", self.extents_groupbox)
        hlayout.addWidget(el_start_label)
        self.el_start_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.el_start_spinbox.setRange(-180.0, 180.0)
        self.el_start_spinbox.setSingleStep(1.0)
        self.el_start_spinbox.setDecimals(2)
        hlayout.addWidget(self.el_start_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        el_stop_label = QLabel("Stop", self.extents_groupbox)
        hlayout.addWidget(el_stop_label)
        self.el_stop_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.el_stop_spinbox.setRange(-180.0, 180.0)
        self.el_stop_spinbox.setSingleStep(1.0)
        self.el_stop_spinbox.setDecimals(2)
        hlayout.addWidget(self.el_stop_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        el_step_label = QLabel("Step", self.extents_groupbox)
        hlayout.addWidget(el_step_label)
        self.el_step_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.el_step_spinbox.setRange(-180.0, 180.0)
        self.el_step_spinbox.setSingleStep(1.0)
        self.el_step_spinbox.setDecimals(2)
        hlayout.addWidget(self.el_step_spinbox)
        layout.addLayout(hlayout)

        self.extents_layout.addLayout(layout)

    def _setup_jog_box(self) -> None:
        layout = QGridLayout()

        jog_az_label = QLabel("Azimuth", self.jog_groupbox)
        jog_az_label.setFont(font["BOLD_12"])
        jog_az_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_az_label, 0, 0, 1, 3)

        jog_az_step_label = QLabel("Step", self.jog_groupbox)
        jog_az_step_label.setFont(font["BOLD_12"])
        jog_az_step_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_az_step_label, 0, 3, 1, 1)

        jog_az_to_label = QLabel("Jog Azimuth To", self.jog_groupbox)
        jog_az_to_label.setFont(font["BOLD_12"])
        jog_az_to_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_az_to_label, 0, 4, 1, 1)

        jog_left_icon = qta.icon('fa.arrow-left')
        self.jog_az_left_btn = QPushButton(
            text="", icon=jog_left_icon, parent=self.jog_groupbox
        )
        self.jog_az_left_btn.setIconSize(QSize(32, 32))
        layout.addWidget(self.jog_az_left_btn, 1, 0, 1, 1)

        self.jog_az_zero_btn = QPushButton("0", self.jog_groupbox)
        self.jog_az_zero_btn.setFont(font["BOLD_20"])
        layout.addWidget(self.jog_az_zero_btn, 1, 1, 1, 1)

        jog_right_icon = qta.icon('fa.arrow-right')
        self.jog_az_right_btn = QPushButton(
            text="", icon=jog_right_icon, parent=self.jog_groupbox
        )
        self.jog_az_right_btn.setIconSize(QSize(32, 32))
        layout.addWidget(self.jog_az_right_btn, 1, 2, 1, 1)

        jog_az_submit_icon = qta.icon('fa.check')
        self.jog_az_submit_btn = QPushButton(
            text="", icon=jog_az_submit_icon, parent=self.jog_groupbox
        )
        self.jog_az_submit_btn.setIconSize(QSize(32, 32))
        layout.addWidget(self.jog_az_submit_btn, 1, 5, 1, 1)

        self.jog_az_step_spinbox = QDoubleSpinBox(self.jog_groupbox)
        self.jog_az_step_spinbox.setRange(0.0, 180.0)
        self.jog_az_step_spinbox.setSingleStep(0.5)
        self.jog_az_step_spinbox.setDecimals(2)
        layout.addWidget(self.jog_az_step_spinbox, 1, 3, 1, 1)

        self.jog_az_to_lineedit = QLineEdit(self.jog_groupbox)
        self.jog_az_to_lineedit.setPlaceholderText("0.0")
        layout.addWidget(self.jog_az_to_lineedit, 1, 4, 1, 1)

        jog_el_label = QLabel("Elevation", self.jog_groupbox)
        jog_el_label.setFont(font["BOLD_12"])
        jog_el_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_el_label, 2, 0, 1, 3)

        jog_el_step_label = QLabel("Step", self.jog_groupbox)
        jog_el_step_label.setFont(font["BOLD_12"])
        jog_el_step_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_el_step_label, 2, 3, 1, 1)

        jog_el_to_label = QLabel("Jog Elevation To", self.jog_groupbox)
        jog_el_to_label.setFont(font["BOLD_12"])
        jog_el_to_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_el_to_label, 2, 4, 1, 1)

        jog_ccw_icon = qta.icon('ph.arrow-counter-clockwise-bold')
        self.jog_el_ccw_btn = QPushButton(
            text="", icon=jog_ccw_icon, parent=self.jog_groupbox
        )
        self.jog_el_ccw_btn.setIconSize(QSize(32, 32))
        layout.addWidget(self.jog_el_ccw_btn, 3, 0, 1, 1)

        self.jog_el_zero_btn = QPushButton("0", self.jog_groupbox)
        self.jog_el_zero_btn.setFont(font["BOLD_20"])
        layout.addWidget(self.jog_el_zero_btn, 3, 1, 1, 1)

        jog_cw_icon = qta.icon('ph.arrow-clockwise-bold')
        self.jog_el_cw_btn = QPushButton(
            text="", icon=jog_cw_icon, parent=self.jog_groupbox
        )
        self.jog_el_cw_btn.setIconSize(QSize(32, 32))
        layout.addWidget(self.jog_el_cw_btn, 3, 2, 1, 1)

        jog_el_submit_icon = qta.icon('fa.check')
        self.jog_el_submit_btn = QPushButton(
            text="", icon=jog_el_submit_icon, parent=self.jog_groupbox
        )
        self.jog_el_submit_btn.setIconSize(QSize(32, 32))
        layout.addWidget(self.jog_el_submit_btn, 3, 5, 1, 1)

        self.jog_el_step_spinbox = QDoubleSpinBox(self.jog_groupbox)
        self.jog_el_step_spinbox.setRange(0.0, 180.0)
        self.jog_el_step_spinbox.setSingleStep(0.5)
        self.jog_el_step_spinbox.setDecimals(2)
        layout.addWidget(self.jog_el_step_spinbox, 3, 3, 1, 1)

        self.jog_el_to_lineedit = QLineEdit(self.jog_groupbox)
        self.jog_el_to_lineedit.setPlaceholderText("0.0")
        layout.addWidget(self.jog_el_to_lineedit, 3, 4, 1, 1)

        self.jog_layout.addLayout(layout)

        hlayout = QHBoxLayout()

        az_pos_layout = QVBoxLayout()

        az_pos_label = QLabel("Azimuth", self.jog_groupbox)
        az_pos_label.setFont(font["BOLD_12"])
        az_pos_label.setAlignment(Qt.AlignHCenter)
        az_pos_layout.addWidget(az_pos_label)

        self.az_pos_lineedit = QLineEdit(self.jog_groupbox)
        self.az_pos_lineedit.setReadOnly(True)
        self.az_pos_lineedit.setFont(font["BOLD_20_IBM"])
        self.az_pos_lineedit.setAlignment(Qt.AlignHCenter)
        az_pos_layout.addWidget(self.az_pos_lineedit)

        hlayout.addLayout(az_pos_layout)

        el_pos_layout = QVBoxLayout()

        el_pos_label = QLabel("Elevation", self.jog_groupbox)
        el_pos_label.setFont(font["BOLD_12"])
        el_pos_label.setAlignment(Qt.AlignHCenter)
        el_pos_layout.addWidget(el_pos_label)

        self.el_pos_lineedit = QLineEdit(self.jog_groupbox)
        self.el_pos_lineedit.setReadOnly(True)
        self.el_pos_lineedit.setFont(font["BOLD_20_IBM"])
        self.el_pos_lineedit.setAlignment(Qt.AlignHCenter)
        el_pos_layout.addWidget(self.el_pos_lineedit)

        hlayout.addLayout(el_pos_layout)

        zero_btn_layout = QHBoxLayout()
        self.set_zero_btn = QPushButton("Set 0,0", self.jog_groupbox)
        zero_btn_layout.addWidget(self.set_zero_btn)

        self.ret_to_zero_btn = QPushButton("Return to 0,0", self.jog_groupbox)
        zero_btn_layout.addWidget(self.ret_to_zero_btn)

        self.jog_layout.addLayout(hlayout)
        self.jog_layout.addLayout(zero_btn_layout)

        self.jog_groupbox.setEnabled(False)

    def _jog(self, axis: JogAxis, direction: JogDir, relative: bool) -> None:
        if self._positioner is None:
            QMessageBox.critical(self, "Connection Error", "Positioner not connected")
            return

        LOG.debug("Setting up jog thread")
        self.set_enabled(False)
        if axis == JogAxis.AZIMUTH:
            if direction == JogDir.ZERO:
                angle = 0.0
            elif relative:
                angle = self._positioner.current_azimuth + (
                    direction.value * float(SETTINGS["positioner/jog-az-step"])
                )
            else:
                angle = self.jog_az_to
            LOG.debug("Starting azimuth jog thread")
            self.jog_thread.run = functools.partial(self.jog_az, angle)
        elif axis == JogAxis.ELEVATION:
            if direction == JogDir.ZERO:
                angle = 0.0
            if relative:
                angle = self._positioner.current_elevation + (
                    direction.value * float(SETTINGS["positioner/jog-el-step"])
                )
            else:
                angle = self.jog_el_to
            LOG.debug("Starting elevation jog thread")
            self.jog_thread.run = functools.partial(self.jog_el, angle)
        else:
            raise ValueError("Unreachable")

        LOG.debug(f"Jogging angle: {angle}")
        self.jog_thread.start()

    # ========== API ==========
    def connect(self, model: str, port: str) -> None:
        """Connect to a positioner.

        Arguments:
            model: model string
            port: serial port the positioner is on
        """
        # TODO: Move messageboxes out of API code
        if model == "":
            QMessageBox.warning(self, "Invalid model", "Must specify model")
            return

        if port == "":
            QMessageBox.warning(self, "Invalid address", "Must specify port")
            return

        LOG.debug(f"Connecting to positioner {model} at {port}")
        try:
            self._positioner = Positioner.connect(model, port)
        except Exception as e:
            LOG.debug(f"{e=}")
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connect to to positioner: {e}"
            )
            return

        LOG.info("Connected")
        self.positioner_connected.emit()

    def positioner(self) -> Positioner:
        """Get the positioner."""
        if self._positioner is None:
            raise RuntimeError("Positioner not connected")

        return self._positioner

    def az_extents(self) -> np.ndarray:
        """Get the current azimuth extents as a numpy array."""
        return np.arange(
            float(SETTINGS["positioner/az-start"]),
            float(SETTINGS["positioner/az-stop"]) + float(SETTINGS["positioner/az-step"]),
            float(SETTINGS["positioner/az-step"]),
        )

    def el_extents(self) -> np.ndarray:
        """Get the current elevation extents as a numpy array."""
        return np.arange(
            float(SETTINGS["positioner/el-start"]),
            float(SETTINGS["positioner/el-stop"]) + float(SETTINGS["positioner/el-step"]),
            float(SETTINGS["positioner/el-step"]),
        )

    def jog_az(self, angle: float) -> None:
        """Jog the azimuth plane to an angle.

        Arguments:
            angle: absolute angle to move the azimuth to

        Raises:
            RuntimeError: if the positioner is not connected
        """
        LOG.debug("Jogging azimuth")
        if self._positioner is None:
            raise RuntimeError("Positioner not connected")

        self._positioner.move_azimuth_absolute(angle)

    def jog_el(self, angle: float) -> None:
        """Jog the elevation plane to an angle.

        Arguments:
            angle: absolute angle to move the elevation to

        Raises:
            RuntimeError: if the positioner is not connected
        """
        LOG.debug("Jogging elevation")
        if self._positioner is None:
            raise RuntimeError("Positioner not connected")

        self._positioner.move_elevation_absolute(angle)

    def set_enabled(self, enable: bool) -> None:
        """Enable/Disable the plugin.

        Arguments:
            enable: True to enable, False to disable
        """
        self.jog_groupbox.setEnabled(enable)
