from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VirtualMotorConfig:
    motor_id: str
    seed: str
    latency_ms: int = 5
    jitter_ms: int = 0
    noise: float = 0.0


@dataclass(frozen=True)
class VirtualScenario:
    name: str
    frames: list[dict[str, Any]]


@dataclass(frozen=True)
class VirtualTrace:
    protocol: str
    scenario: str
    motor_id: str
    diagnostics: dict[str, Any]
    frames: list[dict[str, Any]]


def load_scenario(path: Path) -> VirtualScenario:
    data = json.loads(path.read_text(encoding="utf-8"))
    return VirtualScenario(name=data["name"], frames=list(data.get("frames", [])))


def _stable_noise(seed: str, index: int) -> float:
    digest = sha256(f"{seed}:{index}".encode("utf-8")).hexdigest()
    value = int(digest[:8], 16)
    return (value % 1000) / 100000.0


def run_virtual_motor(config: VirtualMotorConfig, scenario: VirtualScenario) -> VirtualTrace:
    emitted = []
    for index, frame in enumerate(scenario.frames):
        cloned = json.loads(json.dumps(frame))
        cloned.setdefault("timestamp_ms", index * 16)
        cloned.setdefault("confidence", 1.0)
        cloned["latency_ms"] = config.latency_ms + (index % (config.jitter_ms + 1) if config.jitter_ms else 0)
        if config.noise:
            cloned["confidence"] = round(max(0.0, min(1.0, cloned["confidence"] - _stable_noise(config.seed, index) * config.noise)), 6)
        emitted.append(cloned)

    diagnostics = {
        "motor_id": config.motor_id,
        "seed": config.seed,
        "frame_count": len(emitted),
        "latency_ms": config.latency_ms,
        "jitter_ms": config.jitter_ms,
        "noise": config.noise,
    }
    return VirtualTrace(
        protocol="blackmamba.virtual.motor.v1",
        scenario=scenario.name,
        motor_id=config.motor_id,
        diagnostics=diagnostics,
        frames=emitted,
    )


def trace_to_dict(trace: VirtualTrace) -> dict[str, Any]:
    return asdict(trace)

