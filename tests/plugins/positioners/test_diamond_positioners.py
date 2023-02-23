import functools

import pytest
import serial

from pychamber.plugins.positioners.diamond.d6050 import Diamond_D6050


@pytest.fixture(scope="module")
def dummy_positioner(DummySerial, monkeymodule):
    responses = {
        # Connection test
        b"X0\r": b"x0>\r",
        # Initialization commands
        b"X0N-0cz00\r": b"x0>\r",
        b"Y0N-0cz00\r": b"y0>\r",
        b"X0A2000000000\r": b"x0>\r",
        b"Y0A2000000000\r": b"y0>\r",
        b"X0P3,150,50,10\r": b"x0>\r",
        b"Y0P3,200,50,10\r": b"y0>\r",
        b"X0P1\r": b"x0>\r",
        b"Y0P1\r": b"y0>\r",
        b"X0H4\r": b"x0>\r",
        b"Y0H4\r": b"y0>\r",
        b"X0qmC\r": b"x0>\r",
        b"Y0qmC\r": b"y0>\r",
        b"X0qN-\r": b"x0>\r",
        b"Y0qN-\r": b"y0>\r",
        b"X0qE\r": b"x0>\r",
        b"Y0qE\r": b"y0>\r",
        b"X0B1000\r": b"x0>\r",
        b"Y0B1000\r": b"y0>\r",
        b"X0E5000\r": b"x0>\r",
        b"Y0E8000\r": b"y0>\r",
        b"X0S8\r": b"x0>\r",
        b"Y0S8\r": b"y0>\r",
        b"Y0\r": b"y0>\r",
        # Moves
        b"X0RN+3200\r": b"x0\r",
        b"Y0RN+8000\r": b"y0\r",
        b"X0RN-6400\r": b"x0\r",
        b"Y0RN-16000\r": b"y0\r",
        b"X0RN+9600\r": b"x0>\r",
        b"Y0RN+24000\r": b"y0>\r",
        b"X0RN-19200\r": b"x0>\r",
        b"Y0RN-48000\r": b"y0>\r",
        # Aborts
        b"X0*\r": b"x0>\r",
        b"Y0*\r": b"y0>\r",
        b"Z0*\r": b"z0>\r",
    }
    mock_serial = functools.partial(DummySerial, expected_responses=responses, raise_on_unrecognized=True)
    monkeymodule.setattr(serial, "Serial", mock_serial)

    return Diamond_D6050("test")


def test_zero_az(dummy_positioner):
    dummy_positioner._azimuth = 10
    dummy_positioner.zero_az()
    assert dummy_positioner.azimuth == 0


def test_zero_el(dummy_positioner):
    dummy_positioner._elevation = 10
    dummy_positioner.zero_el()
    assert dummy_positioner.elevation == 0


def test_zero_all(dummy_positioner):
    dummy_positioner._azimuth = 10
    dummy_positioner._elevation = 10
    dummy_positioner.zero_all()
    assert dummy_positioner.azimuth == 0
    assert dummy_positioner.elevation == 0


def test_move_az_relative(dummy_positioner):
    dummy_positioner.zero_all()
    dummy_positioner.move_az_relative(-10.0)
    assert dummy_positioner.azimuth == pytest.approx(-10.0)
    dummy_positioner.move_az_relative(20.0)
    assert dummy_positioner.azimuth == pytest.approx(10.0)


def test_move_el_relative(dummy_positioner):
    dummy_positioner.zero_all()
    dummy_positioner.move_el_relative(-10.0)
    assert dummy_positioner.elevation == pytest.approx(-10.0)
    dummy_positioner.move_el_relative(20.0)
    assert dummy_positioner.elevation == pytest.approx(10.0)


def test_move_az_absolute(dummy_positioner):
    dummy_positioner.zero_all()
    dummy_positioner.move_az_absolute(-30.0)
    assert dummy_positioner.azimuth == pytest.approx(-30.0)
    dummy_positioner.move_az_absolute(30.0)
    assert dummy_positioner.azimuth == pytest.approx(30.0)


def test_move_el_absolute(dummy_positioner):
    dummy_positioner.zero_all()
    dummy_positioner.move_el_absolute(-30.0)
    assert dummy_positioner.elevation == pytest.approx(-30.0)
    dummy_positioner.move_el_absolute(30.0)
    assert dummy_positioner.elevation == pytest.approx(30.0)


def test_az_move_unnecessary(dummy_positioner):
    dummy_positioner.zero_all()
    dummy_positioner.move_az_absolute(0.0)
    assert dummy_positioner.azimuth == pytest.approx(0.0)


def test_el_move_unnecessary(dummy_positioner):
    dummy_positioner.zero_all()
    dummy_positioner.move_el_absolute(0.0)
    assert dummy_positioner.elevation == pytest.approx(0.0)


def test_abort_all(dummy_positioner):
    dummy_positioner.abort_all()
