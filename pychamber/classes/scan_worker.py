import time
from typing import Optional, Tuple

import numpy as np
from PyQt5.QtCore import QMutex, pyqtSignal
from skrf.vi import vna

from pychamber.classes.logger import log
from pychamber.classes.positioner import Positioner
from pychamber.classes.worker import Worker
from pychamber.classes.polarization import Polarization


class ScanWorker(Worker):
    finished = pyqtSignal()
    aborted = pyqtSignal()
    progress = pyqtSignal(int)
    cutProgress = pyqtSignal(int)
    timeUpdate = pyqtSignal(float)
    azMoveComplete = pyqtSignal(float)
    elMoveComplete = pyqtSignal(float)
    pol1Acquired = pyqtSignal(object)
    pol2Acquired = pyqtSignal(object)

    def __init__(
        self,
        mutex: QMutex,
        positioner: Positioner,
        analyzer: vna.VNA,
        polarizations: Tuple[Optional[Polarization], Optional[Polarization]],
        azimuths: Optional[np.ndarray] = None,
        elevations: Optional[np.ndarray] = None,
    ) -> None:
        super(ScanWorker, self).__init__(mutex)
        self.positioner = positioner
        self.analyzer = analyzer
        self.polarizations = polarizations
        self.azimuths = azimuths
        self.elevations = elevations
        self.abort = False

    def run(self) -> None:
        log.debug("Starting scan worker")
        self.mutex.lock()
        for pol in self.polarizations:
            if pol:
                self.analyzer.create_measurement(f"ANT_{pol.param}", pol.param)
        self.mutex.unlock()

        try:
            if (self.azimuths is not None) and (self.elevations is not None):
                self._run_full_scan()
            elif self.azimuths is not None:
                self._run_az_scan()
            elif self.elevations is not None:
                self._run_el_scan()

        except Exception as e:
            log.error(f"{e}")

        finally:
            self.mutex.lock()
            for pol in self.polarizations:
                if pol:
                    self.analyzer.delete_measurement(f"ANT_{pol.param}")
            self.mutex.unlock()

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

                if self.polarizations[0]:
                    self.analyzer.set_active_measurement(f"ANT_{self.polarizations[0].param}")
                    ntwk = self.analyzer.get_active_trace()
                    ntwk.params = pos_meta
                    self.pol1Acquired.emit(ntwk)
                if self.polarizations[1]:
                    self.analyzer.set_active_measurement(f"ANT_{self.polarizations[1].param}")
                    ntwk = self.analyzer.get_active_trace()
                    ntwk.params = pos_meta
                    self.pol2Acquired.emit(ntwk)


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

            if self.polarizations[0]:
                self.analyzer.set_active_measurement(f"ANT_{self.polarizations[0].param}")
                ntwk = self.analyzer.get_active_trace()
                ntwk.params = pos_meta
                self.pol1Acquired.emit(ntwk)
            if self.polarizations[1]:
                self.analyzer.set_active_measurement(f"ANT_{self.polarizations[1].param}")
                ntwk = self.analyzer.get_active_trace()
                ntwk.params = pos_meta
                self.pol2Acquired.emit(ntwk)

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

            if self.polarizations[0]:
                self.analyzer.set_active_measurement(f"ANT_{self.polarizations[0].param}")
                ntwk = self.analyzer.get_active_trace()
                ntwk.params = pos_meta
                self.pol1Acquired.emit(ntwk)
            if self.polarizations[1]:
                self.analyzer.set_active_measurement(f"ANT_{self.polarizations[1].param}")
                ntwk = self.analyzer.get_active_trace()
                ntwk.params = pos_meta
                self.pol2Acquired.emit(ntwk)

            self.mutex.unlock()
            end = time.time()

            progress = i * 100 // len(self.elevations)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.elevations) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)
