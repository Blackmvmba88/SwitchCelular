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

    sensitivity = motion.get("sensitivity") if isinstance(motion, dict) else {}
    deadzone = motion.get("deadzone") if isinstance(motion, dict) else {}
    smoothing = motion.get("smoothing") if isinstance(motion, dict) else {}
    recoil = motion.get("recoil") if isinstance(motion, dict) else {}

    def _value(source: object, key: str, default: float) -> float:
        if isinstance(source, dict):
            raw = source.get(key, default)
            return float(raw) if raw is not None else default
        return default

    base_dx = aim_frame.forward_vector[0]
    base_dy = aim_frame.forward_vector[1]
    dx, dy = apply_deadzone(
        base_dx,
        base_dy,
        _value(deadzone, "yaw", 0.0),
        _value(deadzone, "pitch", 0.0),
    )
    dx, dy = apply_sensitivity(
        dx,
        dy,
        _value(sensitivity, "yaw", 1.0),
        _value(sensitivity, "pitch", 1.0),
    )
    alpha = _value(smoothing, "alpha", 0.0)
    dx, dy = apply_smoothing(state.previous_delta, (dx, dy), alpha)
    if isinstance(recoil, dict):
        dx, dy = apply_recoil_compensation(dx, dy, _value(recoil, "x", 0.0), _value(recoil, "y", 0.0))
    state.previous_delta = (dx, dy)
    state.last_profile_id = profile.id
    return AimDelta(dx=dx, dy=dy), state
