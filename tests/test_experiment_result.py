import pathlib

import numpy as np
import pytest
import skrf

from pychamber.experiment_result import ExperimentResult


def test_experiment_result_creation():
    f = skrf.Frequency(1, 10, 11, "ghz")
    s = np.ones((11, 1, 1))
    azimuths = np.arange(0, 90, 10)
    elevations = np.arange(0, 45, 10)

    test = ExperimentResult(
        [
            skrf.Network(frequency=f, s=s, params={"polarization": "vertical", "azimuth": az, "elevation": el})
            for el in elevations
            for az in azimuths
        ]
    )
    assert test is not None


def test_different_params_raises_exception():
    f = skrf.Frequency(1, 10, 11, "ghz")
    s = np.ones((11, 1, 1))

    with pytest.raises(ValueError):
        ntwk_1 = skrf.Network(frequency=f, s=s, params={"polarization": "vertical", "azimuth": 0, "elevation": 0})
        ntwk_2 = skrf.Network(
            frequency=f, s=s, params={"polarization": "vertical", "azimuth": 0, "elevation": 0, "extra": "bad"}
        )
        ExperimentResult([ntwk_1, ntwk_2])


def test_get_unique_param_vals(example_result, test_case):
    assert example_result.get_unique_param_vals("a") == []
    test_case.assertCountEqual(example_result.get_unique_param_vals("polarization"), ["horizontal", "vertical"])


def test_frequencies_property(example_result):
    assert example_result.frequencies == skrf.Frequency(1, 10, 51, "ghz")


def test_polarizations_property(example_result, test_case):
    test_case.assertCountEqual(example_result.polarizations, ["horizontal", "vertical"])


def test_azimuths_property(example_result):
    np.testing.assert_allclose(example_result.azimuths, np.arange(0, 90.0, 12.5))


def test_elevations_property(example_result):
    np.testing.assert_allclose(example_result.elevations, np.arange(0, 45.0, 12.5))


def test_experiment_result_get(example_result):
    az_subset = example_result.get(azimuth=0)
    assert len(az_subset) == (len(example_result.elevations) * len(example_result.polarizations))
    assert isinstance(az_subset, ExperimentResult)
    np.testing.assert_allclose(az_subset.thetas, [0.0])
    np.testing.assert_allclose(az_subset.thetas, example_result.elevations)

    el_subset = example_result.get(elevation=0)
    assert len(el_subset) == (len(example_result.azimuths) * len(example_result.polarizations))
    assert isinstance(el_subset, ExperimentResult)
    np.testing.assert_allclose(el_subset.thetas, example_result.azimuths)
    np.testing.assert_allclose(el_subset.thetas, [0.0])

    specific_value = example_result.get(azimuth=0, elevation=0, polarization="vertical")
    assert isinstance(specific_value, skrf.Network)
    assert specific_value.params["azimuth"] == 0
    assert specific_value.params["elevation"] == 0
    assert specific_value.params["polarization"] == "vertical"

    null_selection = example_result.get()
    assert isinstance(null_selection, ExperimentResult)
    assert null_selection.sort(key=lambda x: x.params["azimuth"]) == example_result.sort(
        key=lambda x: x.params["azimuth"]
    )


def test_getitem_bad_values_raise_exception(example_result):
    with pytest.raises(KeyError):
        example_result.get(azimuth=100)
    with pytest.raises(KeyError):
        example_result.get(azimuth=0, elevation=100)
    with pytest.raises(KeyError):
        example_result.get(elevation=100)
    with pytest.raises(KeyError):
        example_result.get(azimuth=100, elevation=0)


def test_read_write(example_result, tmpdir):
    example_result.name = "test"
    test_path = pathlib.Path(tmpdir) / "result.mdif"
    example_result.save(test_path)
    assert test_path.exists()

    test_load = ExperimentResult.load(test_path)
    assert test_load.sort(key=lambda x: x.params["azimuth"]) == example_result.sort(key=lambda x: x.params["azimuth"])
