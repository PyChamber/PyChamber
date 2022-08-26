from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import os
    import skrf
    from typing import Union

import cloudpickle as pickle


def load(fname: Union[str, os.PathLike]) -> skrf.NetworkSet:
    with open(fname, "rb") as ff:
        ntwkset = pickle.load(ff)

    return ntwkset
