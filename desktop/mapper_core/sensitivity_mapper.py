from __future__ import annotations


def apply_sensitivity(dx: float, dy: float, sensitivity_x: float, sensitivity_y: float) -> tuple[float, float]:
    return dx * sensitivity_x, dy * sensitivity_y
