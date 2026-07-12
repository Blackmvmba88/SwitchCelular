from __future__ import annotations


def apply_deadzone(dx: float, dy: float, deadzone_x: float, deadzone_y: float) -> tuple[float, float]:
    if abs(dx) < deadzone_x:
        dx = 0.0
    if abs(dy) < deadzone_y:
        dy = 0.0
    return dx, dy
