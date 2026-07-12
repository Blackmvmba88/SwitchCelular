from __future__ import annotations

from core.fusion_core.service import FusionFrame

from .frame import AimFrame, quaternion_to_forward_vector


def build_aim_frame(fusion_frame: FusionFrame, reference_state: dict[str, object] | None = None, drift: float = 0.0) -> AimFrame:
    reference_state = reference_state or {}
    forward_vector = quaternion_to_forward_vector(fusion_frame.quaternion)
    confidence = max(0.0, min(1.0, fusion_frame.confidence - abs(drift) * 0.1))
    return AimFrame(
        timestamp_ns=fusion_frame.timestamp_ns,
        quaternion=fusion_frame.quaternion,
        forward_vector=forward_vector,
        confidence=round(confidence, 6),
        drift=round(drift, 6),
        reference_state=reference_state,
    )
