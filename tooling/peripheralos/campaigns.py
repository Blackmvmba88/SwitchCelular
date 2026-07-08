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


@dataclass(frozen=True)
class CampaignResult:
    scenario: str
    trace_path: str
    trace_hash: str
    frame_count: int
    protocol: str


def _hash_trace(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def run_campaign(scenarios: list[CampaignScenario], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[CampaignResult] = []
    for scenario in scenarios:
        summary = run_harness(scenario.path, out_dir / "traces", motor_id=scenario.motor_id, seed=scenario.seed)
        trace_path = Path(summary["trace_path"])
        trace_ref = Path("traces") / trace_path.name
        results.append(
            CampaignResult(
                scenario=summary["scenario"],
                trace_path=trace_ref.as_posix(),
                trace_hash=_hash_trace(trace_path),
                frame_count=summary["frame_count"],
                protocol=summary["protocol"],
            )
        )

    snapshot = {
        "protocol": "blackmamba.virtual.campaign.v1",
        "result_count": len(results),
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
