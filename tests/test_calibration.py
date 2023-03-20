import numpy as np
import pytest
import skrf

from pychamber.calibration import Calibration


@pytest.fixture(scope="module")
def example_calibration():
    f = skrf.Frequency(1, 10, 51, "ghz")
    s = np.ones((51, 1, 1)) * 10
    polarizations = ["vertical", "horizontal", "rhcp"]

    ntwks = [skrf.Network(name=pol, frequency=f, s=s) for pol in polarizations]

    return Calibration(networks=ntwks)


def test_calibration_creation():
    f = skrf.Frequency(1, 10, 51, "ghz")
    s = np.ones((51, 1, 1))
    polarizations = ["vertical", "horizontal"]

    ntwks = [skrf.Network(name=pol, frequency=f, s=s) for pol in polarizations]

    test = Calibration(networks=ntwks)
    assert len(test._data) == 2
    assert test.polarizations == polarizations

    test = Calibration(networks=skrf.NetworkSet(ntwks))
    assert len(test._data) == 2
    assert test.polarizations == polarizations


def test_calibration_creation_raises_on_bad_input():
    with pytest.raises(TypeError):
        Calibration(None)


def test_getitem(example_calibration):
    test = example_calibration["vertical"]
    assert isinstance(test, skrf.Network)
    assert test.name == "vertical"


def test_apply_to(example_calibration, example_result):
    calibrated = example_calibration.apply_to(example_result)
    assert all(elem == 20 for elem in calibrated[0].s_db.reshape((-1,)))


def test_apply_to_missing_polarizations_raises_exception(example_calibration, example_result):
    ntwk_list = example_calibration._data.ntwk_set
    ntwk_list.remove(example_calibration["vertical"])
    cal = Calibration(ntwk_list)
    with pytest.raises(ValueError):
        cal.apply_to(example_result)
