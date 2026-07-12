from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Profile:
    id: str
    version: str
    device: dict[str, object] = field(default_factory=dict)
    motion: dict[str, object] = field(default_factory=dict)
    trigger: dict[str, object] = field(default_factory=dict)
    smoothing: dict[str, object] = field(default_factory=dict)
    mapping: dict[str, object] = field(default_factory=dict)
    limits: dict[str, object] = field(default_factory=dict)
    reference: dict[str, object] = field(default_factory=dict)
    context: dict[str, object] = field(default_factory=dict)
