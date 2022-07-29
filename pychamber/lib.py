import cloudpickle as pickle

from pychamber.classes.network_model import NetworkModel


def load(path: str) -> NetworkModel:
    with open(path, "rb") as ff:
        data = pickle.load(ff)

    return data
