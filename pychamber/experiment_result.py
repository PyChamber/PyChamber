from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import pathlib
from datetime import datetime

import numpy as np
import skrf
from qtpy.QtCore import QObject, QReadWriteLock, Signal

from pychamber import Calibration


class InvalidFileError(Exception):
    pass


class ExperimentResult(QObject):
    dataAppended = Signal()

    def __init__(
        self,
        thetas: np.ndarray,
        phis: np.ndarray,
        polarizations: list[str],
        frequency: skrf.Frequency,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.rw_lock = QReadWriteLock()
        self._ntwk_set = skrf.NetworkSet()
        self._thetas = np.sort(thetas)
        self._phis = np.sort(phis)
        self._polarizations = polarizations
        self._frequency = frequency
        self._s_data = {
            pol: np.full((len(frequency), len(phis), len(thetas)), np.nan, dtype=complex) for pol in polarizations
        }

        self._created = datetime.now()
        self._calibrated = None

    def __str__(self) -> str:
        return (
            f"ExperimentResult(frequencies={self.frequency}, polarizations={self.polarizations}, azimuths={self.phis},"
            f" elevations={self.thetas}) [created {self._created}]"
        )

    def __len__(self) -> int:
        return len(self._ntwk_set)

    def __iter__(self):
        return iter(self._ntwk_set)

    def __getitem__(self, index: int):
        return self._ntwk_set[index]

    @classmethod
    def load(cls, path: str | pathlib.Path) -> ExperimentResult:
        ns = skrf.NetworkSet.from_mdif(str(path))
        if not ns.has_params():
            raise InvalidFileError(f"{path} is an invalid pychamber results file")

        try:
            thetas = np.array(list(set(ns.params_values["theta"])))
            phis = np.array(list(set(ns.params_values["phi"])))
            pols = list(set(ns.params_values["polarization"]))
            frequency = ns[0].frequency
        except (TypeError, KeyError) as e:
            raise InvalidFileError(f"{path} is an invalid pychamber results file") from e

        ret = cls(thetas, phis, pols, frequency)
        for ntwk in ns:
            pol = ntwk.params["polarization"]
            phi_idx = np.where(ret._phis == ntwk.params["phi"])[0]
            theta_idx = np.where(ret._thetas == ntwk.params["theta"])[0]
            ret._s_data[pol][:, phi_idx, theta_idx] = ntwk.s.reshape((-1, 1))
        ret._ntwk_set = ns

        return ret

    def save(self, path: str | pathlib.Path) -> None:
        # Saving to MDIF fails if networks dont have a name, so just set the names to ""
        for ntwk in self._ntwk_set:
            if ntwk.name is None:
                ntwk.name = ""

        self._ntwk_set.write_mdif(path)

    def get_unique_param_vals(self, param: str) -> list[Any]:
        if len(self._ntwk_set) == 0:
            return []
        if self._ntwk_set.params_values is None:
            return []
        try:
            return list(set(self._ntwk_set.params_values[param]))
        except KeyError:
            return []

    def find_nearest(self, array, value) -> tuple:
        idx = np.nanargmin(np.abs(array - value))
        return (idx, array[idx])

    @property
    def frequency(self) -> skrf.Frequency:
        return self._frequency

    @property
    def f(self) -> np.ndarray:
        return self.frequency.f

    @property
    def polarizations(self) -> list[str]:
        return self._polarizations

    @property
    def phis(self) -> np.ndarray:
        return self._phis

    @property
    def thetas(self) -> np.ndarray:
        return self._thetas

    @property
    def params(self) -> dict | None:
        return self._ntwk_set.params

    @property
    def calibrated(self) -> skrf.NetworkSet | None:
        return self._calibrated

    @property
    def raw_data(self) -> skrf.NetworkSet:
        return self._ntwk_set

    def get_theta_cut(self, polarization: str, frequency: float, phi: float):
        f_idx, _ = self.find_nearest(self.f, frequency)
        phi_idx, _ = self.find_nearest(self._phis, phi)
        return self._s_data[polarization][f_idx, phi_idx, :]

    def get_phi_cut(self, polarization: str, frequency: float, theta: float):
        f_idx, _ = self.find_nearest(self.f, frequency)
        theta_idx, _ = self.find_nearest(self._thetas, theta)
        return self._s_data[polarization][f_idx, :, theta_idx]

    def get_over_freq_vals(self, polarization: str, theta: float, phi: float):
        phi_idx, _ = self.find_nearest(self._phis, phi)
        theta_idx, _ = self.find_nearest(self._thetas, theta)
        return self._s_data[polarization][:, phi_idx, theta_idx]

    def get_3d_data(self, polarization: str, frequency: float):
        f_idx, _ = self.find_nearest(self.f, frequency)
        return self._s_data[polarization][f_idx]

    def append(self, ntwk: skrf.Network) -> None:
        new_ns_list = [*self._ntwk_set, ntwk]
        name = self._ntwk_set.name
        new_ns = skrf.NetworkSet(new_ns_list, name=name)
        pol = ntwk.params["polarization"]
        phi_idx = np.where(self._phis == ntwk.params["phi"])[0]
        theta_idx = np.where(self._thetas == ntwk.params["theta"])[0]

        self.rw_lock.lockForWrite()
        self._s_data[pol][:, phi_idx, theta_idx] = ntwk.s.reshape((-1, 1))
        self._ntwk_set = new_ns
        self.rw_lock.unlock()

        self.dataAppended.emit()

    # FIXME: Should be able to iteratively add calibrated values
    def apply_calibration(self, cal: Calibration) -> None:
        for pol in self.polarizations:
            if pol not in self.polarizations:
                raise ValueError(f"Cannot apply this calibration. It does not contain data for polarization: {pol}.")

        calibrated_result_ntwks = []
        for cal_ntwk in list(cal._data):
            try:
                uncalibrated = self._ntwk_set.sel({"polarization": cal_ntwk.name})
            except KeyError:
                continue

            calibrated = uncalibrated / cal_ntwk
            calibrated_result_ntwks += calibrated.ntwk_set

        self._calibrated = skrf.NetworkSet(calibrated_result_ntwks)
