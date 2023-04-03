from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import numpy as np
import skrf
from PySide6.QtCore import QObject, QReadWriteLock, Signal


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
        self._s_data = {pol: np.zeros((len(frequency), len(phis), len(thetas)), dtype=complex) for pol in polarizations}

    def __str__(self) -> str:
        return (
            f"ExperimentResult(frequencies={self.frequency}, polarizations={self.polarizations}, azimuths={self.phis},"
            f" elevations={self.thetas}"
        )

    def __len__(self) -> int:
        return len(self._ntwk_set)

    def __iter__(self):
        return iter(self._ntwk_set)

    def __getitem__(self, index: int):
        return self._ntwk_set[index]

    # @classmethod
    # def load(cls, path: str | pathlib.Path) -> ExperimentResult:
    #     ns = skrf.NetworkSet.from_mdif(str(path))
    #     return cls(ns.ntwk_set)

    # def save(self, path: str | pathlib.Path) -> None:
    #     # Saving to MDIF fails if networks dont have a name, so just set the names to ""
    #     for ntwk in self._ntwk_set:
    #         if ntwk.name is None:
    #             ntwk.name = ""

    #     self._ntwk_set.write_mdif(path)

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

    def get_2d_cut(self, polarization: str, frequency: float):
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
