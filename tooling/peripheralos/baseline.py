from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any

from .campaigns import CampaignScenario, run_campaign


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
    return run_campaign(scenarios, out_dir)


def compare_campaign_to_baseline(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_results = {entry["scenario"]: entry for entry in current.get("results", [])}
    baseline_results = {entry["scenario"]: entry for entry in baseline.get("results", [])}
    drift = []
    for scenario, baseline_entry in baseline_results.items():
        current_entry = current_results.get(scenario)
        if current_entry is None:
            drift.append({"scenario": scenario, "kind": "missing", "breaking": True})
            continue
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
    status = "compatible" if not any(item["breaking"] for item in drift) else "breaking"
    return {"status": status, "drift": drift, "baseline_count": len(baseline_results), "current_count": len(current_results)}

