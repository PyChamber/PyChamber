from __future__ import annotations

import pathlib

import skrf


class ExperimentResult(skrf.NetworkSet):
    def __init__(self, ntwk_set: list | dict | skrf.NetworkSet, name: str = None):
        if isinstance(ntwk_set, skrf.NetworkSet):
            super().__init__(ntwk_set.ntwk_set, name)
        else:
            super().__init__(ntwk_set, name)

        if not self.has_params():
            raise ValueError("Not all networks have the same parameters. Metadata must match *exactly*")

    @classmethod
    def load(cls, path: str | pathlib.Path) -> ExperimentResult:
        ns = skrf.NetworkSet.from_mdif(str(path))
        return cls(ns.ntwk_set)

    def save(self, path: str | pathlib.Path) -> None:
        # Saving to MDIF fails if networks dont have a name, so just set the names to ""
        for ntwk in self.ntwk_set:
            ntwk.name = ""

        # use .sel to convert back to a skrf.NetworkSet. Fails because we overwrote __getitem__
        self.sel().write_mdif(path)

    def get_unique_param_vals(self, param: str) -> list[any]:
        try:
            return list(set(self.params_values[param]))
        except KeyError:
            return []

    @property
    def frequencies(self) -> skrf.Frequency:
        return self.ntwk_set[0].frequency

    @property
    def polarizations(self) -> list[str]:
        return self.get_unique_param_vals("polarization")

    @property
    def azimuths(self) -> list[int | float]:
        return sorted(self.get_unique_param_vals("azimuth"))

    @property
    def elevations(self) -> list[int | float]:
        return sorted(self.get_unique_param_vals("elevation"))

    def get(
        self,
        *,
        azimuth: int | float | None = None,
        elevation: int | float | None = None,
        polarization: str | None = None,
    ) -> skrf.Network | ExperimentResult:
        if azimuth is not None and azimuth not in self.azimuths:
            raise KeyError(f"No results exist for azimuth: {azimuth}")
        if elevation is not None and elevation not in self.elevations:
            raise KeyError(f"No results exist for elevation: {elevation}")
        if polarization is not None and polarization not in self.polarizations:
            raise KeyError(f"No results exist for polarization: '{polarization}'")

        sel_params = {}
        if azimuth is not None:
            sel_params |= {"azimuth": azimuth}
        if elevation is not None:
            sel_params |= {"elevation": elevation}
        if polarization is not None:
            sel_params |= {"polarization": polarization}
        subset = self.sel(sel_params)

        # If we request a single item, it should be returned as a skrf.Network
        if len(subset) == 1:
            return subset[0]

        return ExperimentResult(subset)
