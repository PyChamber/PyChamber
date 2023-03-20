from typing import Protocol

from PySide6.QtWidgets import QWidget


class PositionerLimitException(Exception):
    pass


class PositionerConnectionError(RuntimeError):
    pass


class Postioner(Protocol):
    def create_widget(self, parent: QWidget | None = None) -> QWidget | None:
        return None

    @property
    def manufacturer(self) -> str:
        ...

    @property
    def model(self) -> str:
        ...

    @property
    def azimuth(self) -> float:
        ...

    @property
    def elevation(self) -> float:
        ...

    def test_connection(self) -> None:
        ...

    def abort_movement(self) -> None:
        ...

    def zero_all(self) -> None:
        ...

    def zero_az(self) -> None:
        ...

    def zero_el(self) -> None:
        ...

    def move_az_absolute(self, azimuth: float) -> None:
        ...

    def move_az_relative(self, angle: float) -> None:
        ...

    def move_el_absolute(self, elevation: float) -> None:
        ...

    def move_el_relative(self, angle: float) -> None:
        ...
