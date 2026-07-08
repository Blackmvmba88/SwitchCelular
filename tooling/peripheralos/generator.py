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


def emit_rust_binding(ir: PlatformIR) -> str:
    spec_ids = ",\n        ".join(f'"{spec.header.id}"' for spec in ir.specs)
    return (
        "// AUTO-GENERATED. DO NOT EDIT.\n"
        f"// protocol: {ir.protocol}\n\n"
        "#[derive(Debug, Clone, PartialEq, Eq)]\n"
        "pub struct PlatformBinding {\n"
        "    pub protocol: &'static str,\n"
        "    pub spec_ids: &'static [&'static str],\n"
        "}\n\n"
        "pub const PLATFORM_BINDING: PlatformBinding = PlatformBinding {\n"
        f"    protocol: \"{ir.protocol}\",\n"
        "    spec_ids: &[\n"
        f"        {spec_ids}\n"
        "    ],\n"
        "};\n"
    )


def emit_kotlin_binding(ir: PlatformIR) -> str:
    spec_ids = ", ".join(f'\"{spec.header.id}\"' for spec in ir.specs)
    return (
        "// AUTO-GENERATED. DO NOT EDIT.\n"
        f"// protocol: {ir.protocol}\n\n"
        "data class PlatformBinding(\n"
        "    val protocol: String,\n"
        "    val specIds: List<String>,\n"
        ")\n\n"
        "val PLATFORM_BINDING = PlatformBinding(\n"
        f"    protocol = \"{ir.protocol}\",\n"
        f"    specIds = listOf({spec_ids}),\n"
        ")\n"
    )


def emit_typescript_binding(ir: PlatformIR) -> str:
    spec_ids = ", ".join(f'\"{spec.header.id}\"' for spec in ir.specs)
    return (
        "// AUTO-GENERATED. DO NOT EDIT.\n"
        f"// protocol: {ir.protocol}\n\n"
        "export interface PlatformBinding {\n"
        "  protocol: string;\n"
        "  specIds: string[];\n"
        "}\n\n"
        "export const PLATFORM_BINDING: PlatformBinding = {\n"
        f"  protocol: \"{ir.protocol}\",\n"
        f"  specIds: [{spec_ids}],\n"
        "};\n"
    )


def emit_python_binding(ir: PlatformIR) -> str:
    spec_ids = ", ".join(repr(spec.header.id) for spec in ir.specs)
    return (
        "# AUTO-GENERATED. DO NOT EDIT.\n"
        f"# protocol: {ir.protocol}\n\n"
        "from dataclasses import dataclass\n"
        "from typing import Tuple\n\n"
        "@dataclass(frozen=True)\n"
        "class PlatformBinding:\n"
        "    protocol: str\n"
        "    spec_ids: Tuple[str, ...]\n\n"
        "PLATFORM_BINDING = PlatformBinding(\n"
        f"    protocol=\"{ir.protocol}\",\n"
        f"    spec_ids=({spec_ids}),\n"
        ")\n"
    )


def emit_language_bindings(ir: PlatformIR) -> dict[str, str]:
    return {
        "rust": emit_rust_binding(ir),
        "kotlin": emit_kotlin_binding(ir),
        "typescript": emit_typescript_binding(ir),
        "python": emit_python_binding(ir),
    }


def emit_language_binding_schema(ir: PlatformIR, language: str) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"PeripheralOS {language.title()} Binding v1",
        "type": "object",
        "required": ["language", "protocol", "spec_count", "spec_ids"],
        "properties": {
            "language": {"const": language},
            "protocol": {"const": ir.protocol},
            "spec_count": {"type": "integer", "minimum": 0},
            "spec_ids": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }


def emit_language_schemas(ir: PlatformIR) -> dict[str, dict]:
    return {language: emit_language_binding_schema(ir, language) for language in ("rust", "kotlin", "typescript", "python")}


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


def compare_specs(old_spec, new_spec) -> dict:
    old_header = old_spec.header
    new_header = new_spec.header
    changes = []

    if old_header.version != new_header.version:
        changes.append(
            {
                "field": "version",
                "old": old_header.version,
                "new": new_header.version,
                "breaking": True,
            }
        )
    if old_header.status != new_header.status:
        changes.append(
            {
                "field": "status",
                "old": old_header.status,
                "new": new_header.status,
                "breaking": False,
            }
        )
    if old_header.compatibility != new_header.compatibility:
        changes.append(
            {
                "field": "compatibility",
                "old": old_header.compatibility,
                "new": new_header.compatibility,
                "breaking": new_header.compatibility != "Backward Compatible",
            }
        )
    if old_header.tags != new_header.tags:
        changes.append(
            {
                "field": "tags",
                "old": old_header.tags,
                "new": new_header.tags,
                "breaking": False,
            }
        )
    if old_spec.body.raw_markdown != new_spec.body.raw_markdown:
        changes.append(
            {
                "field": "body",
                "old": old_spec.body.raw_markdown,
                "new": new_spec.body.raw_markdown,
                "breaking": False,
            }
        )

    overall = "compatible" if not any(change["breaking"] for change in changes) else "breaking"
    return {
        "old": old_header.id,
        "new": new_header.id,
        "overall": overall,
        "changes": changes,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload.rstrip() + "\n", encoding="utf-8")
