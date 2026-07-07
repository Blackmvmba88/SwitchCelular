from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "schemas" / "plugin-manifest.schema.json"
FIXTURES = ROOT / "platform" / "tests" / "conformance" / "fixtures"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_valid_plugin_manifest_passes_schema_validation():
    schema = load_json(SCHEMA_PATH)
    fixture = load_json(FIXTURES / "valid-plugin-manifest.json")

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(fixture))

    assert errors == []


def test_invalid_plugin_manifest_fails_schema_validation():
    schema = load_json(SCHEMA_PATH)
    fixture = load_json(FIXTURES / "invalid-plugin-manifest.json")

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(fixture))

    assert errors != []
