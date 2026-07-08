from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling.peripheralos.harness import run_harness
from tooling.peripheralos.simulator import VirtualMotorConfig, load_scenario, run_virtual_motor


class VirtualMotorTests(unittest.TestCase):
    def test_virtual_motor_is_deterministic(self):
        scenario = load_scenario(ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json")
        config = VirtualMotorConfig(motor_id="virtual-motor-001", seed="seed-v1")
        trace_a = run_virtual_motor(config, scenario)
        trace_b = run_virtual_motor(config, scenario)
        self.assertEqual(json.dumps(trace_a.__dict__, sort_keys=True, default=str), json.dumps(trace_b.__dict__, sort_keys=True, default=str))
        self.assertEqual(trace_a.protocol, "blackmamba.virtual.motor.v1")
        self.assertEqual(len(trace_a.frames), 2)

    def test_harness_writes_trace(self):
        out_dir = ROOT / "platform" / "generated" / "virtual"
        summary = run_harness(ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json", out_dir)
        trace_path = Path(summary["trace_path"])
        self.assertTrue(trace_path.exists())
        data = json.loads(trace_path.read_text(encoding="utf-8"))
        self.assertEqual(data["scenario"], "basic-motion")
        self.assertEqual(summary["frame_count"], 2)


if __name__ == "__main__":
    unittest.main()

