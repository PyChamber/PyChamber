import time
from typing import Optional

import numpy as np
from PyQt5.QtCore import QMutex, pyqtSignal
from skrf.vi import vna

from pychamber.positioner import Positioner
from pychamber.worker import Worker


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
        azimuths: Optional[np.ndarray] = None,
        elevations: Optional[np.ndarray] = None,
    ) -> None:
        super(ScanWorker, self).__init__(mutex)
        self.positioner = positioner
        self.analyzer = analyzer
        self.azimuths = azimuths
        self.elevations = elevations
        self.abort = False

    def run(self) -> None:
        if (self.azimuths is not None) and (self.elevations is not None):
            self._run_full_scan()
        elif self.azimuths is not None:
            self._run_az_scan()
        elif self.elevations is not None:
            self._run_el_scan()
        self.finished.emit()

    def _run_full_scan(self) -> None:
        assert self.azimuths is not None
        assert self.elevations is not None

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

                pos_meta = {'azimuth': az, 'elevation': el}
                start = time.time()
                self.mutex.lock()

                self.positioner.move_elevation_absolute(el)
                pos = self.positioner.current_elevation
                self.elMoveComplete.emit(pos)

                ntwk = self.analyzer.get_snp_network()
                ntwk.params = pos_meta
                self.dataAcquired.emit(ntwk)

                self.mutex.unlock()
                end = time.time()

                completed = i * len(self.azimuths) + j
                progress = completed * 100 // total_iters
                self.progress.emit(progress)
                self.cutProgress.emit(j * 100 // len(self.elevations))
                single_iter_time = end - start
                remaining = total_iters - completed
                time_remaining = single_iter_time * remaining
                self.timeUpdate.emit(time_remaining)

            if self.abort:
                break

    def _run_az_scan(self) -> None:
        assert self.azimuths is not None

        for i, az in enumerate(self.azimuths):
            if self.abort:
                self.mutex.lock()
                self.positioner.abort_all()
                self.mutex.unlock()
                break

            pos_meta = {'azimuth': az, 'elevation': 0}
            start = time.time()
            self.mutex.lock()
            self.positioner.move_azimuth_absolute(az)
            pos = self.positioner.current_azimuth
            self.azMoveComplete.emit(pos)

            ntwk = self.analyzer.get_snp_network()
            ntwk.params = pos_meta
            self.dataAcquired.emit(ntwk)

            self.mutex.unlock()
            end = time.time()

            progress = i * 100 // len(self.azimuths)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.azimuths) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)

    def _run_el_scan(self) -> None:
        assert self.elevations is not None

        for i, el in enumerate(self.elevations):
            if self.abort:
                self.mutex.lock()
                self.positioner.abort_all()
                self.mutex.unlock()
                break

            pos_meta = {'azimuth': 0, 'elevation': el}
            start = time.time()
            self.mutex.lock()
            self.positioner.move_elevation_absolute(el)
            pos = self.positioner.current_elevation
            self.elMoveComplete.emit(pos)

            ntwk = self.analyzer.get_snp_network()
            ntwk.params = pos_meta
            self.dataAcquired.emit(ntwk)

            self.mutex.unlock()
            end = time.time()

            progress = i * 100 // len(self.elevations)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.elevations) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)
