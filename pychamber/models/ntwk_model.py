from tkinter.messagebox import RETRY
from typing import Any, Dict, List, Optional, Set

import numpy as np
import skrf
from PyQt5.QtCore import QObject, pyqtSignal

from pychamber.logger import log


class NetworkModel(QObject):
    data_added = pyqtSignal(skrf.Network)
    data_loaded = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._data: skrf.NetworkSet = skrf.NetworkSet()
        self._polarizations: Set[str] = set()
        self._azimuths: Set[float] = set()
        self._elevations: Set[float] = set()

    def __str__(self) -> str:
        return str(self._data)

    def __len__(self) -> int:
        return len(self._data)

    @property
    def frequencies(self) -> np.ndarray:
        return self._data[0].frequency.f  # type: ignore

    @property
    def azimuths(self) -> np.ndarray:
        return np.array(self._azimuths)

    @property
    def elevations(self) -> np.ndarray:
        return np.array(self._elevations)

    @property
    def polarizations(self) -> List[str]:
        return list(self._polarizations)

    def reset(self) -> None:
        log.debug("Resetting network model")
        self._data = skrf.NetworkSet()
        self._polarizations = set()
        self._azimuths = set()
        self._elevations = set()

    def add_data(self, ntwk: skrf.Network) -> None:
        log.debug(f"Adding data: {ntwk}")
        if (
            'azimuth' not in ntwk.params
            or 'elevation' not in ntwk.params
            or 'polarization' not in ntwk.params
        ):
            raise ValueError("ntwk is missing a parameter")

        self._polarizations.add(ntwk.params['polarization'])
        self._azimuths.add(ntwk.params['azimuth'])
        self._elevations.add(ntwk.params['elevation'])

        self._data = skrf.NetworkSet(list(self._data) + [ntwk])  # type: ignore
        self.data_added.emit(ntwk)

    def get_data(self, **kwargs) -> skrf.NetworkSet:
        criteria = {key: val for key, val in kwargs.items() if val is not None}
        log.debug(f"Getting data with {criteria=}")
        try:
            return self._data.sel(criteria)
        except IndexError:
            # An IndexError happens when we don't have data.
            # In that case, just return an empty networkset
            return skrf.NetworkSet()

    def load_data(self, data: skrf.NetworkSet) -> None:
        self._data = data
        self.data_loaded.emit()

    def mags(
        self,
        polarization: str,
        frequency: Optional[str] = None,
        azimuth: Optional[float] = None,
        elevation: Optional[float] = None,
    ) -> np.ndarray:
        if len(self._data) == 0:
            return np.array([])

        params: Dict[str, Any] = {
            'polarization': polarization,
        }

        if azimuth is not None:
            params['azimuth'] = azimuth
        if elevation is not None:
            params['elevation'] = elevation

        subset = self._data.sel(params)

        if frequency is not None:
            return np.array([ntwk[freq].s_db for ntwk in subset])  # type: ignore
        else:
            return np.array([ntwk.s_db for ntwk in subset])  # type: ignore

    def data(self) -> skrf.NetworkSet:
        return self._data
