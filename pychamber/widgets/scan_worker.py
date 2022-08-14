import time
from typing import List

import numpy as np
from PyQt5.QtCore import QMutex, pyqtSignal
from skrf.vi import vna

from pychamber.logger import log
from pychamber.plugins.positioner.positioner import Positioner
from pychamber.polarization import Polarization
from pychamber.widgets.worker import Worker


class ScanWorker(Worker):
    finished = pyqtSignal()
    aborted = pyqtSignal()
    progress = pyqtSignal(int)
    cutProgress = pyqtSignal(int)
    timeUpdate = pyqtSignal(float)
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)
    dataAcquired = pyqtSignal(object)

    def __init__(
        self,
        mutex: QMutex,
        positioner: Positioner,
        analyzer: vna.VNA,
        polarizations: List[Polarization],
        azimuths: np.ndarray,
        elevations: np.ndarray,
    ) -> None:
        super(ScanWorker, self).__init__(mutex)
        self.positioner = positioner
        self.analyzer = analyzer
        self.polarizations = polarizations
        self.azimuths = azimuths
        self.elevations = elevations
        self.abort = False

    def run(self) -> None:
        log.info("Starting scan worker")
        self.mutex.lock()
        for pol in self.polarizations:
            self.analyzer.create_measurement(f"ANT_{pol.param}", pol.param)
        self.mutex.unlock()

        try:
            self._run_scan()

        except Exception as e:
            log.error(f"{e}")

        finally:
            self.mutex.lock()
            for pol in self.polarizations:
                self.analyzer.delete_measurement(f"ANT_{pol.param}")
            self.mutex.unlock()

        self.finished.emit()

    def _run_scan(self) -> None:
        total_iters = len(self.azimuths) * len(self.elevations)
        for i, az in enumerate(self.azimuths):
            self.mutex.lock()
            self.positioner.move_azimuth_absolute(az)
            pos = self.positioner.current_azimuth
            self.mutex.unlock()
            self.azMoveComplete.emit(pos)
            for j, el in enumerate(self.elevations):
                if self.abort:
                    self.mutex.lock()
                    self.positioner.abort_all()
                    self.mutex.unlock()
                    break

                self.mutex.lock()
                start = time.time()
                self.positioner.move_elevation_absolute(el)
                pos = self.positioner.current_elevation
                self.elMoveComplete.emit(pos)

                for pol in self.polarizations:
                    pos_meta = {'azimuth': az, 'elevation': el, 'polarization': pol.label}
                    self.analyzer.set_active_measurement(f"ANT_{pol.param}")
                    ntwk = self.analyzer.get_active_trace()
                    ntwk.params = pos_meta
                    self.dataAcquired.emit(ntwk)

                end = time.time()
                self.mutex.unlock()

                completed = i * len(self.elevations) + j
                progress = completed * 100 // total_iters
                self.progress.emit(progress)
                self.cutProgress.emit(j * 100 // len(self.elevations))
                remaining = total_iters - completed
                single_iter_time = end - start
                time_remaining = single_iter_time * remaining
                self.timeUpdate.emit(time_remaining)

            if self.abort:
                break
