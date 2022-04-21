from typing import Optional

from quantiphy import (
    IncompatiblePreferences,
    InvalidNumber,
    InvalidRecognizer,
    Quantity,
    UnknownConversion,
    UnknownScaleFactor,
)


def to_freq(f: str) -> Optional[Quantity]:
    try:
        ret = Quantity(f)
        if ret.units != 'Hz':
            return None
        else:
            return ret
    except (
        IncompatiblePreferences,
        InvalidNumber,
        InvalidRecognizer,
        UnknownConversion,
        UnknownScaleFactor,
    ):
        return None
