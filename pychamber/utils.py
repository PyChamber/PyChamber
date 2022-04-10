import re

UNIT_REGEXP = re.compile(
    r"(?P<val>\d+\.?\d*)(?:\s*)?(?P<prefix>[GMk])?(?:[hH]z)?"  # noqa: E501
)

MULT_BY_PREFIX = {
    'G': 1e9,
    'M': 1e6,
    'k': 1e3,
}


def parse_freq_str(input: str) -> float:
    """Parse a string with SI prefixes and units and return a float.

    Currently only the following SI prefixes:
        - G (Giga)  1e9,
        - M (Mega)  1e6,
        - k (kilo)  1e3,

    and the following SI units:
        - Hz or hertz

    are supported.

    You cannot have a prefix if you use the full unit name. The full name should
    be used for example with e.g. `"1.5 meter"`, `"2 second"`, `"10 hertz"`.

    The space between quantity (the number) and the prefix/unit is optional.

    Args:
        input: String to parse

    Returns:
        A float equal to the string
    """
    try:
        return float(input)
    except ValueError:
        match = re.match(UNIT_REGEXP, input)
        if match is None:
            raise ValueError(f"Invalid string: {input}")
        else:
            return MULT_BY_PREFIX[match.group("prefix")] * float(match.group("val"))
