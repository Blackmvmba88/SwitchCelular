from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from core.aim_core.frame import AimFrame


@dataclass(slots=True)
class ReferenceState:
    source: str
    confidence: float
    correction_applied: bool = False
    reference_vector: tuple[float, float, float] | None = None


def apply_reference_correction(aim_frame: AimFrame, reference: ReferenceState | None) -> tuple[AimFrame, ReferenceState]:
    if reference is None:
        reference = ReferenceState(source="imu_reference", confidence=0.0, correction_applied=False, reference_vector=None)
        return aim_frame, reference

    corrected_confidence = max(0.0, min(1.0, (aim_frame.confidence + reference.confidence) / 2.0))
    correction_scale = 1.0 - min(0.2, reference.confidence * 0.1)
    x, y, z = aim_frame.forward_vector
    if reference.reference_vector is not None:
        rx, ry, rz = reference.reference_vector
        x = (x + rx) / 2.0
        y = (y + ry) / 2.0
        z = (z + rz) / 2.0
    vector = (x * correction_scale, y * correction_scale, z)
    magnitude = sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) or 1.0
    corrected_frame = AimFrame(
        timestamp_ns=aim_frame.timestamp_ns,
        quaternion=aim_frame.quaternion,
        forward_vector=(vector[0] / magnitude, vector[1] / magnitude, vector[2] / magnitude),
        confidence=round(corrected_confidence, 6),
        drift=round(max(0.0, aim_frame.drift - reference.confidence * 0.05), 6),
        reference_state={
            "source": reference.source,
            "confidence": reference.confidence,
            "correction_applied": True,
            "reference_vector": reference.reference_vector,
        },
    )
    return corrected_frame, ReferenceState(
        source=reference.source,
        confidence=reference.confidence,
        correction_applied=True,
        reference_vector=reference.reference_vector,
    )
