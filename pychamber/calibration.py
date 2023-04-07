from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import skrf


class Calibration:
    def __init__(self, networks: list[skrf.Network] | skrf.NetworkSet, notes: list[str] | None = None) -> None:
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
        return [ntwk.name for ntwk in self._data]

    @property
    def networks(self) -> skrf.NetworkSet:
        return self._data

    @property
    def frequency(self) -> skrf.Frequency:
        return self._data[0].frequency

    def save(self, path: str | Path) -> None:
        self._data.write_mdif(path, comments=self.notes)

    @classmethod
    def load(cls, path: str | Path) -> Calibration:
        cal = skrf.NetworkSet.from_mdif(str(path))
        notes = "\n".join(cal.comments.split("@")[1:-1])

        return Calibration(cal, notes)

    def get_polarization(self, polarization: str) -> skrf.Network:
        return self._data.sel({'polarization': polarization})[0]