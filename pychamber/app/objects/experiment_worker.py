from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychamber import positioner

import time

import numpy as np
import skrf
from PySide6.QtCore import QObject, Signal
from PySide6.QtTest import QSignalSpy


class ExperimentWorker(QObject):
    dataAcquired = Signal(skrf.Network)
    totalIterCountUpdated = Signal(int)
    cutIterCountUpdated = Signal(int)
    avgIterTimeUpdated = Signal(float)
    finished = Signal()

    def __init__(
        self,
        analyzer: skrf.vi.vna.VNA,
        positioner: positioner.Positioner,
        azimuths: np.ndarray,
        elevations: np.ndarray,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.analyzer = analyzer
        self.positioner = positioner
        self.azimuths = azimuths
        self.elevations = elevations

    def run(self) -> None:
        move_spy = QSignalSpy(self.positioner.jogCompleted)
        iter_times = np.array([])

        total_completed = 0
        for az in self.azimuths:
            self.positioner.move_az_absolute(az)
            move_spy.wait()

            cut_completed = 0
            for el in self.elevations:
                start = time.time()
                self.positioner.move_el_absolute(el)
                move_spy.wait()
                ntwk = self.get_snp_network()
                self.dataAcquired.emit(ntwk)
                stop = time.time()

                cut_completed += 1
                total_completed += 1
                iter_times = np.append(iter_times, stop - start)
                self.cutIterCountUpdated.emit(cut_completed)
                self.avgIterTimeUpdated.emit(np.average(iter_times))

            self.totalIterCountUpdated.emit(total_completed)
