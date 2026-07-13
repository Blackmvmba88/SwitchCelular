from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from math import floor
from pathlib import Path
from typing import Any

from core.diagnostics_core import benchmark_pipeline

from .harness import run_harness

from hypothesis import given, settings, strategies as st


@dataclass(frozen=True)
class CampaignScenario:
    path: Path
    motor_id: str = "virtual-motor-001"
    seed: str = "seed-v1"
    profile: str = "default"


@dataclass(frozen=True)
class CampaignResult:
    scenario: str
    profile: str
    trace_path: str
    trace_hash: str
    frame_count: int
    protocol: str
    avg_latency_ms: float
    avg_confidence: float
    max_latency_ms: float
    min_confidence: float


def _hash_trace(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _trace_metrics(trace_path: Path) -> dict[str, float]:
    data = json.loads(trace_path.read_text(encoding="utf-8"))
    frames = data.get("frames", [])
    if not frames:
        return {"avg_latency_ms": 0.0, "avg_confidence": 0.0, "max_latency_ms": 0.0, "min_confidence": 0.0}
    avg_latency = sum(frame.get("latency_ms", 0) for frame in frames) / len(frames)
    avg_confidence = sum(frame.get("confidence", 0.0) for frame in frames) / len(frames)
    return {
        "avg_latency_ms": round(avg_latency, 6),
        "avg_confidence": round(avg_confidence, 6),
        "max_latency_ms": round(max(frame.get("latency_ms", 0) for frame in frames), 6),
        "min_confidence": round(min(frame.get("confidence", 0.0) for frame in frames), 6),
    }


def _summarize_results(results: list[dict[str, Any]], group_key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for result in results:
        key = result[group_key]
        payload = grouped.setdefault(
            key,
            {
                "count": 0,
                "avg_latency_ms": 0.0,
                "avg_confidence": 0.0,
                "max_latency_ms": 0.0,
                "min_confidence": 1.0,
                "profiles": {},
                "scenarios": {},
            },
        )
        payload["count"] += 1
        payload["avg_latency_ms"] += result.get("avg_latency_ms", 0.0)
        payload["avg_confidence"] += result.get("avg_confidence", 0.0)
        payload["max_latency_ms"] = max(payload["max_latency_ms"], result.get("max_latency_ms", 0.0))
        payload["min_confidence"] = min(payload["min_confidence"], result.get("min_confidence", 1.0))
        payload["profiles"][result["profile"]] = payload["profiles"].get(result["profile"], 0) + 1
        payload["scenarios"][result["scenario"]] = payload["scenarios"].get(result["scenario"], 0) + 1

    for payload in grouped.values():
        count = payload["count"] or 1
        payload["avg_latency_ms"] = round(payload["avg_latency_ms"] / count, 6)
        payload["avg_confidence"] = round(payload["avg_confidence"] / count, 6)
        payload["profiles"] = dict(sorted(payload["profiles"].items()))
        payload["scenarios"] = dict(sorted(payload["scenarios"].items()))
    return dict(sorted(grouped.items()))


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 6)
    rank = (len(ordered) - 1) * percentile
    lower = floor(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 6)


def _build_cross_profile_comparisons(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_scenario: dict[str, dict[str, dict[str, Any]]] = {}
    for result in results:
        by_scenario.setdefault(result["scenario"], {})[result["profile"]] = result
    comparisons: list[dict[str, Any]] = []
    for scenario, profiles in sorted(by_scenario.items()):
        baseline = profiles.get("default")
        if baseline is None:
            continue
        for profile, current in sorted(profiles.items()):
            if profile == "default":
                continue
            comparisons.append(
                {
                    "scenario": scenario,
                    "baseline_profile": "default",
                    "profile": profile,
                    "latency_delta_ms": round(current.get("avg_latency_ms", 0.0) - baseline.get("avg_latency_ms", 0.0), 6),
                    "confidence_delta": round(current.get("avg_confidence", 0.0) - baseline.get("avg_confidence", 0.0), 6),
                    "trace_hash_changed": current.get("trace_hash") != baseline.get("trace_hash"),
                }
            )
    return comparisons


def _build_scenario_rankings(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        by_scenario.setdefault(result["scenario"], []).append(result)

    rankings: dict[str, list[dict[str, Any]]] = {}
    for scenario, scenario_results in sorted(by_scenario.items()):
        ordered_latency = sorted(
            (
                {
                    "profile": result["profile"],
                    "trace_hash": result["trace_hash"],
                    "avg_latency_ms": result.get("avg_latency_ms", 0.0),
                    "avg_confidence": result.get("avg_confidence", 0.0),
                }
                for result in scenario_results
            ),
            key=lambda item: (item["avg_latency_ms"], item["avg_confidence"], item["profile"]),
            reverse=True,
        )
        ordered_confidence = sorted(
            (
                {
                    "profile": result["profile"],
                    "trace_hash": result["trace_hash"],
                    "avg_latency_ms": result.get("avg_latency_ms", 0.0),
                    "avg_confidence": result.get("avg_confidence", 0.0),
                }
                for result in scenario_results
            ),
            key=lambda item: (item["avg_confidence"], item["avg_latency_ms"], item["profile"]),
            reverse=True,
        )
        rankings[scenario] = {
            "worst_latency": ordered_latency[:3],
            "best_confidence": ordered_confidence[:3],
            "p50_latency_ms": _percentile([item.get("avg_latency_ms", 0.0) for item in scenario_results], 0.50),
            "p90_latency_ms": _percentile([item.get("avg_latency_ms", 0.0) for item in scenario_results], 0.90),
            "p95_latency_ms": _percentile([item.get("avg_latency_ms", 0.0) for item in scenario_results], 0.95),
            "p99_latency_ms": _percentile([item.get("avg_latency_ms", 0.0) for item in scenario_results], 0.99),
            "min_confidence": min((item.get("avg_confidence", 0.0) for item in scenario_results), default=0.0),
        }
    return rankings


def run_campaign(scenarios: list[CampaignScenario], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[CampaignResult] = []
    for scenario in scenarios:
        summary = run_harness(
            scenario.path,
            out_dir / "traces",
            motor_id=scenario.motor_id,
            seed=scenario.seed,
            profile=scenario.profile,
        )
        trace_path = Path(summary["trace_path"])
        trace_ref = Path("traces") / trace_path.name
        results.append(
            CampaignResult(
                scenario=summary["scenario"],
                profile=scenario.profile,
                trace_path=trace_ref.as_posix(),
                trace_hash=_hash_trace(trace_path),
                frame_count=summary["frame_count"],
                protocol=summary["protocol"],
                **_trace_metrics(trace_path),
            )
        )

    snapshot = {
        "protocol": "blackmamba.virtual.campaign.v1",
        "result_count": len(results),
        "metrics": {
            "scenario_count": len({scenario.scenario for scenario in results}),
            "profile_count": len({scenario.profile for scenario in results}),
            "avg_latency_ms": round(sum(result.avg_latency_ms for result in results) / len(results), 6) if results else 0.0,
            "avg_confidence": round(sum(result.avg_confidence for result in results) / len(results), 6) if results else 0.0,
        },
        "results": [asdict(result) for result in results],
    }
    (out_dir / "campaign.snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = campaign_report(snapshot)
    (out_dir / "campaign.regression.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_campaign_benchmark(scenarios, out_dir, report)
    return snapshot


def _write_campaign_benchmark(scenarios: list[CampaignScenario], out_dir: Path, report: dict[str, Any]) -> None:
    if not scenarios:
        return

    def _run_first_scenario() -> dict[str, Any]:
        summary = run_harness(
            scenarios[0].path,
            out_dir / "benchmark-traces",
            motor_id=scenarios[0].motor_id,
            seed=scenarios[0].seed,
            profile=scenarios[0].profile,
        )
        return summary

    benchmark = benchmark_pipeline(
        "campaign",
        max(3, len(scenarios)),
        _run_first_scenario,
        drift_score=report.get("metrics", {}).get("drift_score", 0.0),
    )
    payload = {
        "protocol": "blackmamba.virtual.campaign.benchmark.v1",
        "name": benchmark.name,
        "sample_count": len(benchmark.samples_ms),
        "samples_ms": [round(sample, 6) for sample in benchmark.samples_ms],
        "median_latency_ms": round(benchmark.median_latency_ms, 6),
        "metrics": None
        if benchmark.metrics is None
        else {
            "p50_latency_ms": benchmark.metrics.p50_latency_ms,
            "p95_latency_ms": benchmark.metrics.p95_latency_ms,
            "p99_latency_ms": benchmark.metrics.p99_latency_ms,
            "drift_score": benchmark.metrics.drift_score,
            "sample_count": benchmark.metrics.sample_count,
        },
        "report_latency_percentiles_ms": report.get("regression_summary", {}).get("latency_percentiles_ms", {}),
    }
    (out_dir / "campaign.benchmark.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fuzz_scenario(path: Path, seed: str, noise: float = 0.05) -> Path:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["name"] = f'{data["name"]}-fuzz-{seed}'
    for index, frame in enumerate(data.get("frames", [])):
        frame.setdefault("confidence", 1.0)
        frame["confidence"] = max(0.0, round(frame["confidence"] - ((index + len(seed)) % 7) * noise / 10.0, 6))
        frame.setdefault("diagnostics", {})
        frame["diagnostics"]["fuzz_seed"] = seed
    fuzzed = path.with_name(f"{path.stem}.fuzz-{seed}.json")
    fuzzed.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fuzzed


def fuzz_scenario_with_hypothesis(path: Path, seed: str) -> Path:
    data = json.loads(path.read_text(encoding="utf-8"))

    @given(
        latency=st.integers(min_value=0, max_value=40),
        jitter=st.integers(min_value=0, max_value=5),
        noise=st.floats(min_value=0.0, max_value=0.2, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=1, derandomize=True)
    def _mutate(latency: int, jitter: int, noise: float) -> None:
        data["name"] = f'{data["name"]}-hypothesis-{seed}'
        for index, frame in enumerate(data.get("frames", [])):
            frame.setdefault("confidence", 1.0)
            frame.setdefault("diagnostics", {})
            frame["diagnostics"]["fuzz_seed"] = seed
            frame["diagnostics"]["jitter_ms"] = jitter
            frame["diagnostics"]["latency_ms"] = latency
            frame["confidence"] = max(0.0, round(frame["confidence"] - noise * (index + 1) / 10.0, 6))
            frame["latency_ms"] = latency + (index % (jitter + 1) if jitter else 0)

    _mutate()
    fuzzed = path.with_name(f"{path.stem}.hypothesis-{seed}.json")
    fuzzed.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fuzzed


def campaign_report(snapshot: dict[str, Any]) -> dict[str, Any]:
    results = snapshot.get("results", [])
    by_profile = _summarize_results(results, "profile")
    by_scenario = _summarize_results(results, "scenario")
    latencies = [result.get("avg_latency_ms", 0.0) for result in results] or [0.0]
    confidences = [result.get("avg_confidence", 0.0) for result in results] or [0.0]
    result_count = len(results)
    matrix = {
        "profiles": sorted(by_profile),
        "scenarios": sorted(by_scenario),
        "cells": {
            f"{scenario}::{profile}": [
                result["trace_hash"]
                for result in results
                if result["scenario"] == scenario and result["profile"] == profile
            ]
            for scenario in sorted(by_scenario)
            for profile in sorted(by_profile)
        },
    }
    cross_profile_comparisons = _build_cross_profile_comparisons(results)
    drift_score = round(
        sum(abs(item["latency_delta_ms"]) for item in cross_profile_comparisons)
        + sum(abs(item["confidence_delta"]) * 100.0 for item in cross_profile_comparisons)
        + sum(10.0 for item in cross_profile_comparisons if item["trace_hash_changed"]),
        6,
    )

    return {
        "protocol": "blackmamba.virtual.campaign.report.v1",
        "scenario_groups": by_scenario,
        "profile_groups": by_profile,
        "comparison_matrix": matrix,
        "cross_profile_comparisons": cross_profile_comparisons,
        "scenario_rankings": _build_scenario_rankings(results),
        "metrics": {
            **snapshot.get("metrics", {}),
            "result_count": result_count,
            "avg_latency_ms": snapshot.get("metrics", {}).get("avg_latency_ms", round(sum(latencies) / len(latencies), 6)),
            "avg_confidence": snapshot.get("metrics", {}).get("avg_confidence", round(sum(confidences) / len(confidences), 6)),
            "max_latency_ms": round(max(latencies), 6),
            "min_confidence": round(min(confidences), 6),
            "p50_latency_ms": _percentile(latencies, 0.50),
            "p90_latency_ms": _percentile(latencies, 0.90),
            "p95_latency_ms": _percentile(latencies, 0.95),
            "p99_latency_ms": _percentile(latencies, 0.99),
            "drift_score": drift_score,
        },
        "result_count": result_count,
        "top_latency_results": sorted(
            (
                {
                    "scenario": result["scenario"],
                    "profile": result["profile"],
                    "trace_hash": result["trace_hash"],
                    "avg_latency_ms": result.get("avg_latency_ms", 0.0),
                    "avg_confidence": result.get("avg_confidence", 0.0),
                }
                for result in results
            ),
            key=lambda item: (item["avg_latency_ms"], item["scenario"], item["profile"]),
            reverse=True,
        )[:5],
        "top_confidence_results": sorted(
            (
                {
                    "scenario": result["scenario"],
                    "profile": result["profile"],
                    "trace_hash": result["trace_hash"],
                    "avg_latency_ms": result.get("avg_latency_ms", 0.0),
                    "avg_confidence": result.get("avg_confidence", 0.0),
                }
                for result in results
            ),
            key=lambda item: (item["avg_confidence"], item["scenario"], item["profile"]),
            reverse=True,
        )[:5],
        "regression_summary": {
            "latency_percentiles_ms": {
                "p50": _percentile(latencies, 0.50),
                "p90": _percentile(latencies, 0.90),
                "p95": _percentile(latencies, 0.95),
                "p99": _percentile(latencies, 0.99),
            },
            "drift_score": drift_score,
            "cross_profile_count": len(cross_profile_comparisons),
        },
    }
