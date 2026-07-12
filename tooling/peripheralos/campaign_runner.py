from __future__ import annotations

import argparse
from pathlib import Path

from .campaigns import CampaignScenario, campaign_report, fuzz_scenario, run_campaign


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="peripheralos-campaign-runner")
    parser.add_argument("--scenario", action="append", required=True, help="Scenario JSON path")
    parser.add_argument("--profile", action="append", default=[], help="Profile name to include in campaign matrix")
    parser.add_argument("--out-dir", default="platform/generated/campaigns")
    parser.add_argument("--fuzz-seed", action="append", default=[], help="Optional deterministic fuzz seed")
    args = parser.parse_args(argv)
    profiles = args.profile or ["default"]

    scenarios = [
        CampaignScenario(path=Path(path), profile=profile)
        for path in args.scenario
        for profile in profiles
    ]
    for seed in args.fuzz_seed:
        for path in args.scenario:
            for profile in profiles:
                scenarios.append(CampaignScenario(path=fuzz_scenario(Path(path), seed), seed=seed, profile=profile))

    snapshot = run_campaign(scenarios, Path(args.out_dir))
    snapshot["report"] = campaign_report(snapshot)
    print(snapshot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
