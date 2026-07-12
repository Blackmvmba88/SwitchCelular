from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from core.aim_core.frame import AimFrame

from .sources import ReferenceState, apply_reference_correction


@dataclass(slots=True)
class VisionDetection:
    monitor_visible: bool
    confidence: float
    center_offset_px: tuple[float, float] = (0.0, 0.0)
    screen_size_inches: float | None = None
    distance_cm: float | None = None


def build_vision_reference(detection: VisionDetection) -> ReferenceState:
    if not detection.monitor_visible:
        return ReferenceState(source="vision_reference", confidence=0.0, correction_applied=False, reference_vector=None)
    x_offset, y_offset = detection.center_offset_px
    vector = (x_offset / 1000.0, y_offset / 1000.0, 1.0)
    magnitude = sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) or 1.0
    return ReferenceState(
        source="vision_reference",
        confidence=max(0.0, min(1.0, detection.confidence)),
        correction_applied=True,
        reference_vector=(vector[0] / magnitude, vector[1] / magnitude, vector[2] / magnitude),
    )


def apply_vision_reference(aim_frame: AimFrame, detection: VisionDetection) -> tuple[AimFrame, ReferenceState]:
    return apply_reference_correction(aim_frame, build_vision_reference(detection))
