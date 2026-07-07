from __future__ import annotations

import json
from pathlib import Path

from .model import PlatformIR


def emit_json_schema(ir: PlatformIR) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "PeripheralOS Platform IR",
        "type": "object",
        "required": ["specs"],
        "properties": {
            "specs": {
                "type": "array",
                "items": {"type": "object"},
            }
        },
        "x-spec-count": len(ir.specs),
    }


def emit_manifest(ir: PlatformIR) -> dict:
    return {
        "spec_count": len(ir.specs),
        "spec_ids": [spec.header.id for spec in ir.specs],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

