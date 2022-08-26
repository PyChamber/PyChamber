"""Defines a model to interact with network data."""
from typing import Any, Dict, List, Optional, Set

import numpy as np
import skrf
from PyQt5.QtCore import QObject, pyqtSignal

from pychamber.logger import LOG


class NetworkModel(QObject):
    """A model that provides interactions with a scikit-rf NetworkSet.

    Attributes:
        data_added: Signal raised when data is added to the internal network set
        data_loaded: Signal sent when data has been loaded to the internal
            network set. Useful for e.g. notifying plots that there is new data
    """

    data_added = pyqtSignal(skrf.Network)
    data_loaded = pyqtSignal()

    def __init__(self, parent=None) -> None:
        """Create the NetworkModel.

        Arguments:
            parent: parent QWidget
        """
        super().__init__(parent)

        self._data: skrf.NetworkSet = skrf.NetworkSet()
        self._polarizations: Set[str] = set()
        self._azimuths: Set[float] = set()
        self._elevations: Set[float] = set()

    def __str__(self) -> str:
        """A string representation of the internal data."""
        return str(self._data)

    def __len__(self) -> int:
        """The lenght of the internal data."""
        return len(self._data)

    @property
    def frequencies(self) -> np.ndarray:
        """The array of frequency values in the set."""
        return self._data[0].frequency.f  # type: ignore

    @property
    def azimuths(self) -> np.ndarray:
        """The azimuth values in the set."""
        return np.array(list(self._azimuths))

    @property
    def elevations(self) -> np.ndarray:
        """The elevation values in the set."""
        return np.array(list(self._elevations))

    @property
    def polarizations(self) -> List[str]:
        """The polarization names in the set."""
        return list(self._polarizations)

    def reset(self) -> None:
        """Empty the set."""
        LOG.debug("Resetting network model")
        self._data = skrf.NetworkSet()
        self._polarizations = set()
        self._azimuths = set()
        self._elevations = set()

    def add_data(self, ntwk: skrf.Network) -> None:
        """Add a piece of data to the NetworkSet.

        The data is a skrf.Network object that MUST contain the parameters:

        - azimuth
        - elevation
        - polarization

        Arguments:
            ntwk: the piece of data to add.

        Raises:
            ValueError: if missing any metadata
        """
        LOG.debug(f"Adding data: {ntwk}")
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
        """Get a subset of data filtered by **kwargs.

        Examples:
            Getting the Networks for the Vertical polraization azimuth=30deg

            >>> ntwk_model.get_data({
                    'polarization': 'Vertical',
                    'azimuth': 30
                })

        Arguments:
            **kwargs: Dictionary of filter values

        Returns:
            skrf.NetworkSet: subset of filtered data
        """
        criteria = {key: val for key, val in kwargs.items() if val is not None}
        LOG.debug(f"Getting data with {criteria=}")
        try:
            return self._data.sel(criteria)
        except IndexError:
            # An IndexError happens when we don't have data.
            # In that case, just return an empty networkset
            return skrf.NetworkSet()

    def load_data(self, data: skrf.NetworkSet) -> None:
        """Load new data into the model and populate the relevant properties.

        Argumnets:
            data: new data to load
        """
        self._data = data
        metadata = self._data.params_values
        self._azimuths = set(metadata['azimuth'])
        self._elevations = set(metadata['elevation'])
        self._polarizations = set(metadata['polarization'])
        self.data_loaded.emit()

    def mags(
        self,
        polarization: str,
        frequency: Optional[str] = None,
        azimuth: Optional[float] = None,
        elevation: Optional[float] = None,
    ) -> np.ndarray:
        """Get magnitudes (dB) of a subset of data.

        Arguments that are none are interpreted as requesting *all* values.

        Arguments:
            polarization: the desired polarization (must match the label it was
                given in measurement)
            frequency: the frequency of interest
            azimuth: the azimuth of interest
            elevation: the elevation of interest

        Returns:
            Array of magnitudes dB of the requested data
        """
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
            return np.array([ntwk[frequency].s_db for ntwk in subset])  # type: ignore
        else:
            return np.array([ntwk.s_db for ntwk in subset])  # type: ignore

    def data(self) -> skrf.NetworkSet:
        return self._data
