from __future__ import annotations

from dataclasses import dataclass, replace

from core.diagnostics_core.tracing import RegressionMetrics
from core.profile_core.profile import Profile


@dataclass(slots=True)
class CalibrationRecommendation:
    sensitivity_yaw: float
    sensitivity_pitch: float
    smoothing_alpha: float
    deadzone_yaw: float
    deadzone_pitch: float
    reason: str


def tune_profile_from_metrics(profile: Profile, metrics: RegressionMetrics) -> tuple[Profile, CalibrationRecommendation]:
    motion = dict(profile.motion)
    sensitivity = dict(motion.get("sensitivity", {}))
    smoothing = dict(motion.get("smoothing", {}))
    deadzone = dict(motion.get("deadzone", {}))

    latency_factor = max(0.85, min(1.15, 1.0 - (metrics.p95_latency_ms / 100.0)))
    drift_factor = max(0.85, min(1.15, 1.0 - (metrics.drift_score * 0.1)))

    sensitivity_yaw = float(sensitivity.get("yaw", 1.0)) * latency_factor
    sensitivity_pitch = float(sensitivity.get("pitch", 1.0)) * latency_factor
    smoothing_alpha = min(0.95, max(0.1, float(smoothing.get("alpha", 0.5)) * drift_factor))
    deadzone_yaw = max(0.0, float(deadzone.get("yaw", 0.0)) + (metrics.p95_latency_ms / 500.0))
    deadzone_pitch = max(0.0, float(deadzone.get("pitch", 0.0)) + (metrics.p95_latency_ms / 500.0))

    tuned_profile = replace(
        profile,
        motion={
            **motion,
            "sensitivity": {"yaw": sensitivity_yaw, "pitch": sensitivity_pitch},
            "smoothing": {"alpha": smoothing_alpha},
            "deadzone": {"yaw": deadzone_yaw, "pitch": deadzone_pitch},
        },
    )
    recommendation = CalibrationRecommendation(
        sensitivity_yaw=sensitivity_yaw,
        sensitivity_pitch=sensitivity_pitch,
        smoothing_alpha=smoothing_alpha,
        deadzone_yaw=deadzone_yaw,
        deadzone_pitch=deadzone_pitch,
        reason="derived from end-to-end latency and drift metrics",
    )
    return tuned_profile, recommendation
