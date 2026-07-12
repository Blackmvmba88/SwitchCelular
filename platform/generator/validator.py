from __future__ import annotations

from collections import Counter
from dataclasses import asdict

from .model import SpecDocument, ValidationIssue, ValidationReport

ALLOWED_STATUSES = {"Draft", "Review", "Accepted", "Frozen", "Deprecated", "Superseded"}
ALLOWED_COMPATIBILITY = {"Backward Compatible", "Breaking", "Migration Required"}
REQUIRED_SECTIONS = {"Status", "Purpose"}


def validate_specs(specs: list[SpecDocument]) -> ValidationReport:
    issues: list[ValidationIssue] = []
    ids = [spec.header.id for spec in specs]
    duplicates = [spec_id for spec_id, count in Counter(ids).items() if count > 1]
    for spec_id in duplicates:
        issues.append(ValidationIssue("error", "duplicate-spec-id", f"duplicate spec id {spec_id}", spec_id))

    known_ids = set(ids)
    for spec in specs:
        header = spec.header
        if header.status not in ALLOWED_STATUSES:
            issues.append(ValidationIssue("error", "invalid-status", f"invalid status {header.status}", header.id))
        if header.compatibility not in ALLOWED_COMPATIBILITY:
            issues.append(ValidationIssue("error", "invalid-compatibility", f"invalid compatibility {header.compatibility}", header.id))
        if not header.owner.strip():
            issues.append(ValidationIssue("error", "missing-owner", "missing owner", header.id))
        for dep in header.depends_on:
            if dep not in known_ids:
                issues.append(ValidationIssue("error", "missing-dependency", f"unknown dependency {dep}", header.id))
        if header.id == "SPEC-0000" and header.depends_on:
            issues.append(ValidationIssue("warning", "root-dependencies", "platform root spec should not depend on others", header.id))
        section_names = {section.name for section in spec.sections}
        missing_sections = REQUIRED_SECTIONS - section_names
        if missing_sections:
            issues.append(
                ValidationIssue(
                    "warning",
                    "missing-sections",
                    f"missing sections: {', '.join(sorted(missing_sections))}",
                    header.id,
                )
            )

    ok = not any(issue.severity == "error" for issue in issues)
    return ValidationReport(ok=ok, issues=issues)


def compatibility_report(spec: SpecDocument) -> dict:
    header = asdict(spec.header)
    return {
        "spec": spec.header.id,
        "status": spec.header.status,
        "compatibility": spec.header.compatibility,
        "depends_on": spec.header.depends_on,
        "owner": spec.header.owner,
        "header": header,
    }
