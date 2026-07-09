from __future__ import annotations

import json
from pathlib import Path

from .simulator import VirtualMotorConfig, load_scenario, run_virtual_motor, trace_to_dict


def run_harness(
    scenario_path: Path,
    out_dir: Path,
    motor_id: str = "virtual-motor-001",
    seed: str = "seed-v1",
    profile: str = "default",
) -> dict:
    scenario = load_scenario(scenario_path)
    trace = run_virtual_motor(VirtualMotorConfig(motor_id=motor_id, seed=seed), scenario)
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_name = f"{scenario.name}.{profile}.{seed}.trace.json" if seed != "seed-v1" or profile != "default" else f"{scenario.name}.trace.json"
    trace_path = out_dir / trace_name
    trace_path.write_text(json.dumps(trace_to_dict(trace), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "scenario": scenario.name,
        "profile": profile,
        "trace_path": str(trace_path),
        "frame_count": len(trace.frames),
        "protocol": trace.protocol,
    }
