import unittest

import numpy as np
import pytest
import skrf

from pychamber.experiment_result import ExperimentResult

from .dummyserial import Serial


@pytest.fixture
def test_case():
    """Useful to use unittest methods like assertCountEqual"""
    return unittest.TestCase()


@pytest.fixture(scope="module")
def monkeymodule():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="module")
def DummySerial():
    def _dummyserial(port, baudrate, timeout, expected_responses, raise_on_unrecognized):
        return Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            expected_responses=expected_responses,
            raise_on_unrecognized=raise_on_unrecognized,
        )

    return _dummyserial


@pytest.fixture(scope="module")
def example_result():
    f = skrf.Frequency(1, 10, 51, "ghz")
    s = np.ones((51, 1, 1)) * 100
    azimuths = np.arange(0, 90.0, 12.5)
    elevations = np.arange(0, 45.0, 12.5)

    ntwks = []
    for az in azimuths:
        for el in elevations:
            ntwks.append(
                skrf.Network(frequency=f, s=s, params={"polarization": "horizontal", "azimuth": az, "elevation": el})
            )
            ntwks.append(
                skrf.Network(frequency=f, s=s, params={"polarization": "vertical", "azimuth": az, "elevation": el})
            )

    return ExperimentResult(ntwks)
