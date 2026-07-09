from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .harness import run_harness


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


def _hash_trace(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _trace_metrics(trace_path: Path) -> dict[str, float]:
    data = json.loads(trace_path.read_text(encoding="utf-8"))
    frames = data.get("frames", [])
    if not frames:
        return {"avg_latency_ms": 0.0, "avg_confidence": 0.0}
    avg_latency = sum(frame.get("latency_ms", 0) for frame in frames) / len(frames)
    avg_confidence = sum(frame.get("confidence", 0.0) for frame in frames) / len(frames)
    return {"avg_latency_ms": round(avg_latency, 6), "avg_confidence": round(avg_confidence, 6)}


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
    return snapshot


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
