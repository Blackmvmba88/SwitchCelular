from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Quaternion:
    w: float
    x: float
    y: float
    z: float
