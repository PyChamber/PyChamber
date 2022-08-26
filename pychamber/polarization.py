"""Defines the Polarization class."""
from dataclasses import dataclass


@dataclass
class Polarization:
    """A single polarization with name and parameter.

    A parameter is the actual value that is being measured e.g. S21
    """

    label: str
    param: str
