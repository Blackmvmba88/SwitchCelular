from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from .baseline import compare_campaign_to_baseline, create_baseline, load_baseline, save_baseline
from .campaigns import CampaignScenario, campaign_report, fuzz_scenario_with_hypothesis


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="peripheralos-baseline-runner")
    parser.add_argument("--scenario", action="append", required=True)
    parser.add_argument("--hypothesis-seed", action="append", default=[], help="Generate deterministic hypothesis fuzzed scenarios")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--out-dir", default="platform/generated/baselines")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args(argv)

    scenarios = [CampaignScenario(path=Path(path)) for path in args.scenario]
    for seed in args.hypothesis_seed:
        for path in args.scenario:
            scenarios.append(CampaignScenario(path=fuzz_scenario_with_hypothesis(Path(path), seed), seed=seed))
    out_dir = Path(args.out_dir)
    current = create_baseline(scenarios, out_dir / "current")
    current["report"] = campaign_report(current)
    baseline_path = Path(args.baseline)

    if args.update or not baseline_path.exists():
        save_baseline(baseline_path, current)
        print({"status": "baseline-updated", "baseline": str(baseline_path)})
        return 0

    baseline = load_baseline(baseline_path)
    baseline.setdefault("report", campaign_report(baseline))
    report = compare_campaign_to_baseline(current, baseline)
    report_text = json.dumps(report, indent=2, sort_keys=True)
    print(report_text)
    if report["status"] != "compatible":
        diff = difflib.unified_diff(
            json.dumps(baseline.get("report", baseline), indent=2, sort_keys=True).splitlines(),
            json.dumps(current.get("report", current), indent=2, sort_keys=True).splitlines(),
            fromfile="baseline.report",
            tofile="current.report",
            lineterm="",
        )
        diff_text = "\n".join(diff)
        if diff_text:
            diff_path = out_dir / "baseline.diff.txt"
            diff_path.write_text(diff_text + "\n", encoding="utf-8")
            print(diff_text)
            print(f"diff written to {diff_path}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
