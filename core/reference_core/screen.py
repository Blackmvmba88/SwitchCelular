from __future__ import annotations

from dataclasses import dataclass

from core.aim_core.frame import AimFrame

from .sources import ReferenceState, apply_reference_correction


@dataclass(slots=True)
class ScreenReference:
    visible: bool
    confidence: float
    screen_center: tuple[float, float] = (0.0, 0.0)
    screen_scale: float = 1.0


def build_screen_reference(reference: ScreenReference) -> ReferenceState:
    if not reference.visible:
        return ReferenceState(source="screen_reference", confidence=0.0, correction_applied=False, reference_vector=None)
    x, y = reference.screen_center
    vector = (x * reference.screen_scale, y * reference.screen_scale, 1.0)
    return ReferenceState(
        source="screen_reference",
        confidence=max(0.0, min(1.0, reference.confidence)),
        correction_applied=True,
        reference_vector=vector,
    )


def apply_screen_reference(aim_frame: AimFrame, reference: ScreenReference) -> tuple[AimFrame, ReferenceState]:
    return apply_reference_correction(aim_frame, build_screen_reference(reference))
