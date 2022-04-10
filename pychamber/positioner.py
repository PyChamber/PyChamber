from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import pkg_resources  # type: ignore
import serial
from omegaconf import OmegaConf


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


class Positioner(ABC):
    """A positioner that holds the antenna under test.

    Establishes a serial port and issues commands over it to control a
    positioner using commands determined by a config file.
    """

    def __init__(self, name: str, serial_port: str) -> None:
        """Create a Positioner object.

        Args:
            name: model name of positioner (e.g. D6050)
            serial_port: port name of serial port connection
        """
        yaml_str = pkg_resources.resource_string(__name__, f"configs/{name}.yaml").decode(
            'utf-8'
        )
        self.config = OmegaConf.create(yaml_str)

        self.serial = serial.Serial(
            serial_port, self.config.serial.baudrate, timeout=self.config.serial.timeout
        )

    def __enter__(self) -> Positioner:
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        # self.save_state()
        self.serial.close()

    def zero(self) -> None:
        self.azimuth_deg = 0.0
        self.elevation_deg = 0.0

    @abstractmethod
    def write(self, cmd: str) -> Optional[BoardResponse]:
        pass

    @abstractmethod
    def query(self, cmd: str) -> str:
        pass

    @abstractmethod
    def abort_all(self) -> None:
        pass

    @property  # type: ignore
    @abstractmethod
    def current_azimuth(self) -> float:
        pass

    @current_azimuth.setter  # type: ignore
    @abstractmethod
    def current_azimuth(self) -> None:
        pass

    @property  # type: ignore
    @abstractmethod
    def current_elevation(self) -> float:
        pass

    @current_elevation.setter  # type: ignore
    @abstractmethod
    def current_elevation(self) -> None:
        pass

    @abstractmethod
    def move_azimuth_relative(self, angle: float) -> None:
        pass

    @abstractmethod
    def move_azimuth_absolute(self, angle: float) -> None:
        pass

    @abstractmethod
    def move_elevation_relative(self, angle: float) -> None:
        pass

    @abstractmethod
    def move_elevation_absolute(self, angle: float) -> None:
        pass


class D6050(Positioner):
    x = "X0"
    y = "Y0"

    def __init__(self, serial_port: str) -> None:
        super().__init__("D6050", serial_port)

        self.az_steps_per_deg = self.config.hardware.steps_per_degree[
            self.config.hardware.azimuth
        ]
        self.el_steps_per_deg = self.config.hardware.steps_per_degree[
            self.config.hardware.elevation
        ]

        self.azimuth = self.config.hardware.azimuth.upper() + "0"
        self.elevation = self.config.hardware.elevation.upper() + "0"

        self.reset()

    def write(self, cmd: str) -> Optional[BoardResponse]:
        self.serial.flushInput()
        self.serial.write(f"{cmd}\r".encode('ascii'))
        self.serial.flush()
        time.sleep(0.01)

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
        buffer = self.serial.read_all()
        if buffer:
            buffer = buffer.decode('ascii')
            return BoardResponse(
                buffer[0],
                buffer[1],
                buffer[2],
                buffer[3:-2] if len(buffer) >= 4 else "",
            )
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

        self.zero()

    def init(self, axis: str) -> None:
        self.write(f"{axis}N-0cz00")

    @property
    def current_az_steps(self) -> int:
        return int(self.query(f"{self.azimuth}m"))

    @property
    def current_el_steps(self) -> int:
        return int(self.query(f"{self.elevation}m"))

    @property
    def current_azimuth(self) -> float:
        return self.azimuth_deg

    @current_azimuth.setter
    def current_azimuth(self, angle: float) -> None:
        self.azimuth_deg = angle

    @property
    def current_elevation(self) -> float:
        return self.elevation_deg

    @current_elevation.setter
    def current_elevation(self, angle: float) -> None:
        self.elevation_deg = angle

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
            resp = self.write("")
            if not resp:
                continue
            if resp.status == 'f':
                break
            elif resp.status == 'H':
                raise PositionerError('Home limit')
            elif resp.status == 'L':
                raise PositionerError('Max limit')
            time.sleep(0.05)

    def move_azimuth_relative(self, angle: float) -> None:
        steps = int(self.az_steps_per_deg * angle)
        self.move(self.azimuth, f"{steps:+}")
        self.azimuth_deg += angle

    def move_elevation_relative(self, angle: float) -> None:
        steps = int(self.el_steps_per_deg * angle)
        self.move(self.elevation, f"{steps:+}")
        self.elevation_deg += angle

    def move_azimuth_absolute(self, angle: float) -> None:
        diff = angle - self.current_azimuth
        self.move_azimuth_relative(diff)

    def move_elevation_absolute(self, angle: float) -> None:
        diff = angle - self.current_elevation
        self.move_elevation_relative(diff)
