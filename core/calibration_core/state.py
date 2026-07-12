from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CalibrationState:
    center_yaw: float = 0.0
    center_pitch: float = 0.0
    center_roll: float = 0.0
    sensitivity_x: float = 1.0
    sensitivity_y: float = 1.0
    deadzone_x: float = 0.0
    deadzone_y: float = 0.0
    drift_compensation: bool = True
