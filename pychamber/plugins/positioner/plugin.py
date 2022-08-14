import functools
from typing import Optional

import numpy as np
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap
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
    QWidget,
)
from serial.tools import list_ports

from pychamber.logger import log
from pychamber.plugins.positioner.positioner import JogAxis, JogDir, Positioner
from pychamber.settings import SETTINGS
from pychamber.ui import font, size_policy

from ..base import PyChamberPlugin


class PositionerPlugin(PyChamberPlugin):
    # Signals
    positioner_connected = pyqtSignal()
    jog_started = pyqtSignal()
    jog_complete = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setObjectName('positioner')
        self.setLayout(QVBoxLayout())
        self.setSizePolicy(size_policy["PREF_PREF"])

        self._positioner: Optional[Positioner] = None

        self.current_az: float = 0.0
        self.current_el: float = 0.0
        self.jog_az_to: float = 0.0
        self.jog_el_to: float = 0.0

        self.jog_thread: QThread = QThread(None)
        self.jog_thread.started.connect(self.jog_started.emit)
        self.jog_thread.finished.connect(lambda: self.jog_groupbox.setEnabled(True))
        self.jog_thread.finished.connect(lambda: self.jog_complete.emit())

    def setup(self) -> None:
        self._add_widgets()

    def post_visible_setup(self) -> None:
        log.debug("Post-visible setup...")
        self._init_inputs()
        self._connect_signals()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.jog_thread.quit()
        self.jog_thread.wait()
        super().closeEvent(event)

    def _add_widgets(self) -> None:
        log.debug("Creating Positioner widget...")
        self.groupbox = QGroupBox("Positioner", self)
        self.layout().addWidget(self.groupbox)

        self.groupbox_layout = QVBoxLayout(self.groupbox)
        hlayout = QHBoxLayout()

        model_label = QLabel("Model", self.groupbox)
        model_label.setSizePolicy(size_policy["MIN_PREF"])
        hlayout.addWidget(model_label)

        self.model_combobox = QComboBox(self.groupbox)
        self.model_combobox.setSizePolicy(size_policy["EXP_PREF"])
        hlayout.addWidget(self.model_combobox)

        port_label = QLabel("Port", self.groupbox)
        port_label.setSizePolicy(size_policy["MIN_PREF"])
        hlayout.addWidget(port_label)

        self.port_combobox = QComboBox(self.groupbox)
        self.port_combobox.setSizePolicy(size_policy["EXP_PREF"])
        hlayout.addWidget(self.port_combobox)

        self.connect_btn = QPushButton("Connect", self.groupbox)
        self.connect_btn.setSizePolicy(size_policy["MIN_PREF"])
        hlayout.addWidget(self.connect_btn)

        self.groupbox_layout.addLayout(hlayout)

        self.extents_groupbox = QGroupBox(self.groupbox)
        self.extents_layout = QHBoxLayout(self.extents_groupbox)
        self._setup_az_extent_widget()
        self._setup_el_extent_widget()
        self.groupbox_layout.addWidget(self.extents_groupbox)

        self.jog_groupbox = QGroupBox(self.groupbox)
        self.jog_layout = QVBoxLayout(self.jog_groupbox)
        self._setup_jog_box()
        self.groupbox_layout.addWidget(self.jog_groupbox)

    def _init_inputs(self) -> None:
        log.debug("Populating models...")
        self.model_combobox.clear()
        self.model_combobox.addItems(Positioner.model_names())

        log.debug("Populating addrs...")
        self.port_combobox.clear()
        ports = [p.device for p in list_ports.comports()]
        self.port_combobox.addItems(ports)

        log.debug("Updating inputs from settings...")
        self.model_combobox.setCurrentText(SETTINGS['positioner-model'])
        self.port_combobox.setCurrentText(SETTINGS['positioner-port'])
        self.az_start_spinbox.setValue(float(SETTINGS["az-start"]))
        self.az_stop_spinbox.setValue(float(SETTINGS["az-stop"]))
        self.az_step_spinbox.setValue(float(SETTINGS["az-step"]))
        self.el_start_spinbox.setValue(float(SETTINGS["el-start"]))
        self.el_stop_spinbox.setValue(float(SETTINGS["el-stop"]))
        self.el_step_spinbox.setValue(float(SETTINGS["el-step"]))

    def _connect_signals(self) -> None:
        self.model_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("positioner-model", text)
        )
        self.port_combobox.currentTextChanged.connect(
            lambda text: SETTINGS.setval("positioner-port", text)
        )
        self.connect_btn.clicked.connect(self._on_connect_clicked)

        self.az_start_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("az-start", val)
        )
        self.az_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("az-step", val)
        )
        self.az_stop_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("az-stop", val)
        )

        self.el_start_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("el-start", val)
        )
        self.el_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("el-step", val)
        )
        self.el_stop_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("el-stop", val)
        )

        self.jog_az_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("jog-az-step", val)
        )
        self.jog_el_step_spinbox.valueChanged.connect(
            lambda val: SETTINGS.setval("jog-el-step", val)
        )

        self.jog_az_to_lineedit.textChanged.connect(self._on_jog_az_to_changed)
        self.jog_el_to_lineedit.textChanged.connect(self._on_jog_el_to_changed)

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

        self.az_pos_lineedit.textChanged.connect(
            lambda text: setattr(self, "current_az", text)
        )
        self.el_pos_lineedit.textChanged.connect(
            lambda text: setattr(self, "current_el", text)
        )

        self.set_zero_btn.clicked.connect(self._on_set_zero_clicked)

    def _on_jog_az_to_changed(self, val: str) -> None:
        self.jog_az_to = float(val)

    def _on_jog_el_to_changed(self, val: str) -> None:
        self.jog_el_to = float(val)

    def _on_az_pos_changed(self, val: str) -> None:
        self.current_az = float(val)

    def _on_el_pos_changed(self, val: str) -> None:
        self.current_el = float(val)

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

    def _on_az_move_complete(self, pos: float) -> None:
        self.az_pos_lineedit.setText(str(pos))

    def _on_el_move_complete(self, pos: float) -> None:
        self.el_pos_lineedit.setText(str(pos))

    def _on_positioner_connected(self) -> None:
        assert self._positioner is not None
        self._positioner.az_move_complete.connect(self._on_az_move_complete)
        self._positioner.az_move_complete.connect(self.jog_complete.emit)
        self._positioner.el_move_complete.connect(self._on_el_move_complete)
        self._positioner.el_move_complete.connect(self.jog_complete.emit)

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
        self.az_start_spinbox.setSizePolicy(size_policy["EXP_PREF"])
        self.az_start_spinbox.setRange(-180.0, 180.0)
        self.az_start_spinbox.setSingleStep(1.0)
        self.az_start_spinbox.setDecimals(2)
        hlayout.addWidget(self.az_start_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        az_stop_label = QLabel("Stop", self.extents_groupbox)
        self.az_stop_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.az_stop_spinbox.setSizePolicy(size_policy["EXP_PREF"])
        self.az_stop_spinbox.setRange(-180.0, 180.0)
        self.az_stop_spinbox.setSingleStep(1.0)
        self.az_stop_spinbox.setDecimals(2)
        hlayout.addWidget(az_stop_label)
        hlayout.addWidget(self.az_stop_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        az_step_label = QLabel("Step", self.extents_groupbox)
        self.az_step_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.az_step_spinbox.setSizePolicy(size_policy["EXP_PREF"])
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
        self.el_start_spinbox.setSizePolicy(size_policy["EXP_PREF"])
        self.el_start_spinbox.setRange(-180.0, 180.0)
        self.el_start_spinbox.setSingleStep(1.0)
        self.el_start_spinbox.setDecimals(2)
        hlayout.addWidget(self.el_start_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        el_stop_label = QLabel("Stop", self.extents_groupbox)
        hlayout.addWidget(el_stop_label)
        self.el_stop_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.el_stop_spinbox.setSizePolicy(size_policy["EXP_PREF"])
        self.el_stop_spinbox.setRange(-180.0, 180.0)
        self.el_stop_spinbox.setSingleStep(1.0)
        self.el_stop_spinbox.setDecimals(2)
        hlayout.addWidget(self.el_stop_spinbox)
        layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        el_step_label = QLabel("Step", self.extents_groupbox)
        hlayout.addWidget(el_step_label)
        self.el_step_spinbox = QDoubleSpinBox(self.extents_groupbox)
        self.el_step_spinbox.setSizePolicy(size_policy["EXP_PREF"])
        self.el_step_spinbox.setRange(-180.0, 180.0)
        self.el_step_spinbox.setSingleStep(1.0)
        self.el_step_spinbox.setDecimals(2)
        hlayout.addWidget(self.el_step_spinbox)
        layout.addLayout(hlayout)

        self.extents_layout.addLayout(layout)

    def _setup_jog_box(self) -> None:
        layout = QGridLayout()

        jog_az_label = QLabel("Azimuth", self.jog_groupbox)
        jog_az_label.setSizePolicy(size_policy["PREF_MIN"])
        jog_az_label.setFont(font["BOLD_12"])
        jog_az_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_az_label, 0, 0, 1, 3)

        jog_az_step_label = QLabel("Step", self.jog_groupbox)
        jog_az_step_label.setSizePolicy(size_policy["PREF_MIN"])
        jog_az_step_label.setFont(font["BOLD_12"])
        jog_az_step_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_az_step_label, 0, 3, 1, 1)

        jog_az_to_label = QLabel("Jog Azimuth To", self.jog_groupbox)
        jog_az_to_label.setSizePolicy(size_policy["PREF_MIN"])
        jog_az_to_label.setFont(font["BOLD_12"])
        jog_az_to_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_az_to_label, 0, 4, 1, 1)

        self.jog_az_left_btn = QPushButton(self.jog_groupbox)
        self.jog_az_left_btn.setIcon(QIcon(QPixmap(":/icons/icons/LeftArrow.png")))
        self.jog_az_left_btn.setIconSize(QSize(32, 32))
        self.jog_az_left_btn.setSizePolicy(size_policy["MIN_PREF"])
        layout.addWidget(self.jog_az_left_btn, 1, 0, 1, 1)

        self.jog_az_zero_btn = QPushButton("0", self.jog_groupbox)
        self.jog_az_zero_btn.setSizePolicy(size_policy["MIN_PREF"])
        self.jog_az_zero_btn.setFont(font["BOLD_20"])
        layout.addWidget(self.jog_az_zero_btn, 1, 1, 1, 1)

        self.jog_az_right_btn = QPushButton(self.jog_groupbox)
        self.jog_az_right_btn.setIcon(QIcon(QPixmap(":/icons/icons/RightArrow.png")))
        self.jog_az_right_btn.setIconSize(QSize(32, 32))
        self.jog_az_right_btn.setSizePolicy(size_policy["MIN_PREF"])
        layout.addWidget(self.jog_az_right_btn, 1, 2, 1, 1)

        self.jog_az_submit_btn = QPushButton(self.jog_groupbox)
        self.jog_az_submit_btn.setIcon(QIcon(QPixmap(":/icons/icons/Check.png")))
        self.jog_az_submit_btn.setIconSize(QSize(32, 32))
        self.jog_az_submit_btn.setSizePolicy(size_policy["MIN_PREF"])
        layout.addWidget(self.jog_az_submit_btn, 1, 5, 1, 1)

        self.jog_az_step_spinbox = QDoubleSpinBox(self.jog_groupbox)
        self.jog_az_step_spinbox.setSizePolicy(size_policy["MIN_PREF"])
        self.jog_az_step_spinbox.setRange(0.0, 180.0)
        self.jog_az_step_spinbox.setSingleStep(0.5)
        self.jog_az_step_spinbox.setDecimals(2)
        layout.addWidget(self.jog_az_step_spinbox, 1, 3, 1, 1)

        self.jog_az_to_lineedit = QLineEdit(self.jog_groupbox)
        self.jog_az_to_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.jog_az_to_lineedit.setPlaceholderText("0.0")
        layout.addWidget(self.jog_az_to_lineedit, 1, 4, 1, 1)

        jog_el_label = QLabel("Elevation", self.jog_groupbox)
        jog_el_label.setSizePolicy(size_policy["PREF_MIN"])
        jog_el_label.setFont(font["BOLD_12"])
        jog_el_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_el_label, 2, 0, 1, 3)

        jog_el_step_label = QLabel("Step", self.jog_groupbox)
        jog_el_step_label.setSizePolicy(size_policy["PREF_MIN"])
        jog_el_step_label.setFont(font["BOLD_12"])
        jog_el_step_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_el_step_label, 2, 3, 1, 1)

        jog_el_to_label = QLabel("Jog Elevation To", self.jog_groupbox)
        jog_el_to_label.setSizePolicy(size_policy["PREF_MIN"])
        jog_el_to_label.setFont(font["BOLD_12"])
        jog_el_to_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(jog_el_to_label, 2, 4, 1, 1)

        self.jog_el_cw_btn = QPushButton("", self.jog_groupbox)
        self.jog_el_cw_btn.setIcon(QIcon(QPixmap(":/icons/icons/DownArrow.png")))
        self.jog_el_cw_btn.setIconSize(QSize(32, 32))
        self.jog_el_cw_btn.setSizePolicy(size_policy["MIN_PREF"])
        layout.addWidget(self.jog_el_cw_btn, 3, 0, 1, 1)

        self.jog_el_zero_btn = QPushButton("0", self.jog_groupbox)
        self.jog_el_zero_btn.setSizePolicy(size_policy["MIN_PREF"])
        self.jog_el_zero_btn.setFont(font["BOLD_20"])
        layout.addWidget(self.jog_el_zero_btn, 3, 1, 1, 1)

        self.jog_el_ccw_btn = QPushButton("", self.jog_groupbox)
        self.jog_el_ccw_btn.setIcon(QIcon(QPixmap(":/icons/icons/DownArrow.png")))
        self.jog_el_ccw_btn.setIconSize(QSize(32, 32))
        self.jog_el_ccw_btn.setSizePolicy(size_policy["MIN_PREF"])
        layout.addWidget(self.jog_el_ccw_btn, 3, 2, 1, 1)

        self.jog_el_submit_btn = QPushButton("", self.jog_groupbox)
        self.jog_el_submit_btn.setIcon(QIcon(QPixmap(":/icons/icons/Check.png")))
        self.jog_el_submit_btn.setIconSize(QSize(32, 32))
        self.jog_el_submit_btn.setSizePolicy(size_policy["MIN_PREF"])
        layout.addWidget(self.jog_el_submit_btn, 3, 5, 1, 1)

        self.jog_el_step_spinbox = QDoubleSpinBox(self.jog_groupbox)
        self.jog_el_step_spinbox.setSizePolicy(size_policy["MIN_PREF"])
        self.jog_el_step_spinbox.setRange(0.0, 180.0)
        self.jog_el_step_spinbox.setSingleStep(0.5)
        self.jog_el_step_spinbox.setDecimals(2)
        layout.addWidget(self.jog_el_step_spinbox, 3, 3, 1, 1)

        self.jog_el_to_lineedit = QLineEdit(self.jog_groupbox)
        self.jog_el_to_lineedit.setSizePolicy(size_policy["PREF_PREF"])
        self.jog_el_to_lineedit.setPlaceholderText("0.0")
        layout.addWidget(self.jog_el_to_lineedit, 3, 4, 1, 1)

        self.jog_layout.addLayout(layout)

        hlayout = QHBoxLayout()

        az_pos_layout = QVBoxLayout()

        az_pos_label = QLabel("Azimuth", self.jog_groupbox)
        az_pos_label.setSizePolicy(size_policy["PREF_PREF"])
        az_pos_label.setFont(font["BOLD_12"])
        az_pos_label.setAlignment(Qt.AlignHCenter)
        az_pos_layout.addWidget(az_pos_label)

        self.az_pos_lineedit = QLineEdit(self.jog_groupbox)
        self.az_pos_lineedit.setReadOnly(True)
        self.az_pos_lineedit.setSizePolicy(size_policy["MIN_PREF"])
        self.az_pos_lineedit.setFont(font["BOLD_12"])
        az_pos_layout.addWidget(self.az_pos_lineedit)

        hlayout.addLayout(az_pos_layout)

        el_pos_layout = QVBoxLayout()

        el_pos_label = QLabel("Elevation", self.jog_groupbox)
        el_pos_label.setSizePolicy(size_policy["PREF_PREF"])
        el_pos_label.setFont(font["BOLD_12"])
        el_pos_label.setAlignment(Qt.AlignHCenter)
        el_pos_layout.addWidget(el_pos_label)

        self.el_pos_lineedit = QLineEdit(self.jog_groupbox)
        self.el_pos_lineedit.setReadOnly(True)
        self.el_pos_lineedit.setSizePolicy(size_policy["MIN_PREF"])
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

        log.debug("Setting up jog thread")
        self.jog_groupbox.setEnabled(False)
        match axis:
            case JogAxis.AZIMUTH:
                if direction == JogDir.ZERO:
                    angle = 0.0
                elif relative:
                    angle = self.current_az + (direction.value * SETTINGS["az-step"])
                else:
                    angle = self.jog_az_to
                log.debug("Starting azimuth jog thread")
                self.jog_thread.run = functools.partial(self.jog_az, angle)
            case JogAxis.ELEVATION:
                if direction == JogDir.ZERO:
                    angle = 0.0
                if relative:
                    angle = self.current_el + (direction.value * SETTINGS["el_step"])
                else:
                    angle = self.jog_el_to
                log.debug("Starting elevation jog thread")
                self.jog_thread.run = functools.partial(self.jog_el, angle)

        self.jog_thread.start()

    # ========== API ==========
    def connect(self, model: str, port: str) -> None:
        if model == "":
            QMessageBox.warning(self, "Invalid model", "Must specify model")
            return

        if port == "":
            QMessageBox.warning(self, "Invalid address", "Must specify port")
            return

        log.debug(f"Connecting to positioner {model} at {port}")
        try:
            self._positioner = Positioner.connect(model, port)
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connecto to positioner: {e}"
            )
            return

        log.info("Connected")
        self.positioner_connected.emit()

    def positioner(self) -> Positioner:
        if self._positioner is None:
            raise RuntimeError("Positioner not connected")

        return self._positioner

    def az_extents(self) -> np.ndarray:
        return np.arange(SETTINGS["az-start"], SETTINGS["az-stop"], SETTINGS["az-step"])

    def el_extents(self) -> np.ndarray:
        return np.arange(SETTINGS["el-start"], SETTINGS["el-stop"], SETTINGS["el-step"])

    def jog_az(self, angle: float) -> None:
        if self._positioner is None:
            raise RuntimeError("Positioner not connected")

        if np.isclose(self.current_az, angle):
            return

        self._positioner.move_azimuth_absolute(angle)

    def jog_el(self, angle: float) -> None:
        if self._positioner is None:
            raise RuntimeError("Positioner not connected")

        if np.isclose(self.current_el, angle):
            return

        self._positioner.move_elevation_absolute(angle)

    def set_enabled(self, enable: bool) -> None:
        self.groupbox.setEnabled(enable)
