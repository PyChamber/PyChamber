from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import skrf


class Calibration:
    """A class containing data for a scalar substitution calibration.

    This kind of calibration is performed when you have an antenna with known
    performance. By measuring the antenna with your experiment setup, you can
    determine the difference between the expected performance and what you
    measure influenced by path loss, cable loss, etc.

    Additionally, notes can be stored with the calibration which can describe
    important contextual information about the setup as it existed when this
    calibration was created.

    When saved, this class is stored as a .mdif file, a text-based file format.
    Comments are stored using a specific delimiter ('@') to allow them to be
    differentiated from other comments in the file. To make it easier to
    differentiate calibrations from other data files, it is suggested to use the
    file extension `.pycal`
    """

    def __init__(self, networks: list[skrf.Network] | skrf.NetworkSet, notes: list[str] | None = None) -> None:
        """
        Args:
            networks: The networks containing the calibration data
            notes: A list of strings containing notes. Each element is another line.
        """
        self.notes = notes
        if isinstance(networks, list):
            self._data = skrf.NetworkSet(networks)
        elif isinstance(networks, skrf.NetworkSet):
            self._data = networks
        else:
            raise TypeError(f"Networks must be a list of skrf.Network or a skrf.NetworkSet. Got {type(networks)}")

    def __getitem__(self, key: str) -> skrf.Network:
        return self._data.to_dict()[key]

    @property
    def polarizations(self) -> list[str]:
        """The names of the polarizations in this calibration."""
        return [ntwk.name for ntwk in self._data]

    @property
    def networks(self) -> skrf.NetworkSet:
        """The underlying networks that comprise this calibration"""
        return self._data

    @property
    def frequency(self) -> skrf.Frequency:
        """The frequency range covered by this calibration"""
        return self._data[0].frequency

    def save(self, path: str | Path) -> None:
        """Save this calibration to a file.

        Args:
            path: Where to save the file
        """
        self._data.write_mdif(path, comments=self.notes)

    @classmethod
    def load(cls, path: str | Path) -> Calibration:
        """Loads a calibration from a file.

        Args:
            path: The file to load

        Returns:
            (Calibration): A new calibration containing the data from the file
        """
        cal = skrf.NetworkSet.from_mdif(str(path))
        notes = "\n".join(cal.comments.split("@")[1:-1])

        return Calibration(cal, notes)

    def get_polarization(self, polarization: str) -> skrf.Network:
        """Get the Network for the named polarization.

        Args:
            polarization: The name of the polarization

        Returns:
            (skrf.network.Network): The data for the requested polarization
        """
        return self._data.sel({"polarization": polarization})[0]
