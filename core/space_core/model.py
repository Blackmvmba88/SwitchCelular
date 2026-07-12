from __future__ import annotations

from dataclasses import dataclass
from core.aim_core.frame import AimFrame


@dataclass(slots=True)
class SpaceState:
    monitor_distance_cm: float | None = None
    monitor_orientation_deg: float | None = None
    relative_device_position: str | None = None
    sensor_space: str = "right-handed"
    application_space: str = "screen-relative"
    host_space: str = "desktop-relative"


def project_aim_to_space(aim_frame: AimFrame, space_state: SpaceState | None = None) -> tuple[AimFrame, SpaceState]:
    space_state = space_state or SpaceState()
    distance = space_state.monitor_distance_cm or 85.0
    scale = 1.0 / max(1.0, distance / 85.0)
    x, y, z = aim_frame.forward_vector
    orientation_scale = 1.0 if space_state.monitor_orientation_deg is None else max(0.5, min(1.5, 1.0 + space_state.monitor_orientation_deg / 180.0))
    projected = (x * scale * orientation_scale, y * scale * orientation_scale, z)
    return (
        AimFrame(
            timestamp_ns=aim_frame.timestamp_ns,
            quaternion=aim_frame.quaternion,
            forward_vector=projected,
            confidence=aim_frame.confidence,
            drift=aim_frame.drift,
            reference_state={
                **aim_frame.reference_state,
                "space": {
                    "sensor_space": space_state.sensor_space,
                    "application_space": space_state.application_space,
                    "host_space": space_state.host_space,
                },
            },
        ),
        space_state,
    )
