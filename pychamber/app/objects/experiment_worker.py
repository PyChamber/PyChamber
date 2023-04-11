from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from pychamber import positioner

import functools
import time

import numpy as np
import skrf
from qtpy.QtCore import QEventLoop, QObject, QThread, QTimer, Signal


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
        phis: np.ndarray,
        thetas: np.ndarray,
        polarizations: list[tuple[str, int, int]],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.analyzer = analyzer
        self.positioner = positioner
        self.phis = phis
        self.thetas = thetas
        self.polarizations = polarizations

    def run(self) -> None:
        self._running = True
        self.started.emit()
        iter_times = np.array([])
        total_iters = len(self.phis) * len(self.thetas)
        total_completed = 0
        for theta in self.thetas:
            if QThread.currentThread().isInterruptionRequested():
                self._running = False
            self.wait_for(
                functools.partial(self.positioner.move_theta_absolute, theta), self.positioner.jogCompleted, timeout=None
            )

            cut_completed = 0
            for phi in self.phis:
                if QThread.currentThread().isInterruptionRequested():
                    self._running = False
                start = time.time()

                self.wait_for(
                    functools.partial(self.positioner.move_phi_absolute, phi),
                    self.positioner.jogCompleted,
                    timeout=None,
                )

                for pol_name, a, b in self.polarizations:
                    ntwk = self.analyzer.ch1.get_sdata(a, b)
                    ntwk.params = {
                        "phi": phi,
                        "theta": theta,
                        "polarization": pol_name,
                        "calibrated": False
                    }
                    self.dataAcquired.emit(ntwk)
                stop = time.time()

                cut_completed += 1
                total_completed += 1
                iter_times = np.append(iter_times, stop - start)
                self.cutIterCountUpdated.emit(cut_completed)
                self.totalIterCountUpdated.emit(total_completed)
                avg_iter_time = np.average(iter_times)
                time_remaining_est = (total_iters - total_completed) * avg_iter_time
                self.timeEstUpdated.emit(time_remaining_est)

                if not self._running:
                    break
            if not self._running:
                break

        self.finished.emit()

    def wait_for(self, fn: Callable, signal, timeout: int | None = 5000) -> None:
        event_loop = QEventLoop()
        signal.connect(event_loop.quit)
        QTimer.singleShot(0, fn)

        if timeout is not None:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(event_loop.quit)
            timer.start()

        event_loop.exec()
