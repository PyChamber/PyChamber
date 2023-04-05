import math
import time

from qtpy.QtCore import QObject
from qtpy.QtWidgets import QWidget

from pychamber.positioner import Postioner
from pychamber.settings import CONF


class ExamplePositioner(Postioner):
    _manufacturer = "Example"
    _model = "Example"

    _msecs_per_deg = 25

    def __init__(self, port: str, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._port = port

        stored_phi = CONF["example_positioner_phi"]
        if stored_phi is None:
            CONF["example_positioner_phi"] = 0
        stored_theta = CONF["example_positioner_theta"]
        if stored_theta is None:
            CONF["example_positioner_theta"] = 0

        self._phi = float(CONF["example_positioner_phi"])
        self._theta = float(CONF["example_positioner_theta"])

        self.test_connection()

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
        return self._phi

    @property
    def theta(self) -> float:
        return self._theta

    def test_connection(self) -> None:
        return

    def abort_movement(self) -> None:
        # TODO
        self.jogAborted.emit()

    def zero_all(self) -> None:
        self._phi = 0
        self._theta = 0
        CONF["example_positioner_phi"] = 0
        CONF["example_positioner_theta"] = 0

    def zero_phi(self) -> None:
        self._phi = 0
        CONF["example_positioner_phi"] = 0

    def zero_theta(self) -> None:
        self._theta = 0
        CONF["example_positioner_theta"] = 0

    def move_phi_absolute(self, phi: float) -> None:
        diff = phi - self._phi
        self.move_phi_relative(diff)

    def move_phi_relative(self, angle: float) -> None:
        self.jogStarted.emit()
        if math.isclose(angle, 0.0):
            self.jogCompleted.emit()
            return
        self._phi += angle
        CONF["example_positioner_phi"] = self._phi
        time.sleep(abs(angle) * self._msecs_per_deg / 1000)
        self.jogCompleted.emit()

    def move_theta_absolute(self, theta: float) -> None:
        diff = theta - self._theta
        self.move_theta_relative(diff)

    def move_theta_relative(self, angle: float) -> None:
        self.jogStarted.emit()
        if math.isclose(angle, 0.0):
            self.jogCompleted.emit()
            return
        self._theta += angle
        CONF["example_positioner_theta"] = self._theta
        time.sleep(abs(angle) * self._msecs_per_deg / 1000)
        self.jogCompleted.emit()
