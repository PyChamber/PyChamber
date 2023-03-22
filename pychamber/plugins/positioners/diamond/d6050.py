from __future__ import annotations

import math
from dataclasses import dataclass

import serial
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from pychamber.positioner import PositionerConnectionError, PositionerLimitException
from pychamber.settings import CONF

from .d6050_widget import Ui_D6050Widget


@dataclass
class BoardResponse:
    """Response from the positioner."""

    type_: str
    address: str
    status: str
    response: str

    def __str__(self) -> str:
        """String representation of the response."""
        return f"{self.type_}{self.address}{self.status}{self.response}"


class Diamond_D6050Widget(QWidget, Ui_D6050Widget):
    def __init__(self, positioner: Diamond_D6050, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)


class Diamond_D6050(QObject):
    # TODO: Make these part of the protocol? ABC?
    jogStarted = Signal()
    jogCompleted = Signal()
    jogAborted = Signal()

    manufacturer = "Diamond Engineering"
    model = "D6050"

    _serial_baudrate = 57600
    _serial_timeout = 1

    _az_steps_per_deg = 800
    _el_steps_per_deg = 320

    _x = "X0"
    _y = "Y0"

    _az_axis = _y
    _el_axis = _x

    _initial_pos_x = 2000000000
    _initial_pos_y = 2000000000

    _x_run_current = 150
    _x_hold_current = 50
    _x_dwell = 10
    _x_stepping_mode = 4
    _x_encoder_mode = "C"
    _x_axis_direction = "-"
    _x_start_speed = "1000"
    _x_end_speed = "5000"
    _x_slope = "8"

    _y_run_current = 200
    _y_hold_current = 50
    _y_dwell = 10
    _y_stepping_mode = 4
    _y_encoder_mode = "C"
    _y_axis_direction = "-"
    _y_start_speed = "1000"
    _y_end_speed = "8000"
    _y_slope = "8"

    _step_delay = 0.1
    _delay_mode = 1

    def __init__(self, serial_port: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.serial_connection = serial.Serial(
            port=serial_port, baudrate=self._serial_baudrate, timeout=self._serial_timeout
        )

        self._azimuth = float(CONF['diamond_d6050_azimuth'])
        self._elevation = float(CONF['diamond_d6050_elevation'])

        self.test_connection()
        self.reset()

    def create_widget(self, parent: QWidget | None = None) -> QWidget | None:
        return Diamond_D6050Widget(self, parent)

    @property
    def azimuth(self) -> float:
        return self._azimuth

    @property
    def elevation(self) -> float:
        return self._elevation

    def test_connection(self) -> None:
        resp = self.write("X0")
        if resp is None:
            raise PositionerConnectionError()

    def abort_movement(self) -> None:
        self.write("X0*")
        self.write("Y0*")
        self.write("Z0*")
        self.jogAborted.emit()

    def zero_all(self) -> None:
        self._azimuth = 0
        self._elevation = 0
        CONF['diamond_d6050_azimuth'] = 0
        CONF['diamond_d6050_elevation'] = 0

    def zero_az(self) -> None:
        self._azimuth = 0
        CONF['diamond_d6050_azimuth'] = 0

    def zero_el(self) -> None:
        self._elevation = 0
        CONF['diamond_d6050_elevation'] = 0

    def move(self, axis: str, steps: str) -> None:
        self.write(f"{axis}RN{steps}")
        while True:
            resp = self.write(f"{axis}")
            if not resp:
                continue
            if resp.status == "f" or resp.status == ">":
                break
            elif resp.status == "H":
                raise PositionerLimitException("Home limit")
            elif resp.status == "L":
                raise PositionerLimitException("Max limit")


    def move_az_absolute(self, azimuth: float) -> None:
        diff = azimuth - self.azimuth
        self.move_az_relative(diff)

    def move_az_relative(self, angle: float) -> None:
        self.jogStarted.emit()
        if math.isclose(angle, 0.0):
            self.jogCompleted.emit()
            return
        steps = -int(self._az_steps_per_deg * angle)
        self.move(self._az_axis, f"{steps:+}")
        self._azimuth += angle
        CONF['diamond_d6050_azimuth'] = self._azimuth
        self.jogCompleted.emit()

    def move_el_absolute(self, elevation: float) -> None:
        diff = elevation - self.elevation
        self.move_el_relative(diff)

    def move_el_relative(self, angle: float) -> None:
        self.jogStarted.emit()
        if math.isclose(angle, 0.0):
            self.jogCompleted.emit()
            return
        steps = int(self._el_steps_per_deg * angle)
        self.move(self._el_axis, f"{steps:+}")
        self._elevation += angle
        CONF['diamond_d6050_elevation'] = self._elevation
        self.jogCompleted.emit()

    def write(self, cmd: str) -> BoardResponse | None:
        self.serial_connection.reset_input_buffer()
        self.serial_connection.write(f"{cmd}\r".encode("ascii"))

        return self.check_response()

    def abort_all(self) -> None:
        print("ABORTING")
        self.write("X0*")
        self.write("Y0*")
        self.write("Z0*")

    def check_response(self) -> BoardResponse | None:
        buffer = self.serial_connection.read_until(b"\r")
        if buffer:
            try:
                buffer = buffer.decode("ascii")
                if buffer.startswith("x0") or buffer.startswith("y0") or buffer.startswith("z0"):
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
        self.write(f"{self._x}N-0cz00")
        self.write(f"{self._y}N-0cz00")

        self.set_abs_count(self._x, self._initial_pos_x)
        self.set_abs_count(self._y, self._initial_pos_y)

        self.set_motor_currents(self._x, self._x_run_current, self._x_hold_current, self._x_dwell)
        self.set_motor_currents(self._y, self._y_run_current, self._y_hold_current, self._y_dwell)

        self.set_motor_hold(self._x, True)
        self.set_motor_hold(self._y, True)

        self.set_stepping_mode(self._x, self._x_stepping_mode)
        self.set_stepping_mode(self._y, self._y_stepping_mode)

        self.set_encoder_mode(self._x, self._x_encoder_mode)
        self.set_encoder_mode(self._y, self._y_encoder_mode)

        self.set_axis_direction(self._x, self._x_axis_direction)
        self.set_axis_direction(self._y, self._y_axis_direction)

        self.enable_encoder(self._x)
        self.enable_encoder(self._y)

        self.set_start_speed(self._x, self._x_start_speed)
        self.set_start_speed(self._y, self._y_start_speed)

        self.set_end_speed(self._x, self._x_end_speed)
        self.set_end_speed(self._y, self._y_end_speed)

        self.set_move_slope(self._x, self._x_slope)
        self.set_move_slope(self._y, self._y_slope)

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

    def set_axis_direction(self, axis: str, direction: str) -> None:
        self.write(f"{axis}qN{direction}")

    def enable_encoder(self, axis: str) -> None:
        self.write(f"{axis}qE")

    def set_start_speed(self, axis: str, speed: int) -> None:
        self.write(f"{axis}B{speed}")

    def set_end_speed(self, axis: str, speed: int) -> None:
        self.write(f"{axis}E{speed}")

    def set_move_slope(self, axis: str, slope: int) -> None:
        self.write(f"{axis}S{slope}")
