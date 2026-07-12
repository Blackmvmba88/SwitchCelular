"""Diagnostics and observability."""

from .benchmark import BenchmarkRun, benchmark_pipeline
from .metrics import DiagnosticsFrame
from .tracing import EndToEndTrace, RegressionMetrics, StageTrace, build_regression_metrics
from core.regression_core import MotionTrace, finalize_trace, record_stage, write_trace

__all__ = [
    "BenchmarkRun",
    "DiagnosticsFrame",
    "EndToEndTrace",
    "MotionTrace",
    "RegressionMetrics",
    "StageTrace",
    "benchmark_pipeline",
    "build_regression_metrics",
    "finalize_trace",
    "record_stage",
    "write_trace",
]
