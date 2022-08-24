from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

import numpy as np
import pkg_resources  # type: ignore
import serial
from omegaconf import OmegaConf
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from pychamber.logger import log
from pychamber.settings import SETTINGS


class JogAxis(Enum):
    AZIMUTH = auto()
    ELEVATION = auto()


class JogDir(Enum):
    MINUS = -1.0
    ZERO = 0.0
    PLUS = 1.0


@dataclass
class BoardResponse:
    type_: str
    address: str
    status: str
    response: str

    def __str__(self) -> str:
        return f"{self.type_}{self.address}{self.status}{self.response}"


class PositionerError(RuntimeError):
    pass


class Positioner(QObject):
    """A positioner that holds the antenna under test.

    Establishes a serial port and issues commands over it to control a
    positioner using commands determined by a config file.
    """

    # Signals
    az_move_complete = pyqtSignal()
    el_move_complete = pyqtSignal()

    _models: Dict[str, Any] = dict()

    def __init__(self, name: str, serial_port: str, parent=None) -> None:
        """Create a Positioner object.

        Args:
            name: model name of positioner (e.g. D6050)
            serial_port: port name of serial port connection
        """
        super().__init__(parent)
        yaml_str = pkg_resources.resource_string(__name__, f"configs/{name}.yaml").decode(
            'utf-8'
        )
        self.config = OmegaConf.create(yaml_str)

        self.serial = serial.Serial(
            serial_port, self.config.serial.baudrate, timeout=self.config.serial.timeout
        )

    # Register subclasses so we can later call Positioner[<model name>]() to construct
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls._models[cls.__name__] = cls

    @classmethod
    def connect(cls, model: str, serial_port: str) -> Positioner:
        return cls._models[model](serial_port)

    @classmethod
    def model_names(cls) -> List[str]:
        return list(cls._models.keys())

    def __enter__(self) -> Positioner:
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        # self.save_state()
        self.serial.close()

    def zero(self) -> None:
        SETTINGS["positioner/az-pos"] = 0.0
        SETTINGS["positioner/el-pos"] = 0.0

        self.current_azimuth = 0.0
        self.current_elevation = 0.0

    def write(self, cmd: str) -> Optional[BoardResponse]:
        ...

    def query(self, cmd: str) -> str:
        ...

    def abort_all(self) -> None:
        ...

    @property  # type: ignore
    def current_azimuth(self) -> float:
        ...

    @current_azimuth.setter  # type: ignore
    def current_azimuth(self) -> None:
        ...

    @property  # type: ignore
    def current_elevation(self) -> float:
        ...

    @current_elevation.setter  # type: ignore
    def current_elevation(self) -> None:
        ...

    def move_azimuth_relative(self, angle: float) -> None:
        ...

    def move_azimuth_absolute(self, angle: float) -> None:
        ...

    def move_elevation_relative(self, angle: float) -> None:
        ...

    def move_elevation_absolute(self, angle: float) -> None:
        ...


