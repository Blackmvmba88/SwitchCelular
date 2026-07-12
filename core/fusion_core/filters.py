from __future__ import annotations


def smooth_value(previous: float, current: float, alpha: float) -> float:
    alpha = max(0.0, min(1.0, alpha))
    return previous * alpha + current * (1.0 - alpha)
