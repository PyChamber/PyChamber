from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychamber import positioner

import functools
import time

import numpy as np
import skrf
from PySide6.QtCore import QEventLoop, QObject, QTimer, Signal


class ExperimentWorker(QObject):
    dataAcquired = Signal(skrf.Network)
    totalIterCountUpdated = Signal(int)
    cutIterCountUpdated = Signal(int)
    timeEstUpdated = Signal(float)
    started = Signal()
    finished = Signal()

    def __init__(
        self,
        analyzer: skrf.vi.vna.VNA,
        positioner: positioner.Positioner,
        azimuths: np.ndarray,
        elevations: np.ndarray,
        polarizations: list[tuple[str, int, int]],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.analyzer = analyzer
        self.positioner = positioner
        self.azimuths = azimuths
        self.elevations = elevations
        self.polarizations = polarizations

    def run(self) -> None:
        self.started.emit()
        iter_times = np.array([])
        total_iters = len(self.azimuths) * len(self.elevations)
        total_completed = 0
        for az in self.azimuths:
            self.wait_for(
                functools.partial(self.positioner.move_az_absolute, az), self.positioner.jogCompleted, timeout=None
            )

            cut_completed = 0
            for el in self.elevations:
                start = time.time()

                self.wait_for(
                    functools.partial(self.positioner.move_el_absolute, el), self.positioner.jogCompleted, timeout=None
                )

                for pol_name, a, b in self.polarizations:
                    ntwk = self.analyzer.ch1.get_sdata(a, b)
                    ntwk.params = {
                        'azimuth': az,
                        'elevation': el,
                        'polarization': pol_name,
                    }
                    self.dataAcquired.emit(ntwk)
                stop = time.time()

                cut_completed += 1
                total_completed += 1
                iter_times = np.append(iter_times, stop - start)
                self.cutIterCountUpdated.emit(cut_completed)
                avg_iter_time = np.average(iter_times)
                time_remaining_est = (total_iters - total_completed) * avg_iter_time
                self.timeEstUpdated.emit(time_remaining_est)

            self.totalIterCountUpdated.emit(total_completed)

        self.finished.emit()
        

    def wait_for(self, fn: callable, signal, timeout: int | None = 5000) -> None:
        event_loop = QEventLoop()
        signal.connect(event_loop.quit)
        QTimer.singleShot(0, fn)

        if timeout is not None:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(event_loop.quit)

        if timeout is not None:
            timer.start()
        event_loop.exec()
