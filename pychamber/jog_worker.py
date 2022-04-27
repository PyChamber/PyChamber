from enum import Enum, auto

from PyQt5.QtCore import QMutex, pyqtSignal

from pychamber.positioner import Positioner
from pychamber.worker import Worker


class JogAxis(Enum):
    AZIMUTH = auto()
    ELEVATION = auto()


class JogWorker(Worker):
    finished = pyqtSignal()
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)

    def __init__(
        self,
        mutex: QMutex,
        axis: JogAxis,
        angle: float,
        positioner: Positioner,
        relative: bool = False,
    ) -> None:
        super(JogWorker, self).__init__(mutex, parent=None)
        self.axis = axis
        self.angle = angle
        self.positioner = positioner
        self.relative = relative

    def run(self) -> None:
        if self.axis == JogAxis.AZIMUTH:
            self._jog_az()
        elif self.axis == JogAxis.ELEVATION:
            self._jog_el()
        self.finished.emit()

    def _jog_az(self) -> None:
        if self.relative:
            self.mutex.lock()
            self.positioner.move_azimuth_relative(self.angle)
            pos = self.positioner.current_azimuth
            self.mutex.unlock()
        else:
            self.mutex.lock()
            self.positioner.move_azimuth_absolute(self.angle)
            pos = self.positioner.current_azimuth
            self.mutex.unlock()
        self.azMoveComplete.emit(pos)

    def _jog_el(self) -> None:
        if self.relative:
            self.mutex.lock()
            self.positioner.move_elevation_relative(self.angle)
            pos = self.positioner.current_elevation
            self.mutex.unlock()
        else:
            self.mutex.lock()
            self.positioner.move_elevation_absolute(self.angle)
            pos = self.positioner.current_elevation
            self.mutex.unlock()
        self.elMoveComplete.emit(pos)


class JogZeroWorker(Worker):
    finished = pyqtSignal()
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)

    def __init__(self, mutex: QMutex, positioner: Positioner) -> None:
        super(JogZeroWorker, self).__init__(mutex)
        self.positioner = positioner

    def run(self) -> None:
        self.mutex.lock()
        self.positioner.move_elevation_absolute(0.0)
        self.mutex.unlock()
        self.elMoveComplete.emit(0.0)

        self.mutex.lock()
        self.positioner.move_azimuth_absolute(0.0)
        self.mutex.unlock()
        self.azMoveComplete.emit(0.0)

        self.finished.emit()
