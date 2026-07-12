from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median
from time import perf_counter_ns
from collections.abc import Callable

from .tracing import RegressionMetrics, build_regression_metrics


@dataclass(slots=True)
class BenchmarkRun:
    name: str
    samples_ms: list[float] = field(default_factory=list)
    metrics: RegressionMetrics | None = None
    warnings: list[str] = field(default_factory=list)

    def summarize(self, drift_score: float = 0.0) -> RegressionMetrics:
        self.metrics = build_regression_metrics(self.samples_ms, drift_score)
        return self.metrics

    @property
    def median_latency_ms(self) -> float:
        return median(self.samples_ms) if self.samples_ms else 0.0


def benchmark_pipeline(name: str, iterations: int, runner: Callable[[], object], drift_score: float = 0.0) -> BenchmarkRun:
    samples_ms: list[float] = []
    for _ in range(max(1, iterations)):
        started_ns = perf_counter_ns()
        runner()
        finished_ns = perf_counter_ns()
        samples_ms.append((finished_ns - started_ns) / 1_000_000.0)
    run = BenchmarkRun(name=name, samples_ms=samples_ms)
    run.summarize(drift_score=drift_score)
    return run
