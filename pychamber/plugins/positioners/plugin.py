from pychamber import positioner

from .diamond.d6050 import Diamond_D6050


def initialize() -> None:
    positioner.register("Diamond Eng.", "D6050", Diamond_D6050)
