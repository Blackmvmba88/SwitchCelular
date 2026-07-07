from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SPEC_INDEX = ROOT / "platform" / "spec" / "index.yaml"
SPEC_DIR = ROOT / "platform" / "spec"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_canonical_contracts_exist_and_match_index_ids():
    index = load_yaml(SPEC_INDEX)
    contracts = index.get("canonical_contracts", [])

    assert contracts, "Expected canonical contracts in platform/spec/index.yaml"

    for contract in contracts:
        spec_path = SPEC_DIR / contract["file"]
        assert spec_path.exists(), f"Missing canonical contract: {spec_path}"

        spec = load_yaml(spec_path)
        assert spec["id"] == contract["id"]
        assert spec["authority"] == "platform/spec/index.yaml"
        assert "ownership" in spec


def test_generation_and_validation_sections_are_registered():
    index = load_yaml(SPEC_INDEX)

    assert index["generation"]["source_of_truth"] == "platform/spec/index.yaml"
    assert "platform/bindings/" in index["generation"]["generated_outputs"]
    assert index["validation"]["conformance_tests"] == "platform/tests/conformance/"
    assert index["validation"]["compatibility_tests"] == "platform/tests/compatibility/"
