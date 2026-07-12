from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SensorSample:
    timestamp_ns: int
    sensor: str
    x: float
    y: float
    z: float
    accuracy: float | None = None
    status: str = "ok"


@dataclass(slots=True)
class AndroidSensorEvent:
    timestamp_ns: int
    sensor_type: str
    values: tuple[float, float, float]
    accuracy: float | None = None
    status: str = "ok"
    device_model: str = "android"
    sample_rate_hz: float | None = None
