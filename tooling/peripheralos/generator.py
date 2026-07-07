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


def _binding_payload(ir: PlatformIR, language: str) -> dict:
    return {
        "language": language,
        "protocol": ir.protocol,
        "spec_count": len(ir.specs),
        "spec_ids": [spec.header.id for spec in ir.specs],
    }


def emit_binding_stubs(ir: PlatformIR) -> dict[str, dict]:
    return {
        "rust": _binding_payload(ir, "rust"),
        "kotlin": _binding_payload(ir, "kotlin"),
        "typescript": _binding_payload(ir, "typescript"),
        "python": _binding_payload(ir, "python"),
    }


def emit_ir_schema(ir: PlatformIR) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "PeripheralOS Platform IR v1",
        "type": "object",
        "required": ["protocol", "index", "specs"],
        "properties": {
            "protocol": {"const": ir.protocol},
            "index": {
                "type": "object",
                "properties": {
                    "specs": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["specs"],
            },
            "specs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["header", "body"],
                    "properties": {
                        "header": {"type": "object"},
                        "body": {"type": "string"},
                    },
                },
            },
        },
    }


def emit_compatibility_report(ir: PlatformIR) -> dict:
    return {
        "protocol": ir.protocol,
        "spec_count": len(ir.specs),
        "status": "compatible",
        "changes": [],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload.rstrip() + "\n", encoding="utf-8")
