#!/usr/bin/env python3
"""PeripheralOS validation CLI.

This tool validates the governance-first platform contracts before runtime code
becomes authoritative.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SPEC_INDEX = ROOT / "platform" / "spec" / "index.yaml"
SCHEMAS = ROOT / "schemas"
FIXTURES = ROOT / "platform" / "tests" / "conformance" / "fixtures"


class ValidationFailure(RuntimeError):
    """Raised when a validation command fails."""


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_specs() -> None:
    if not SPEC_INDEX.exists():
        raise ValidationFailure(f"Missing spec index: {SPEC_INDEX}")

    index = load_yaml(SPEC_INDEX)
    canonical_contracts = index.get("canonical_contracts", [])

    if not canonical_contracts:
        raise ValidationFailure("No canonical contracts registered in platform/spec/index.yaml")

    failures: list[str] = []

    for contract in canonical_contracts:
        contract_file = ROOT / "platform" / "spec" / contract["file"]
        if not contract_file.exists():
            failures.append(f"Missing canonical contract file: {contract_file}")
            continue

        data = load_yaml(contract_file)
        for required in ["id", "version", "status", "authority", "summary", "ownership"]:
            if required not in data:
                failures.append(f"{contract_file}: missing required field '{required}'")

        if data.get("id") != contract.get("id"):
            failures.append(
                f"{contract_file}: id mismatch index={contract.get('id')} file={data.get('id')}"
            )

    if failures:
        raise ValidationFailure("\n".join(failures))


def validate_fixture(schema_path: Path, fixture_path: Path) -> list[str]:
    schema = load_json(schema_path)
    fixture = load_json(fixture_path)
    validator = Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(fixture), key=str)]


def validate_fixtures() -> None:
    plugin_schema = SCHEMAS / "plugin-manifest.schema.json"
    valid_plugin = FIXTURES / "valid-plugin-manifest.json"
    invalid_plugin = FIXTURES / "invalid-plugin-manifest.json"

    for path in [plugin_schema, valid_plugin, invalid_plugin]:
        if not path.exists():
            raise ValidationFailure(f"Missing validation asset: {path}")

    valid_errors = validate_fixture(plugin_schema, valid_plugin)
    if valid_errors:
        raise ValidationFailure(
            "Valid plugin manifest fixture failed validation:\n" + "\n".join(valid_errors)
        )

    invalid_errors = validate_fixture(plugin_schema, invalid_plugin)
    if not invalid_errors:
        raise ValidationFailure("Invalid plugin manifest fixture unexpectedly passed validation")


def validate_all() -> None:
    validate_specs()
    validate_fixtures()


def main() -> int:
    parser = argparse.ArgumentParser(prog="peripheralos_validate")
    parser.add_argument(
        "target",
        choices=["specs", "fixtures", "all"],
        help="Validation target to run.",
    )
    args = parser.parse_args()

    try:
        if args.target == "specs":
            validate_specs()
        elif args.target == "fixtures":
            validate_fixtures()
        else:
            validate_all()
    except ValidationFailure as exc:
        print(f"PeripheralOS validation failed:\n{exc}")
        return 1

    print(f"PeripheralOS validation passed: {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
