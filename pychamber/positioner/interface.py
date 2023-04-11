from qtpy.QtCore import QObject, Signal
from qtpy.QtWidgets import QWidget


class PositionerLimitException(Exception):
    pass


class PositionerConnectionError(RuntimeError):
    pass


class Positioner(QObject):
    jogStarted = Signal()
    jogCompleted = Signal()
    jogAborted = Signal()

    _manufacturer = ""
    _model = ""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def create_widget(self, parent: QWidget | None = None) -> QWidget | None:
        return None

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @property
    def model(self) -> str:
        return self._model

    @property
    def phi(self) -> float:
        raise NotImplementedError("Must be implemented in subclass")

    @property
    def theta(self) -> float:
        raise NotImplementedError("Must be implemented in subclass")

    def test_connection(self) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def abort_movement(self) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def zero_all(self) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def zero_phi(self) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def zero_theta(self) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def move_phi_absolute(self, phi: float) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def move_phi_relative(self, angle: float) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def move_theta_absolute(self, theta: float) -> None:
        raise NotImplementedError("Must be implemented in subclass")

    def move_theta_relative(self, angle: float) -> None:
        raise NotImplementedError("Must be implemented in subclass")
