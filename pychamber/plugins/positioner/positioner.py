"""Defines the positioner class."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

import pkg_resources  # type: ignore
import serial
from omegaconf import OmegaConf
from PyQt5.QtCore import QObject, pyqtSignal

from pychamber.settings import SETTINGS
from pychamber.logger import LOG


class JogAxis(Enum):
    """Which axis to jog."""

    AZIMUTH = auto()
    ELEVATION = auto()


class JogDir(Enum):
    """Jog direction +/-."""

    MINUS = -1.0
    ZERO = 0.0
    PLUS = 1.0


@dataclass
class BoardResponse:
    """Response from the positioner.

    Warning:
        This is specific to the D6050's motor driver and might change.
    """

    type_: str
    address: str
    status: str
    response: str

    def __str__(self) -> str:
        """String representation of the response."""
        return f"{self.type_}{self.address}{self.status}{self.response}"


class PositionerError(RuntimeError):
    """Error raised when the positioner encounters an issue, e.g. home limits."""

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
            parent: parent QWidget
        """
        CONFIG: Dict

        super().__init__(parent)

        self.serial = serial.Serial(
            serial_port,
            self.CONFIG["serial"]["baudrate"],
            timeout=self.CONFIG["serial"]["timeout"],
        )

    # Register subclasses so we can later call Positioner[<model name>]() to construct
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls._models[cls.__name__] = cls

    @classmethod
    def connect(cls, model: str, serial_port: str) -> Positioner:
        """Connect to a positioner.

        Classes are registered with __init_subclass__ so we can just connect
        using the model name of the positioner to get an instance of that class.

        Arguments:
            model: model name (class name of the positioner)
            serial_port: serial port the positioner is connected to
        """
        return cls._models[model](serial_port)

    @classmethod
    def model_names(cls) -> List[str]:
        """Get a list of all registered model names."""
        return list(cls._models.keys())

    def __enter__(self) -> Positioner:
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the serial connection."""
        self.serial.close()

    def zero(self) -> None:
        """Zero the positioner.

        Sets the PyChamber plugin setting to all zero and updates the internal state.
        """
        SETTINGS["positioner/az-pos"] = 0.0
        SETTINGS["positioner/el-pos"] = 0.0

        self.current_azimuth = 0.0
        self.current_elevation = 0.0

    def write(self, cmd: str) -> Optional[BoardResponse]:
        """Send a command over the serial port and get the response.

        Arguments:
            cmd: command string to send

        Returns:
            BoardResponse | None: The parsed response from the positioner if there
                was one
        """
        ...

    def query(self, cmd: str) -> str:
        """Send a command and get the plain text positioner response.

        Arguments:
            cmd: command string to send

        Returns:
            str: the response from the positioner
        """
        ...

    def abort_all(self) -> None:
        """Abort all movement."""
        ...

    @property  # type: ignore
    def current_azimuth(self) -> float:
        """The current azimuth position [deg]."""
        ...

    @current_azimuth.setter  # type: ignore
    def current_azimuth(self) -> None:
        ...

    @property  # type: ignore
    def current_elevation(self) -> float:
        """The current elevation position [deg]."""
        ...

    @current_elevation.setter  # type: ignore
    def current_elevation(self) -> None:
        ...

    def move_azimuth_relative(self, angle: float) -> None:
        """Move the azimuth a relative number of degrees.

        Arguments:
            angle: how far to move the positioner's azimuth
        """
        ...

    def move_azimuth_absolute(self, angle: float) -> None:
        """Move the azimuth to an absolute angle.

        Arguments:
            angle: the absolute azimuth to move to
        """
        ...

    def move_elevation_relative(self, angle: float) -> None:
        """Move the elevation a relative number of degrees.

        Arguments:
            angle: how far to move the positioner's elevation
        """
        ...

    def move_elevation_absolute(self, angle: float) -> None:
        """Move the elevation to an absolute angle.

        Arguments:
            angle: the absolute elevation to move to
        """
        ...
