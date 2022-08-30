from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Optional

import numpy as np
from PyQt5.QtCore import QTimer

from pychamber.settings import SETTINGS
from pychamber.logger import LOG

from .positioner import BoardResponse, Positioner, PositionerError


class D6050(Positioner):
    """The Diamond Engineering D6050 Turntable.

    The motor driver is a SimpleStep SSXYXMicroMC.

    - [Turntable
      Website](https://www.diamondeng.net/antenna-measurement/d6050-series/)
    - [Motor Driver
      Manual](https://simplestep.com/wp-content/uploads/2019/03/Simple-Step\
        -Product-Manual-4x.pdf)

    It does have a Z axis, however this is currently unsupported.
    """

    x = "X0"
    y = "Y0"

    CONFIG: Dict = {
        "serial": {"baudrate": 57600, "timeout": 1},
        "hardware": {
            "elevation": "x",
            "azimuth": "y",
            "initial_pos": {
                "x": 2000000000,
                "y": 2000000000,
            },
            "steps_per_degree": {
                "x": 320,
                "y": 800,
            },
            "run_current": {
                "x": 150,
                "y": 200,
            },
            "hold_current": {
                "x": 50,
                "y": 50,
            },
            "dwell": {
                "x": 10,
                "y": 10,
            },
            "stepping_mode": {
                "x": 4,  # 1/16th step mode
                "y": 4,  # 1/16th step mode
            },
            "encoder_mode": {
                "x": "C",  # Count-only
                "y": "C",  # Count-only
            },
            "axis_direction": {
                "x": "-",
                "y": "-",
            },
            "start_speed": {
                "x": 1000,
                "y": 1000,
            },
            "end_speed": {
                "x": 5000,
                "y": 8000,
            },
            "slope": {
                "x": 8,
                "y": 8,
            },
            "stepdelay": 0.1,
            "delaymode": 1,
        },
    }

    def __init__(self, serial_port: str) -> None:
        super(D6050, self).__init__("D6050", serial_port)

        self.az_steps_per_deg = self.CONFIG["hardware"]["steps_per_degree"][
            self.CONFIG["hardware"]["azimuth"]
        ]
        self.el_steps_per_deg = self.CONFIG["hardware"]["steps_per_degree"][
            self.CONFIG["hardware"]["elevation"]
        ]

        self.azimuth = self.CONFIG["hardware"]["azimuth"].upper() + "0"
        self.elevation = self.CONFIG["hardware"]["elevation"].upper() + "0"

        self.current_az: float = float(SETTINGS["positioner/az-pos"])
        self.current_el: float = float(SETTINGS["positioner/el-pos"])
        LOG.debug(f"{self.current_az=}")
        LOG.debug(f"{self.current_el=}")

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

        self.set_abs_count(self.x, self.CONFIG["hardware"]["initial_pos"]["x"])
        self.set_abs_count(self.y, self.CONFIG["hardware"]["initial_pos"]["y"])

        self.set_motor_currents(
            self.x,
            self.CONFIG["hardware"]["run_current"]["x"],
            self.CONFIG["hardware"]["hold_current"]["x"],
            self.CONFIG["hardware"]["dwell"]["x"],
        )
        self.set_motor_currents(
            self.y,
            self.CONFIG["hardware"]["run_current"]["y"],
            self.CONFIG["hardware"]["hold_current"]["y"],
            self.CONFIG["hardware"]["dwell"]["y"],
        )

        self.set_motor_hold(self.x, True)
        self.set_motor_hold(self.y, True)

        self.set_stepping_mode(self.x, self.CONFIG["hardware"]["stepping_mode"]["x"])
        self.set_stepping_mode(self.y, self.CONFIG["hardware"]["stepping_mode"]["y"])

        self.set_encoder_mode(self.x, self.CONFIG["hardware"]["encoder_mode"]["x"])
        self.set_encoder_mode(self.y, self.CONFIG["hardware"]["encoder_mode"]["y"])

        self.set_axis_direction(self.x, self.CONFIG["hardware"]["axis_direction"]["x"])
        self.set_axis_direction(self.y, self.CONFIG["hardware"]["axis_direction"]["y"])

        self.enable_encoder(self.x)
        self.enable_encoder(self.y)

        self.set_start_speed(self.x, self.CONFIG["hardware"]["start_speed"]["x"])
        self.set_start_speed(self.y, self.CONFIG["hardware"]["start_speed"]["y"])

        self.set_end_speed(self.x, self.CONFIG["hardware"]["end_speed"]["x"])
        self.set_end_speed(self.y, self.CONFIG["hardware"]["end_speed"]["y"])

        self.set_move_slope(self.x, self.CONFIG["hardware"]["slope"]["x"])
        self.set_move_slope(self.y, self.CONFIG["hardware"]["slope"]["y"])

    def init(self, axis: str) -> None:
        self.write(f"{axis}N-0cz00")

    @property
    def current_az_steps(self) -> int:
        az_steps = self.query(f"{self.azimuth}m")
        LOG.debug(f"{az_steps=}")
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
        LOG.debug(f"move az relative: {angle} degrees / {steps} steps")
        self.move(self.azimuth, f"{steps:+}")
        self.current_az += angle

    def move_elevation_relative(self, angle: float) -> None:
        if np.isclose(angle, 0.0):
            self.el_move_complete.emit()
            return
        steps = -int(self.el_steps_per_deg * angle)
        LOG.debug(f"move el relative: {angle} degrees / {steps} steps")
        self.move(self.elevation, f"{steps:+}")
        self.current_el += angle

    def move_azimuth_absolute(self, angle: float) -> None:
        diff = angle - self.current_azimuth
        self.move_azimuth_relative(diff)

    def move_elevation_absolute(self, angle: float) -> None:
        diff = angle - self.current_elevation
        self.move_elevation_relative(diff)
