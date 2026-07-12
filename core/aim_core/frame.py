from __future__ import annotations

from dataclasses import dataclass

from core.fusion_core.quaternion import Quaternion


@dataclass(slots=True)
class AimFrame:
    timestamp_ns: int
    quaternion: Quaternion
    forward_vector: tuple[float, float, float]
    confidence: float
    drift: float
    reference_state: dict[str, object]


def normalize_vector(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = vector
    magnitude = (x * x + y * y + z * z) ** 0.5 or 1.0
    return (x / magnitude, y / magnitude, z / magnitude)


def quaternion_to_forward_vector(quaternion: Quaternion) -> tuple[float, float, float]:
    # Simple canonical forward vector estimate for the first implementation.
    x = 2.0 * (quaternion.x * quaternion.z + quaternion.w * quaternion.y)
    y = 2.0 * (quaternion.y * quaternion.z - quaternion.w * quaternion.x)
    z = 1.0 - 2.0 * (quaternion.x * quaternion.x + quaternion.y * quaternion.y)
    return normalize_vector((x, y, z))
