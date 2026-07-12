from __future__ import annotations

from dataclasses import dataclass, field

from core.aim_core.frame import AimFrame
from core.profile_core.profile import Profile


@dataclass(slots=True)
class ContextRecommendation:
    profile_id: str | None = None
    tuning: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0


def recommend_context(aim_frame: AimFrame, profile: Profile | None = None) -> ContextRecommendation:
    profile_id = profile.id if profile else None
    tuning: dict[str, float] = {}
    if profile is not None:
        motion = profile.motion
        sensitivity = motion.get("sensitivity", {})
        if isinstance(sensitivity, dict):
            tuning["sensitivity_yaw"] = float(sensitivity.get("yaw", 1.0))
            tuning["sensitivity_pitch"] = float(sensitivity.get("pitch", 1.0))
        smoothing = motion.get("smoothing", {})
        if isinstance(smoothing, dict):
            tuning["smoothing_alpha"] = float(smoothing.get("alpha", 0.0))
    if aim_frame.confidence < 0.5:
        tuning["increase_deadzone"] = 1.0
    return ContextRecommendation(
        profile_id=profile_id,
        tuning=tuning,
        confidence=round(min(1.0, max(0.0, aim_frame.confidence)), 6),
    )
