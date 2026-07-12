from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiagnosticsFrame:
    timestamp_ns: int
    sample_rate_hz: float
    latency_ms: float
    jitter_ms: float
    packet_loss: float
    drift_score: float
    signal_quality: str
