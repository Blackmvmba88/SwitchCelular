from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median


@dataclass(slots=True)
class StageTrace:
    stage: str
    started_ns: int
    finished_ns: int
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def latency_ms(self) -> float:
        return max(0.0, (self.finished_ns - self.started_ns) / 1_000_000.0)


@dataclass(slots=True)
class EndToEndTrace:
    trace_id: str
    stages: list[StageTrace] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def latency_ms(self) -> float:
        if not self.stages:
            return 0.0
        return (max(stage.finished_ns for stage in self.stages) - min(stage.started_ns for stage in self.stages)) / 1_000_000.0

    def stage_latency_ms(self, stage_name: str) -> float:
        latencies = [stage.latency_ms for stage in self.stages if stage.stage == stage_name]
        return median(latencies) if latencies else 0.0


@dataclass(slots=True)
class RegressionMetrics:
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    drift_score: float
    sample_count: int


def build_regression_metrics(latencies_ms: list[float], drift_score: float) -> RegressionMetrics:
    if not latencies_ms:
        return RegressionMetrics(0.0, 0.0, 0.0, drift_score, 0)
    ordered = sorted(latencies_ms)
    sample_count = len(ordered)

    def percentile(fraction: float) -> float:
        if sample_count == 1:
            return ordered[0]
        index = min(sample_count - 1, max(0, round((sample_count - 1) * fraction)))
        return ordered[index]

    return RegressionMetrics(
        p50_latency_ms=percentile(0.50),
        p95_latency_ms=percentile(0.95),
        p99_latency_ms=percentile(0.99),
        drift_score=drift_score,
        sample_count=sample_count,
    )
