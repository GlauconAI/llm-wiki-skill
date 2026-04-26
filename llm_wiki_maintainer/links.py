from __future__ import annotations

from pathlib import Path
import re

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
RAW_WIKILINK_RE = re.compile(r"\[\[(raw/sources/[^\]|]+)(?:\|[^\]]+)?\]\]")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def normalize_wikilink_target(target: str) -> str:
    normalized = target.strip().lstrip("/")
    if normalized.endswith(".md"):
        normalized = normalized[:-3]
    return normalized


def target_exists(base: Path, target: str) -> bool:
    normalized = normalize_wikilink_target(target)
    candidate = base / normalized
    return candidate.exists() or candidate.with_suffix(".md").exists()


def section_bounds(text: str, heading: str) -> tuple[int, int] | None:
    marker = heading + "\n"
    start = text.find(marker)
    if start == -1:
        return None
    body_start = start + len(marker)
    rest = text[body_start:]
    next_heading = rest.find("\n## ")
    end = len(text) if next_heading == -1 else body_start + next_heading + 1
    return body_start, end


def section_block(text: str, heading: str) -> str:
    bounds = section_bounds(text, heading)
    if bounds is None:
        return ""
    start, end = bounds
    return text[start:end].strip()


def section_lines(text: str, heading: str) -> list[str]:
    return [line.rstrip() for line in section_block(text, heading).splitlines()]


def wikilink_targets(text: str) -> list[str]:
    return [normalize_wikilink_target(target) for target in WIKILINK_RE.findall(text)]
