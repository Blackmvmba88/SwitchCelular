from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MotionPacket:
    version: int
    sequence: int
    timestamp_ns: int
    orientation: dict[str, float]
    angular_velocity: dict[str, float]
    acceleration: dict[str, float]
    buttons: int = 0
    battery: int = 0
    flags: int = 0
    capabilities: list[str] = field(default_factory=list)
    reserved: list[object] = field(default_factory=list)
    extension_length: int = 0
