import time
from typing import Dict, Optional, Sequence

import numpy as np
from PyQt5.QtCore import QMutex, pyqtSignal
from skrf.vi import vna

from pychamber.network_model import NetworkModel
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
        ntwk_models: Dict[str, NetworkModel],
        azimuths: Optional[np.ndarray] = None,
        elevations: Optional[np.ndarray] = None,
        pol1: Optional[Sequence[int]] = None,
        pol2: Optional[Sequence[int]] = None,
    ) -> None:
        super(ScanWorker, self).__init__(mutex)
        self.positioner = positioner
        self.analyzer = analyzer
        self.ntwk_models = ntwk_models
        self.azimuths = azimuths
        self.elevations = elevations
        self.pol1 = pol1
        self.pol2 = pol2
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
        assert self.analyzer is not None
        assert self.positioner_ is not None
        assert self.ntwk_models is not None

        total_iters = len(self.azimuths) * len(self.elevations)
        pol_1_data = []
        pol_2_data = []
        for i, az in enumerate(self.azimuths):
            self.mutex.lock()
            self.positioner_.move_azimuth_absolute(az)
            pos = self.positioner_.current_azimuth
            self.mutex.unlock()
            self.azMoveComplete.emit(pos)
            for j, el in enumerate(self.elevations):
                if self.abort:
                    self.mutex.lock()
                    self.positioner_.abort_all()
                    self.mutex.unlock()
                    break

                pos_meta = {'azimuth': az, 'elevation': el}
                start = time.time()
                self.mutex.lock()
                self.positioner_.move_elevation_absolute(el)
                pos = self.positioner_.current_elevation
                self.elMoveComplete.emit(pos)
                if self.pol1:
                    # FIXME: just getting s21 is INCORRECT!!!
                    ntwk = self.analyzer.get_snp_network(self.pol1).s21  # type: ignore
                    ntwk.params = pos_meta
                    pol_1_data.append(ntwk)
                if self.pol2:
                    ntwk = self.analyzer.get_snp_network(self.pol2).s21  # type: ignore
                    ntwk.params = pos_meta
                    pol_2_data.append(ntwk)
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

        self.dataAcquired.emit(
            {'pol1': NetworkModel(pol_1_data), 'pol2': NetworkModel(pol_2_data)}
        )

    def _run_az_scan(self) -> None:
        assert self.azimuths is not None
        assert self.analyzer is not None
        assert self.positioner_ is not None
        assert self.ntwk_models is not None

        pol_1_data = []
        pol_2_data = []
        for i, az in enumerate(self.azimuths):
            if self.abort:
                self.mutex.lock()
                self.positioner_.abort_all()
                self.mutex.unlock()
                break

            pos_meta = {'azimuth': az, 'elevation': 0}
            start = time.time()
            self.mutex.lock()
            self.positioner_.move_azimuth_absolute(az)
            pos = self.positioner_.current_azimuth
            self.azMoveComplete.emit(pos)

            if self.pol1:
                ntwk = self.analyzer.get_snp_network(self.pol1).s21  # type: ignore
                ntwk.params = pos_meta
                pol_1_data.append(ntwk)
            if self.pol2:
                ntwk = self.analyzer.get_snp_network(self.pol2).s21  # type: ignore
                ntwk.params = pos_meta
                pol_2_data.append(ntwk)
            self.mutex.unlock()
            end = time.time()

            progress = i * 100 // len(self.azimuths)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.azimuths) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)

        self.dataAcquired.emit(
            {'pol1': NetworkModel(pol_1_data), 'pol2': NetworkModel(pol_2_data)}
        )

    def _run_el_scan(self) -> None:
        assert self.elevations is not None
        assert self.analyzer is not None
        assert self.positioner_ is not None
        assert self.ntwk_models is not None

        pol_1_data = []
        pol_2_data = []
        for i, el in enumerate(self.elevations):
            if self.abort:
                self.mutex.lock()
                self.positioner_.abort_all()
                self.mutex.unlock()
                break

            pos_meta = {'azimuth': 0, 'elevation': el}
            start = time.time()
            self.mutex.lock()
            self.positioner_.move_elevation_absolute(el)
            pos = self.positioner_.current_elevation
            self.elMoveComplete.emit(pos)

            if self.pol1:
                ntwk = self.analyzer.get_snp_network(self.pol1).s21  # type: ignore
                ntwk.params = pos_meta
                pol_1_data.append(ntwk)
            if self.pol2:
                ntwk = self.analyzer.get_snp_network(self.pol2).s21  # type: ignore
                ntwk.params = pos_meta
                pol_2_data.append(ntwk)
            self.mutex.unlock()
            end = time.time()

            progress = i * 100 // len(self.elevations)
            self.progress.emit(progress)
            single_iter_time = end - start
            remaining = len(self.elevations) - i
            time_remaining = single_iter_time * remaining
            self.timeUpdate.emit(time_remaining)

        self.dataAcquired.emit(
            {'pol1': NetworkModel(pol_1_data), 'pol2': NetworkModel(pol_2_data)}
        )
