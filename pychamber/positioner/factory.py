from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pychamber.positioner.interface import Positioner

_MODELS: dict[str, dict[str, callable[..., Positioner]]] = {}


def available_models() -> dict:
    return _MODELS


def register(manufacturer: str, model: str, constructor: callable[..., Positioner]) -> None:
    if manufacturer not in _MODELS:
        _MODELS[manufacturer] = {}
    _MODELS[manufacturer][model] = constructor


def unregister(manufacturer: str, model: str) -> None:
    if manufacturer not in _MODELS:
        return
    _MODELS[manufacturer].pop(model, None)


def connect(manufacturer: str, model: str, address: str, **kwargs: dict[str, any]) -> Positioner:
    _MODELS[manufacturer][model](address=address, **kwargs)
