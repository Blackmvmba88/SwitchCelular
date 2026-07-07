from __future__ import annotations

import argparse
import json
from pathlib import Path

from .generator import emit_json_schema, emit_manifest, write_json
from .model import PlatformIR
from .parser import parse_spec
from .validator import validate_specs


def load_ir(spec_dir: Path) -> PlatformIR:
    specs = sorted(spec_dir.glob("*.md"))
    parsed = [parse_spec(path) for path in specs]
    index = {"specs": [spec.header.id for spec in parsed]}
    return PlatformIR(specs=parsed, index=index)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="peripheralos-generator")
    parser.add_argument("--spec-dir", default="platform/spec")
    parser.add_argument("--out-dir", default="platform/generated")
    args = parser.parse_args(argv)

    ir = load_ir(Path(args.spec_dir))
    report = validate_specs(ir.specs)
    if not report.ok:
        for issue in report.issues:
            print(f"{issue.severity.upper()}: {issue.code}: {issue.message} [{issue.spec_id}]")
        return 1

    out_dir = Path(args.out_dir)
    write_json(out_dir / "schema.json", emit_json_schema(ir))
    write_json(out_dir / "manifest.json", emit_manifest(ir))
    write_json(
        out_dir / "ir.json",
        {
            "index": ir.index,
            "specs": [
                {
                    "header": {
                        "id": spec.header.id,
                        "title": spec.header.title,
                        "version": spec.header.version,
                        "status": spec.header.status,
                        "owner": spec.header.owner,
                        "depends_on": spec.header.depends_on,
                        "referenced_by": spec.header.referenced_by,
                        "compatibility": spec.header.compatibility,
                        "since": spec.header.since,
                        "supersedes": spec.header.supersedes,
                        "tags": spec.header.tags,
                    },
                    "body": spec.body.raw_markdown,
                }
                for spec in ir.specs
            ],
        },
    )
    print(json.dumps({"ok": True, "spec_count": len(ir.specs)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

