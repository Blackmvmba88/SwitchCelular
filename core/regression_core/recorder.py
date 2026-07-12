from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json

from core.diagnostics_core.tracing import EndToEndTrace, RegressionMetrics, StageTrace, build_regression_metrics


@dataclass(slots=True)
class MotionTrace:
    id: str
    frames: list[dict[str, object]] = field(default_factory=list)
    trace: EndToEndTrace | None = None
    metrics: RegressionMetrics | None = None


def record_stage(trace: MotionTrace, stage: str, started_ns: int, finished_ns: int, **metadata: object) -> MotionTrace:
    end_to_end = trace.trace or EndToEndTrace(trace_id=trace.id)
    end_to_end.stages.append(StageTrace(stage=stage, started_ns=started_ns, finished_ns=finished_ns, metadata=dict(metadata)))
    trace.trace = end_to_end
    return trace


def finalize_trace(trace: MotionTrace, drift_score: float = 0.0) -> MotionTrace:
    if trace.trace is None:
        trace.trace = EndToEndTrace(trace_id=trace.id)
    trace.metrics = build_regression_metrics([stage.latency_ms for stage in trace.trace.stages], drift_score)
    return trace


def write_trace(trace: MotionTrace, path: Path) -> Path:
    payload = {
        "id": trace.id,
        "frames": trace.frames,
        "trace": None
        if trace.trace is None
        else {
            "trace_id": trace.trace.trace_id,
            "warnings": trace.trace.warnings,
            "stages": [
                {
                    "stage": stage.stage,
                    "started_ns": stage.started_ns,
                    "finished_ns": stage.finished_ns,
                    "latency_ms": stage.latency_ms,
                    "metadata": stage.metadata,
                }
                for stage in trace.trace.stages
            ],
        },
        "metrics": None
        if trace.metrics is None
        else {
            "p50_latency_ms": trace.metrics.p50_latency_ms,
            "p95_latency_ms": trace.metrics.p95_latency_ms,
            "p99_latency_ms": trace.metrics.p99_latency_ms,
            "drift_score": trace.metrics.drift_score,
            "sample_count": trace.metrics.sample_count,
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path
