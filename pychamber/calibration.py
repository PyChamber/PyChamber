import skrf

from pychamber.experiment_result import ExperimentResult


class Calibration:
    def __init__(self, networks: list[skrf.Network] | skrf.NetworkSet, notes: str = "") -> None:
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

    def apply_to(self, measurements: ExperimentResult) -> ExperimentResult:
        for pol in measurements.polarizations:
            if pol not in self.polarizations:
                raise ValueError(f"Cannot apply this calibration. It does not contain data for polarization: {pol}.")

        calibrated_result_ntwks = []
        for cal in self._data:
            try:
                uncalibrated = measurements.get(polarization=cal.name)
            except KeyError:
                continue

            calibrated = uncalibrated / cal
            calibrated_result_ntwks += calibrated.ntwk_set

        return ExperimentResult(calibrated_result_ntwks)
