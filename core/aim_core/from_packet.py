from __future__ import annotations

from core.fusion_core import Quaternion
from core.protocol_core import MotionPacket

from .frame import AimFrame, quaternion_to_forward_vector


def aim_frame_from_motion_packet(packet: MotionPacket) -> AimFrame:
    """Convert a canonical motion packet into the aim layer without game logic."""
    raw = packet.orientation
    quaternion = Quaternion(
        w=float(raw["w"]),
        x=float(raw["x"]),
        y=float(raw["y"]),
        z=float(raw["z"]),
    )
    magnitude = (
        quaternion.w * quaternion.w
        + quaternion.x * quaternion.x
        + quaternion.y * quaternion.y
        + quaternion.z * quaternion.z
    ) ** 0.5
    if magnitude <= 1e-9:
        raise ValueError("motion packet contains a zero-length quaternion")

    quaternion = Quaternion(
        w=quaternion.w / magnitude,
        x=quaternion.x / magnitude,
        y=quaternion.y / magnitude,
        z=quaternion.z / magnitude,
    )
    has_orientation = "CAPABILITY_ORIENTATION" in packet.capabilities
    return AimFrame(
        timestamp_ns=packet.timestamp_ns,
        quaternion=quaternion,
        forward_vector=quaternion_to_forward_vector(quaternion),
        confidence=1.0 if has_orientation else 0.5,
        drift=0.0,
        reference_state={
            "source": "motion_packet_v1",
            "sequence": packet.sequence,
        },
    )
