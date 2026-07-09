from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling.peripheralos.baseline import compare_campaign_to_baseline, create_baseline, load_baseline, save_baseline
from tooling.peripheralos.campaigns import CampaignScenario, fuzz_scenario, run_campaign
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

    def test_fuzzed_scenario_is_reproducible(self):
        source = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        fuzz_a = fuzz_scenario(source, "seed-a")
        fuzz_b = fuzz_scenario(source, "seed-a")
        self.assertEqual(fuzz_a.read_text(encoding="utf-8"), fuzz_b.read_text(encoding="utf-8"))

    def test_campaign_runner_writes_snapshot(self):
        out_dir = ROOT / "platform" / "generated" / "campaigns"
        scenario = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        snapshot = run_campaign([CampaignScenario(path=scenario, profile="default"), CampaignScenario(path=fuzz_scenario(scenario, "seed-c"), seed="seed-c", profile="default")], out_dir)
        self.assertEqual(snapshot["protocol"], "blackmamba.virtual.campaign.v1")
        self.assertEqual(snapshot["result_count"], 2)
        self.assertIn("metrics", snapshot)
        self.assertTrue((out_dir / "campaign.snapshot.json").exists())

    def test_campaign_golden_snapshot_matches(self):
        scenario = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        fuzzed = fuzz_scenario(scenario, "seed-a")
        snapshot = run_campaign(
            [
                CampaignScenario(path=scenario, profile="default"),
                CampaignScenario(path=scenario, profile="aim"),
                CampaignScenario(path=fuzzed, seed="seed-a", profile="default"),
                CampaignScenario(path=fuzzed, seed="seed-a", profile="aim"),
            ],
            ROOT / "platform" / "generated" / "campaigns-golden-check",
        )
        golden = ROOT / "platform" / "tests" / "golden" / "virtual-campaigns" / "basic-motion.campaign.snapshot.json"
        self.assertEqual(json.loads(golden.read_text(encoding="utf-8")), snapshot)

    def test_baseline_runner_detects_drift(self):
        scenario = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        baseline = create_baseline([CampaignScenario(path=scenario, profile="default")], ROOT / "platform" / "generated" / "baseline-build")
        report = compare_campaign_to_baseline(baseline, baseline)
        self.assertEqual(report["status"], "compatible")
        self.assertEqual(report["drift"], [])
        baseline_path = ROOT / "platform" / "generated" / "baseline.json"
        save_baseline(baseline_path, baseline)
        loaded = load_baseline(baseline_path)
        self.assertEqual(loaded["protocol"], "blackmamba.virtual.campaign.v1")

    def test_multi_profile_campaign_matrix(self):
        scenario = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        snapshot = run_campaign(
            [
                CampaignScenario(path=scenario, profile="default"),
                CampaignScenario(path=scenario, profile="aim"),
            ],
            ROOT / "platform" / "generated" / "multi-profile",
        )
        self.assertEqual(snapshot["metrics"]["profile_count"], 2)


if __name__ == "__main__":
    unittest.main()
