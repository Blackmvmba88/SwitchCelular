from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any

from .campaigns import CampaignScenario, campaign_report, run_campaign


@dataclass(frozen=True)
class BaselineEntry:
    scenario: str
    trace_hash: str
    frame_count: int
    protocol: str


def load_baseline(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_baseline(path: Path, campaign_snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(campaign_snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def create_baseline(scenarios: list[CampaignScenario], out_dir: Path) -> dict[str, Any]:
    snapshot = run_campaign(scenarios, out_dir)
    snapshot["report"] = campaign_report(snapshot)
    return snapshot


def compare_campaign_to_baseline(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_results = {entry["scenario"]: entry for entry in current.get("results", [])}
    baseline_results = {entry["scenario"]: entry for entry in baseline.get("results", [])}
    drift = []
    comparison_rows = []
    for scenario, baseline_entry in baseline_results.items():
        current_entry = current_results.get(scenario)
        if current_entry is None:
            drift.append({"scenario": scenario, "kind": "missing", "breaking": True})
            continue
        row = {
            "scenario": scenario,
            "baseline_profile": baseline_entry.get("profile"),
            "current_profile": current_entry.get("profile"),
            "baseline_latency_ms": baseline_entry.get("avg_latency_ms"),
            "current_latency_ms": current_entry.get("avg_latency_ms"),
            "baseline_confidence": baseline_entry.get("avg_confidence"),
            "current_confidence": current_entry.get("avg_confidence"),
            "latency_delta_ms": round(current_entry.get("avg_latency_ms", 0.0) - baseline_entry.get("avg_latency_ms", 0.0), 6),
            "confidence_delta": round(current_entry.get("avg_confidence", 0.0) - baseline_entry.get("avg_confidence", 0.0), 6),
        }
        if current_entry["trace_hash"] != baseline_entry["trace_hash"]:
            drift.append(
                {
                    "scenario": scenario,
                    "kind": "trace_hash",
                    "baseline": baseline_entry["trace_hash"],
                    "current": current_entry["trace_hash"],
                    "breaking": True,
                }
            )
        if current_entry["frame_count"] != baseline_entry["frame_count"]:
            drift.append(
                {
                    "scenario": scenario,
                    "kind": "frame_count",
                    "baseline": baseline_entry["frame_count"],
                    "current": current_entry["frame_count"],
                    "breaking": False,
                }
            )
        if current_entry.get("profile") != baseline_entry.get("profile"):
            drift.append(
                {
                    "scenario": scenario,
                    "kind": "profile",
                    "baseline": baseline_entry.get("profile"),
                    "current": current_entry.get("profile"),
                    "breaking": False,
                }
            )
        comparison_rows.append(row)
    baseline_metrics = baseline.get("metrics", {})
    current_metrics = current.get("metrics", {})
    profile_delta = {}
    for profile in sorted(set(baseline.get("report", {}).get("profile_groups", {})) | set(current.get("report", {}).get("profile_groups", {}))):
        baseline_profile = baseline.get("report", {}).get("profile_groups", {}).get(profile, {})
        current_profile = current.get("report", {}).get("profile_groups", {}).get(profile, {})
        profile_delta[profile] = {
            "count_delta": current_profile.get("count", 0) - baseline_profile.get("count", 0),
            "latency_delta_ms": round(current_profile.get("avg_latency_ms", 0.0) - baseline_profile.get("avg_latency_ms", 0.0), 6),
            "confidence_delta": round(current_profile.get("avg_confidence", 0.0) - baseline_profile.get("avg_confidence", 0.0), 6),
        }
    scenario_delta = {}
    for scenario in sorted(set(baseline.get("report", {}).get("scenario_groups", {})) | set(current.get("report", {}).get("scenario_groups", {}))):
        baseline_scenario = baseline.get("report", {}).get("scenario_groups", {}).get(scenario, {})
        current_scenario = current.get("report", {}).get("scenario_groups", {}).get(scenario, {})
        scenario_delta[scenario] = {
            "count_delta": current_scenario.get("count", 0) - baseline_scenario.get("count", 0),
            "latency_delta_ms": round(current_scenario.get("avg_latency_ms", 0.0) - baseline_scenario.get("avg_latency_ms", 0.0), 6),
            "confidence_delta": round(current_scenario.get("avg_confidence", 0.0) - baseline_scenario.get("avg_confidence", 0.0), 6),
        }
    for key in ["avg_latency_ms", "avg_confidence"]:
        if baseline_metrics.get(key) != current_metrics.get(key):
            drift.append(
                {
                    "kind": key,
                    "baseline": baseline_metrics.get(key),
                    "current": current_metrics.get(key),
                    "breaking": False,
                }
            )
    status = "compatible" if not any(item["breaking"] for item in drift) else "breaking"
    return {
        "status": status,
        "drift": drift,
        "baseline_count": len(baseline_results),
        "current_count": len(current_results),
        "baseline_metrics": baseline_metrics,
        "current_metrics": current_metrics,
        "baseline_report": baseline.get("report", {}),
        "current_report": current.get("report", {}),
        "comparison_rows": comparison_rows,
        "profile_deltas": profile_delta,
        "scenario_deltas": scenario_delta,
    }
