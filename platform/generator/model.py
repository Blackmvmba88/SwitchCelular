from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SpecSection:
    name: str
    body: str


@dataclass(frozen=True)
class SpecHeader:
    id: str
    title: str
    version: str
    status: str
    owner: str
    depends_on: list[str] = field(default_factory=list)
    referenced_by: list[str] = field(default_factory=list)
    compatibility: str = "Backward Compatible"
    since: str = "1.0"
    supersedes: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SpecBody:
    raw_markdown: str


@dataclass(frozen=True)
class SpecDocument:
    path: Path
    header: SpecHeader
    body: SpecBody
    sections: list[SpecSection] = field(default_factory=list)


@dataclass(frozen=True)
class SpecAST:
    metadata: SpecHeader
    sections: list[SpecSection]
    constraints: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    spec_id: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    issues: list[ValidationIssue]


@dataclass(frozen=True)
class PlatformIR:
    specs: list[SpecDocument]
    index: dict[str, Any]
    spec_version: str = "1.0.0-candidate"
