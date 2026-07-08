from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling.peripheralos.cli import load_ir
from tooling.peripheralos.generator import emit_binding_stubs, emit_compatibility_report, emit_ir_schema, emit_json_schema, emit_language_bindings, emit_manifest
from tooling.peripheralos.validator import compatibility_report, validate_specs


class GeneratorTests(unittest.TestCase):
    def test_peripheral_abi_conforms(self):
        ir = load_ir(ROOT / "platform" / "spec")
        report = validate_specs(ir.specs)
        self.assertTrue(report.ok, report.issues)
        schema = emit_json_schema(ir)
        ir_schema = emit_ir_schema(ir)
        manifest = emit_manifest(ir)
        self.assertEqual(schema["x-spec-count"], len(ir.specs))
        self.assertEqual(ir_schema["properties"]["protocol"]["const"], ir.protocol)
        self.assertEqual(manifest["spec_count"], len(ir.specs))
        self.assertIn("SPEC-0002", manifest["spec_ids"])

    def test_binding_stubs_exist(self):
        ir = load_ir(ROOT / "platform" / "spec")
        bindings = emit_binding_stubs(ir)
        self.assertEqual(set(bindings), {"rust", "kotlin", "typescript", "python"})
        for language, payload in bindings.items():
            self.assertEqual(payload["language"], language)
            self.assertEqual(payload["protocol"], ir.protocol)

    def test_compatibility_report_exists(self):
        ir = load_ir(ROOT / "platform" / "spec")
        report = emit_compatibility_report(ir)
        self.assertEqual(report["protocol"], ir.protocol)
        self.assertEqual(report["status"], "compatible")

    def test_language_binding_sources_exist(self):
        ir = load_ir(ROOT / "platform" / "spec")
        bindings = emit_language_bindings(ir)
        self.assertEqual(set(bindings), {"rust", "kotlin", "typescript", "python"})
        self.assertIn("pub const PLATFORM_BINDING", bindings["rust"])
        self.assertIn("val PLATFORM_BINDING", bindings["kotlin"])
        self.assertIn("export const PLATFORM_BINDING", bindings["typescript"])
        self.assertIn("PLATFORM_BINDING = PlatformBinding(", bindings["python"])

    def test_compatibility_report_available(self):
        ir = load_ir(ROOT / "platform" / "spec")
        spec = next(spec for spec in ir.specs if spec.header.id == "SPEC-0002")
        report = compatibility_report(spec)
        self.assertEqual(report["spec"], "SPEC-0002")
        self.assertEqual(report["compatibility"], "Backward Compatible")


if __name__ == "__main__":
    unittest.main()
