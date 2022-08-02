"""An extension of scikit-rf's NetworkSet.

This module defines the NetworkModel class which extends scikit-rf's NetworkSet
to provide helpful functions relevant to chamber measurements.

When taking measurements, each polarization will be a NetworkModel.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from skrf.network import Network
from skrf.networkSet import NetworkSet

from pychamber.classes.logger import log


class NetworkModel(NetworkSet):
    """Set of Networks that represent one meausurement.

    Extends scikit-rf's NetworkSet to provide helper functions relevant to
    chamber measurements.

    Attributes:
        freqs: List of frequencies in the set
        azimuths: List of azimuths in the set
        elevations: List of elevations in the set
    """

    @property
    def freqs(self) -> np.ndarray:
        """The list of frequencies contained in the set."""
        if len(self) == 0:
            return np.array([])
        else:
            return self[0].frequency.f  # type: ignore

    @property
    def azimuths(self) -> np.ndarray:
        """The list of azimuths contained in the set."""
        if len(self) == 0:
            return np.array([])
        else:
            return np.array(
                [n.params['azimuth'] for n in self.sel({'elevation': 0})]  # type: ignore
            ).reshape(-1, 1)

    @property
    def elevations(self) -> np.ndarray:
        """The list of elevations contained in the set."""
        if len(self) == 0:
            return np.array([])
        else:
            return np.array(
                [n.params['elevation'] for n in self.sel({'azimuth': 0})]  # type: ignore
            ).reshape(-1, 1)

    def __str__(self) -> str:
        if len(self) == 0:
            return "Empty NetworkModel"
        else:
            return (
                f"NetworkModel(Frequency: {self[0].frequency},"  # type: ignore
                f"Azimuths: {len(self.azimuths)} points,"
                f"Elevations: {len(self.elevations)} points)"
            )

    def mags(
        self,
        freq: Optional[str] = None,
        azimuth: Optional[float] = None,
        elevation: Optional[float] = None,
    ) -> np.ndarray:
        """Fetches data filtered by the arguments provided.

        Any argument not passed will be interpreted as requesting all values of
        that type.

        Example:
        ```py
        import pychamber
        data = pychamber.load("/path/to/data")
        # data = {"Vertical": NetworkModel, "Horizontal": NetworkModel}
        vert = data["Vertical"]
        # Retrieve the primary azimuth cut-plane (theta=90) for 2.45GHz
        cut = vert.mags(freq="2.45 GHz", elevation=0)
        ```

        This example makes clear that theta in the traditional sense is
        different from elevation. Elevation is dependent on the positioner, but
        for the D6050 for example, if boresight is taken as (0 azimuth, 0
        elevation), then elevation is the angle of rotation of the
        secondary-axis.

        Args:
            freq: Frequency of interest
            azimuth: Azimuth of interest
            elevation: Elevation of interest
        """
        log.debug("Fetching Mags")
        if len(self) == 0:
            return np.array([])
        else:
            params = dict()
            if azimuth is not None:
                params['azimuth'] = azimuth
            if elevation is not None:
                params['elevation'] = elevation

            log.debug(f"{params=}")
            if freq:
                return np.array([n[freq].s_db for n in self.sel(params)]).reshape(
                    -1, 1
                )  # type: ignore
            else:
                return self.sel(params)[0].s_db.reshape(-1, 1)  # type: ignore

    def append(self, ntwk: Network) -> NetworkModel:
        log.debug("Appending to network model")
        ret = NetworkModel(list(self) + [ntwk])  # type: ignore
        log.debug(f"{ret=}")
        return ret
