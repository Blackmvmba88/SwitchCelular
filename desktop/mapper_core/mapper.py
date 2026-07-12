from __future__ import annotations

from dataclasses import dataclass, field

from core.aim_core.frame import AimFrame
from core.profile_core.profile import Profile

from .deadzone_mapper import apply_deadzone
from .orientation_mapper import AimDelta
from .recoil_mapper import apply_recoil_compensation
from .sensitivity_mapper import apply_sensitivity
from .smoothing_mapper import apply_smoothing


@dataclass(slots=True)
class MapperState:
    previous_delta: tuple[float, float] | None = None
    last_profile_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    fallback_reason: str | None = None


def map_aim_to_delta(
    aim_frame: AimFrame,
    profile: Profile,
    state: MapperState | None = None,
) -> tuple[AimDelta, MapperState]:
    state = state or MapperState()
    motion = profile.motion
    sensitivity = motion.get("sensitivity", {})
    deadzone = motion.get("deadzone", {})
    smoothing = motion.get("smoothing", {})
    recoil = motion.get("recoil", {})

    base_dx = aim_frame.forward_vector[0]
    base_dy = aim_frame.forward_vector[1]
    dx, dy = apply_deadzone(
        base_dx,
        base_dy,
        float(deadzone.get("yaw", 0.0)) if isinstance(deadzone, dict) else 0.0,
        float(deadzone.get("pitch", 0.0)) if isinstance(deadzone, dict) else 0.0,
    )
    dx, dy = apply_sensitivity(
        dx,
        dy,
        float(sensitivity.get("yaw", 1.0)) if isinstance(sensitivity, dict) else 1.0,
        float(sensitivity.get("pitch", 1.0)) if isinstance(sensitivity, dict) else 1.0,
    )
    alpha = float(smoothing.get("alpha", 0.0)) if isinstance(smoothing, dict) else 0.0
    dx, dy = apply_smoothing(state.previous_delta, (dx, dy), alpha)
    if isinstance(recoil, dict):
        dx, dy = apply_recoil_compensation(
            dx,
            dy,
            float(recoil.get("x", 0.0)),
            float(recoil.get("y", 0.0)),
        )
    state.previous_delta = (dx, dy)
    state.last_profile_id = profile.id
    return AimDelta(dx=dx, dy=dy), state
