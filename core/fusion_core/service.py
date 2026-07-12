from __future__ import annotations

from dataclasses import dataclass
from math import atan2, sqrt

from core.sensor_core.models import SensorSample

from .filters import smooth_value
from .quaternion import Quaternion


@dataclass(slots=True)
class FusionFrame:
    timestamp_ns: int
    quaternion: Quaternion
    yaw: float
    pitch: float
    roll: float
    confidence: float


def _normalize_quaternion(quaternion: Quaternion) -> Quaternion:
    magnitude = sqrt(quaternion.w**2 + quaternion.x**2 + quaternion.y**2 + quaternion.z**2) or 1.0
    return Quaternion(
        w=quaternion.w / magnitude,
        x=quaternion.x / magnitude,
        y=quaternion.y / magnitude,
        z=quaternion.z / magnitude,
    )


def _quaternion_from_samples(gyro: SensorSample | None, accel: SensorSample | None, magnetometer: SensorSample | None) -> Quaternion:
    if gyro is None:
        return Quaternion(1.0, 0.0, 0.0, 0.0)

    yaw = gyro.z * 0.01
    pitch = gyro.y * 0.01
    roll = gyro.x * 0.01
    if accel is not None:
        pitch += atan2(-accel.x, sqrt(accel.y**2 + accel.z**2)) * 0.25
        roll += atan2(accel.y, accel.z if accel.z else 1.0) * 0.25
    if magnetometer is not None:
        yaw += atan2(magnetometer.y, magnetometer.x if magnetometer.x else 1.0) * 0.1
    return _normalize_quaternion(Quaternion(w=1.0, x=roll, y=pitch, z=yaw))


def fuse_orientation(gyro: SensorSample | None, accel: SensorSample | None, magnetometer: SensorSample | None, timestamp_ns: int) -> FusionFrame:
    quaternion = _quaternion_from_samples(gyro, accel, magnetometer)
    yaw = quaternion.z
    pitch = quaternion.y
    roll = quaternion.x
    confidence = 1.0
    if accel is None:
        confidence -= 0.15
    if gyro is None:
        confidence -= 0.4
    if magnetometer is None:
        confidence -= 0.05
    return FusionFrame(
        timestamp_ns=timestamp_ns,
        quaternion=quaternion,
        yaw=yaw,
        pitch=pitch,
        roll=roll,
        confidence=max(0.0, round(confidence, 6)),
    )


def fuse_samples(samples: list[SensorSample]) -> FusionFrame:
    gyro = next((sample for sample in samples if sample.sensor == "gyroscope"), None)
    accel = next((sample for sample in samples if sample.sensor == "accelerometer"), None)
    magnetometer = next((sample for sample in samples if sample.sensor == "magnetometer"), None)
    timestamp_ns = max((sample.timestamp_ns for sample in samples), default=0)
    return fuse_orientation(gyro, accel, magnetometer, timestamp_ns)