class D6050(Positioner):
    x = "X0"
    y = "Y0"

    def __init__(self, serial_port: str) -> None:
        super(D6050, self).__init__("D6050", serial_port)

        self.az_steps_per_deg = self.config.hardware.steps_per_degree[
            self.config.hardware.azimuth
        ]
        self.el_steps_per_deg = self.config.hardware.steps_per_degree[
            self.config.hardware.elevation
        ]

        self.azimuth = self.config.hardware.azimuth.upper() + "0"
        self.elevation = self.config.hardware.elevation.upper() + "0"

        self.current_az: float = float(SETTINGS["positioner/az-pos"])
        self.current_el: float = float(SETTINGS["positioner/el-pos"])
        log.debug(f"{self.current_az=}")
        log.debug(f"{self.current_el=}")

        self.reset()

    def write(self, cmd: str) -> Optional[BoardResponse]:
        self.serial.reset_input_buffer()
        self.serial.write(f"{cmd}\r".encode('ascii'))
        QTimer.singleShot(500, lambda: None)

        resp = self.check_response()

        return resp

    def query(self, cmd: str) -> str:
        resp = self.write(cmd)
        return resp.response if resp else ""

    def abort_all(self) -> None:
        self.write("X0*")
        self.write("Y0*")
        self.write("Z0*")

    def check_response(self) -> Optional[BoardResponse]:
        buffer = self.serial.read_until(b'\r')
        if buffer:
            try:
                buffer = buffer.decode('ascii')
                if (
                    buffer.startswith('x0')
                    or buffer.startswith('y0')
                    or buffer.startswith('z0')
                ):
                    return BoardResponse(
                        buffer[0],
                        buffer[1],
                        buffer[2],
                        buffer[3:-2] if len(buffer) >= 4 else "",
                    )
                else:
                    return None
            except IndexError:
                return None
        else:
            return None

    def reset(self) -> None:
        self.init(self.x)
        self.init(self.y)

        self.set_abs_count(self.x, self.config.hardware.initial_pos.x)
        self.set_abs_count(self.y, self.config.hardware.initial_pos.y)

        self.set_motor_currents(
            self.x,
            self.config.hardware.run_current.x,
            self.config.hardware.hold_current.x,
            self.config.hardware.dwell.x,
        )
        self.set_motor_currents(
            self.y,
            self.config.hardware.run_current.y,
            self.config.hardware.hold_current.y,
            self.config.hardware.dwell.y,
        )

        self.set_motor_hold(self.x, True)
        self.set_motor_hold(self.y, True)

        self.set_stepping_mode(self.x, self.config.hardware.stepping_mode.x)
        self.set_stepping_mode(self.y, self.config.hardware.stepping_mode.y)

        self.set_encoder_mode(self.x, self.config.hardware.encoder_mode.x)
        self.set_encoder_mode(self.y, self.config.hardware.encoder_mode.y)

        self.set_axis_direction(self.x, self.config.hardware.axis_direction.x)
        self.set_axis_direction(self.y, self.config.hardware.axis_direction.y)

        self.enable_encoder(self.x)
        self.enable_encoder(self.y)

        self.set_start_speed(self.x, self.config.hardware.start_speed.x)
        self.set_start_speed(self.y, self.config.hardware.start_speed.y)

        self.set_end_speed(self.x, self.config.hardware.end_speed.x)
        self.set_end_speed(self.y, self.config.hardware.end_speed.y)

        self.set_move_slope(self.x, self.config.hardware.slope.x)
        self.set_move_slope(self.y, self.config.hardware.slope.y)

    def init(self, axis: str) -> None:
        self.write(f"{axis}N-0cz00")

    @property
    def current_az_steps(self) -> int:
        az_steps = self.query(f"{self.azimuth}m")
        log.debug(f"{az_steps=}")
        return int(az_steps)

    @property
    def current_el_steps(self) -> int:
        el_steps = self.query(f"{self.elevation}m")
        return int(el_steps)

    @property
    def current_azimuth(self) -> float:
        return float(self.current_az)

    @current_azimuth.setter
    def current_azimuth(self, val: float) -> None:
        self.current_az = val

    @property
    def current_elevation(self) -> float:
        return self.current_el

    @current_elevation.setter
    def current_elevation(self, val: float) -> None:
        self.current_el = val

    def set_abs_count(self, axis: str, pos: int) -> None:
        self.write(f"{axis}A{pos}")

    def set_motor_currents(self, axis: str, run: int, hold: int, dwell: int) -> None:
        self.write(f"{axis}P3,{run},{hold},{dwell}")

    def set_motor_hold(self, axis: str, hold: bool) -> None:
        self.write(f"{axis}P{int(hold)}")

    def set_stepping_mode(self, axis: str, mode: int) -> None:
        self.write(f"{axis}H{mode}")

    def set_encoder_mode(self, axis: str, mode: int) -> None:
        self.write(f"{axis}qm{mode}")

    def set_axis_direction(self, axis: str, dir: str) -> None:
        self.write(f"{axis}qN{dir}")

    def enable_encoder(self, axis: str) -> None:
        self.write(f"{axis}qE")

    def set_start_speed(self, axis: str, speed: int) -> None:
        self.write(f"{axis}B{speed}")

    def set_end_speed(self, axis: str, speed: int) -> None:
        self.write(f"{axis}E{speed}")

    def set_move_slope(self, axis: str, slope: int) -> None:
        self.write(f"{axis}S{slope}")

    def read_encoder(self, axis: str) -> int:
        self.serial.flush()
        self.write(f"{axis}qP")
        if read := self.serial.read_all():
            return int(read.decode('ascii'))
        else:
            return 0

    def move(self, axis: str, steps: str) -> None:
        self.write(f"{axis}RN{steps}")
        while True:
            resp = self.write(f"{axis}")
            if not resp:
                continue
            if resp.status == 'f' or resp.status == '>':
                if axis == self.x:
                    self.el_move_complete.emit()
                elif axis == self.y:
                    self.az_move_complete.emit()
                break
            elif resp.status == 'H':
                raise PositionerError('Home limit')
            elif resp.status == 'L':
                raise PositionerError('Max limit')

    def move_azimuth_relative(self, angle: float) -> None:
        if np.isclose(angle, 0.0):
            self.az_move_complete.emit()
            return
        steps = -int(self.az_steps_per_deg * angle)
        log.debug(f"move az relative: {angle} degrees / {steps} steps")
        self.move(self.azimuth, f"{steps:+}")
        self.current_az += angle

    def move_elevation_relative(self, angle: float) -> None:
        if np.isclose(angle, 0.0):
            self.el_move_complete.emit()
            return
        steps = -int(self.el_steps_per_deg * angle)
        log.debug(f"move el relative: {angle} degrees / {steps} steps")
        self.move(self.elevation, f"{steps:+}")
        self.current_el += angle

    def move_azimuth_absolute(self, angle: float) -> None:
        diff = angle - self.current_azimuth
        self.move_azimuth_relative(diff)

    def move_elevation_absolute(self, angle: float) -> None:
        diff = angle - self.current_elevation
        self.move_elevation_relative(diff)
