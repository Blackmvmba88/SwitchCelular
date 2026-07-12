from __future__ import annotations

from core.fusion_core.filters import smooth_value


def apply_smoothing(previous: tuple[float, float] | None, current: tuple[float, float], alpha: float) -> tuple[float, float]:
    if previous is None:
        return current
    return (
        smooth_value(previous[0], current[0], alpha),
        smooth_value(previous[1], current[1], alpha),
    )
