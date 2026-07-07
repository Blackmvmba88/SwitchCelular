from __future__ import annotations

from pathlib import Path

from .model import SpecBody, SpecDocument, SpecHeader


class SpecParseError(ValueError):
    pass


def _parse_scalar(value: str):
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _parse_list(value: str) -> list[str]:
    inner = value.strip()[1:-1].strip()
    if not inner:
        return []
    items = []
    for part in inner.split(","):
        item = part.strip()
        if item.startswith('"') and item.endswith('"'):
            item = item[1:-1]
        elif item.startswith("'") and item.endswith("'"):
            item = item[1:-1]
        items.append(item)
    return items


def parse_frontmatter(markdown: str) -> tuple[dict[str, object], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SpecParseError("missing YAML frontmatter")
    data: dict[str, object] = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            return data, "\n".join(lines[i + 1 :]).lstrip("\n")
        if not line.strip():
            i += 1
            continue
        if ":" not in line:
            raise SpecParseError(f"invalid frontmatter line {i + 1}: {line}")
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw == "":
            data[key] = []
        elif raw.startswith("[") and raw.endswith("]"):
            data[key] = _parse_list(raw)
        else:
            data[key] = _parse_scalar(raw)
        i += 1
    raise SpecParseError("unterminated YAML frontmatter")


def parse_spec(path: Path) -> SpecDocument:
    markdown = path.read_text(encoding="utf-8")
    header_data, body = parse_frontmatter(markdown)
    required = ["id", "title", "version", "status", "owner"]
    missing = [key for key in required if key not in header_data]
    if missing:
        raise SpecParseError(f"{path.name}: missing keys: {', '.join(missing)}")
    if not str(header_data["id"]).startswith("SPEC-"):
        raise SpecParseError(f"{path.name}: invalid spec id {header_data['id']}")
    if not str(header_data["version"]).count(".") >= 1:
        raise SpecParseError(f"{path.name}: invalid version {header_data['version']}")
    header = SpecHeader(
        id=str(header_data["id"]),
        title=str(header_data["title"]),
        version=str(header_data["version"]),
        status=str(header_data["status"]),
        owner=str(header_data["owner"]),
        depends_on=[str(x) for x in header_data.get("depends_on", [])],
        referenced_by=[str(x) for x in header_data.get("referenced_by", [])],
        compatibility=str(header_data.get("compatibility", "Backward Compatible")),
        since=str(header_data.get("since", "1.0")),
        supersedes=None if header_data.get("supersedes") in {None, "null"} else str(header_data.get("supersedes")),
        tags=[str(x) for x in header_data.get("tags", [])],
    )
    return SpecDocument(path=path, header=header, body=SpecBody(raw_markdown=body))
