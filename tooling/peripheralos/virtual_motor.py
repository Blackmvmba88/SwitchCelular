from __future__ import annotations

from pathlib import Path

from .harness import run_harness


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="peripheralos-virtual-motor")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--out-dir", default="platform/generated/virtual")
    parser.add_argument("--motor-id", default="virtual-motor-001")
    parser.add_argument("--seed", default="seed-v1")
    args = parser.parse_args(argv)

    summary = run_harness(Path(args.scenario), Path(args.out_dir), motor_id=args.motor_id, seed=args.seed)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

