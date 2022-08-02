""" Defines the general PyChamber api.

Provides helpful methods not found elsewhere in PyChamber. Specifically:

- `load` to load data from previous experiments.
"""
from os import PathLike
from typing import Dict, Union

import cloudpickle as pickle

from pychamber.classes.network_model import NetworkModel

__all__ = ["load"]


def load(path: Union[str, PathLike]) -> Dict[str, NetworkModel]:
    """Loads data from previous experiments.

    Args:
        path: path to data file

    Returns:
        - The dictionary of previous experiment data
    """
    with open(path, "rb") as ff:
        data = pickle.load(ff)

    return data
