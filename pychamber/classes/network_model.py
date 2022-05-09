from __future__ import annotations

from typing import Optional

import numpy as np
from skrf.network import Network
from skrf.networkSet import NetworkSet


class NetworkModel(NetworkSet):
    @property
    def freqs(self) -> np.ndarray:
        if len(self) == 0:
            return np.array([])
        else:
            return self[0].frequency.f  # type: ignore

    @property
    def azimuths(self) -> np.ndarray:
        if len(self) == 0:
            return np.array([])
        else:
            return np.array(
                [n.params['azimuth'] for n in self.sel({'elevation': 0})]  # type: ignore
            ).reshape(-1, 1)

    @property
    def elevations(self) -> np.ndarray:
        if len(self) == 0:
            return np.array([])
        else:
            return np.array(
                [n.params['elevation'] for n in self.sel({'azimuth': 0})]  # type: ignore
            ).reshape(-1, 1)

    def mags(
        self,
        freq: Optional[str] = None,
        azimuth: Optional[float] = None,
        elevation: Optional[float] = None,
    ) -> np.ndarray:
        if len(self) == 0:
            return np.array([])
        else:
            params = dict()
            if azimuth:
                params['azimuth'] = azimuth
            if elevation:
                params['elevation'] = elevation

            if freq:
                return np.array([n[freq].s_db for n in self.sel(params)])  # type: ignore
            else:
                return self.sel(params)[0].s_db.reshape(-1, 1)  # type: ignore

    def append(self, ntwk: Network) -> NetworkModel:
        return NetworkModel(list(self) + [ntwk])  # type: ignore
