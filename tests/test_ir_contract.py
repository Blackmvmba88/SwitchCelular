from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling.peripheralos.cli import load_ir
from tooling.peripheralos.generator import emit_binding_stubs, emit_ir_schema, emit_language_bindings, emit_language_schemas, compare_specs
from tooling.peripheralos.validator import validate_specs


class IRContractTests(unittest.TestCase):
    def test_ir_is_versioned_and_complete(self):
        ir = load_ir(ROOT / "platform" / "spec")
        report = validate_specs(ir.specs)
        self.assertTrue(report.ok, report.issues)
        self.assertEqual(ir.protocol, "blackmamba.platform.ir.v1")
        self.assertGreaterEqual(len(ir.specs), 13)

        first = ir.specs[0]
        self.assertEqual(first.header.id, "SPEC-0000")
        self.assertEqual(first.header.title, "Platform")
        self.assertTrue(first.body.raw_markdown.startswith("# Spec 0000: Platform"))

    def test_ir_schema_matches_protocol(self):
        ir = load_ir(ROOT / "platform" / "spec")
        schema = emit_ir_schema(ir)
        self.assertEqual(schema["properties"]["protocol"]["const"], "blackmamba.platform.ir.v1")
        self.assertIn("specs", schema["required"])
        self.assertIn("index", schema["required"])

    def test_golden_ir_fixture_exists(self):
        golden = ROOT / "platform" / "tests" / "golden" / "ir" / "platform-ir-v1.json"
        data = json.loads(golden.read_text(encoding="utf-8"))
        self.assertEqual(data["protocol"], "blackmamba.platform.ir.v1")
        self.assertIn("SPEC-0013", data["index"]["specs"])

    def test_golden_ir_schema_matches_generator(self):
        golden = ROOT / "platform" / "tests" / "golden" / "ir" / "platform-ir-v1.schema.json"
        ir = load_ir(ROOT / "platform" / "spec")
        data = json.loads(golden.read_text(encoding="utf-8"))
        self.assertEqual(data, emit_ir_schema(ir))

    def test_binding_golden_directories_exist(self):
        ir = load_ir(ROOT / "platform" / "spec")
        bindings = emit_binding_stubs(ir)
        for language in bindings:
            golden_dir = ROOT / "platform" / "tests" / "golden" / "ir" / "bindings" / language
            self.assertTrue(golden_dir.exists(), golden_dir)

    def test_binding_golden_sources_match_generator(self):
        ir = load_ir(ROOT / "platform" / "spec")
        sources = emit_language_bindings(ir)
        extensions = {"rust": "rs", "kotlin": "kt", "typescript": "ts", "python": "py"}
        for language, source in sources.items():
            golden = ROOT / "platform" / "tests" / "golden" / "ir" / "bindings" / language / f"platform-binding-v1.{extensions[language]}"
            self.assertEqual(golden.read_text(encoding="utf-8"), source)

    def test_binding_golden_schemas_match_generator(self):
        ir = load_ir(ROOT / "platform" / "spec")
        schemas = emit_language_schemas(ir)
        for language, schema in schemas.items():
            golden = ROOT / "platform" / "tests" / "golden" / "ir" / "bindings" / language / "schema.json"
            self.assertEqual(json.loads(golden.read_text(encoding="utf-8")), schema)

    def test_compatibility_golden_matches_generator(self):
        ir = load_ir(ROOT / "platform" / "spec")
        golden = ROOT / "platform" / "tests" / "golden" / "ir" / "compatibility" / "spec-0013-to-0014.json"
        self.assertEqual(json.loads(golden.read_text(encoding="utf-8")), compare_specs(ir.specs[-2], ir.specs[-1]))


if __name__ == "__main__":
    unittest.main()
