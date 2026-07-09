from __future__ import annotations

import argparse
from pathlib import Path

from .baseline import compare_campaign_to_baseline, create_baseline, load_baseline, save_baseline
from .campaigns import CampaignScenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="peripheralos-baseline-runner")
    parser.add_argument("--scenario", action="append", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--out-dir", default="platform/generated/baselines")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args(argv)

    scenarios = [CampaignScenario(path=Path(path)) for path in args.scenario]
    out_dir = Path(args.out_dir)
    current = create_baseline(scenarios, out_dir / "current")
    baseline_path = Path(args.baseline)

    if args.update or not baseline_path.exists():
        save_baseline(baseline_path, current)
        print({"status": "baseline-updated", "baseline": str(baseline_path)})
        return 0

    baseline = load_baseline(baseline_path)
    report = compare_campaign_to_baseline(current, baseline)
    print(report)
    return 0 if report["status"] == "compatible" else 1


if __name__ == "__main__":
    raise SystemExit(main())

