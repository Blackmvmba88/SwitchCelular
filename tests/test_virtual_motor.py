from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tooling.peripheralos.baseline import compare_campaign_to_baseline, create_baseline, load_baseline, save_baseline
from tooling.peripheralos.campaigns import CampaignScenario, campaign_report, fuzz_scenario, fuzz_scenario_with_hypothesis, run_campaign
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

    def test_hypothesis_fuzz_is_reproducible(self):
        source = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        fuzz_a = fuzz_scenario_with_hypothesis(source, "seed-h")
        fuzz_b = fuzz_scenario_with_hypothesis(source, "seed-h")
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
        report = campaign_report(snapshot)
        self.assertEqual(report["result_count"], 4)
        self.assertIn("profile_groups", report)
        self.assertIn("scenario_groups", report)

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

    def test_campaign_report_groups_by_profile_and_scenario(self):
        scenario = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        snapshot = run_campaign(
            [
                CampaignScenario(path=scenario, profile="default"),
                CampaignScenario(path=scenario, profile="aim"),
            ],
            ROOT / "platform" / "generated" / "single-campaign",
        )
        report = campaign_report(snapshot)
        self.assertEqual(report["result_count"], 2)
        self.assertIn("default", report["profile_groups"])
        self.assertIn("basic-motion", report["scenario_groups"])
        self.assertIn("comparison_matrix", report)
        self.assertIn("top_latency_results", report)
        self.assertIn("top_confidence_results", report)
        self.assertIn("cross_profile_comparisons", report)
        self.assertIn("scenario_rankings", report)
        self.assertIn("regression_summary", report)
        self.assertIn("p50_latency_ms", report["metrics"])
        self.assertIn("drift_score", report["metrics"])
        self.assertEqual(report["regression_summary"]["cross_profile_count"], 1)
        self.assertEqual(report["cross_profile_comparisons"][0]["profile"], "aim")
        self.assertIn("basic-motion", report["scenario_rankings"])
        self.assertIn("worst_latency", report["scenario_rankings"]["basic-motion"])
        self.assertTrue((ROOT / "platform" / "generated" / "single-campaign" / "campaign.regression.json").exists())
        self.assertTrue((ROOT / "platform" / "generated" / "single-campaign" / "campaign.benchmark.json").exists())

        benchmark_path = ROOT / "platform" / "generated" / "single-campaign" / "campaign.benchmark.json"
        benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
        self.assertEqual(benchmark["protocol"], "blackmamba.virtual.campaign.benchmark.v1")
        self.assertGreaterEqual(benchmark["sample_count"], 3)
        self.assertIn("metrics", benchmark)
        self.assertIn("report_latency_percentiles_ms", benchmark)

    def test_baseline_comparison_includes_profile_and_scenario_deltas(self):
        scenario = ROOT / "platform" / "tests" / "scenarios" / "basic-motion.json"
        baseline = create_baseline([CampaignScenario(path=scenario, profile="default")], ROOT / "platform" / "generated" / "baseline-comparison")
        report = compare_campaign_to_baseline(baseline, baseline)
        self.assertIn("comparison_rows", report)
        self.assertIn("profile_deltas", report)
        self.assertIn("scenario_deltas", report)
        self.assertIn("default", report["profile_deltas"])
        self.assertIn("basic-motion", report["scenario_deltas"])
        self.assertIn("baseline_report", report)
        self.assertIn("current_report", report)


if __name__ == "__main__":
    unittest.main()
