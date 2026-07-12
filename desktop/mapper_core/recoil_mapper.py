from __future__ import annotations


def apply_recoil_compensation(dx: float, dy: float, recoil_x: float = 0.0, recoil_y: float = 0.0) -> tuple[float, float]:
    return dx + recoil_x, dy + recoil_y
