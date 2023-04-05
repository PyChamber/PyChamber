from pychamber import positioner

from .diamond.d6050 import Diamond_D6050
from .example.example import ExamplePositioner


def initialize() -> None:
    positioner.register("Diamond Eng.", "D6050", Diamond_D6050)
    positioner.register("Example", "Example Positioner", ExamplePositioner)
