from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.wiki_io import write_text

SRC_ID_RE = re.compile(r"(SRC-\d+)", re.I)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")


@dataclass(frozen=True)
class SourceCardResult:
    status: str
    path: Path


def slugify(text: str) -> str:
    text = text.strip().lower().replace("_", "-")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "untitled-source"


def create_source_card(raw_file: Path, root: Path, today: str) -> SourceCardResult:
    existing = find_existing_card_for_raw(root, raw_file)
    if existing is not None:
        return SourceCardResult(status="exists", path=existing)

    out = build_source_card_path(raw_file, root)
    write_text(out, render_source_card(raw_file, root, today=today))
    return SourceCardResult(status="created", path=out)


def find_existing_card_for_raw(root: Path, raw_file: Path) -> Path | None:
    target = raw_file.relative_to(root).with_suffix("").as_posix()
    for card in sorted((root / "wiki" / "sources").glob("*.md")):
        text = card.read_text(encoding="utf-8", errors="replace")
        location = location_section(text)
        if location_has_raw_link(location, target=target):
            return card
    return None


def build_source_card_path(raw_file: Path, root: Path) -> Path:
    default_name = slugify(raw_file.stem.replace("SRC-", "").split("-", 1)[-1]) + ".md"
    out = root / "wiki" / "sources" / default_name
    i = 2
    while out.exists():
        out = root / "wiki" / "sources" / f"{default_name[:-3]}-{i}.md"
        i += 1
    return out


def render_source_card(raw_file: Path, root: Path, today: str) -> str:
    text = raw_file.read_text(encoding="utf-8", errors="replace")
    relative = raw_file.relative_to(root)
    rel_raw = relative.as_posix()
    stem = relative.with_suffix("").as_posix()
    title = title_from_raw(text, raw_file.stem)
    sid = source_id_from_raw(raw_file, text)
    source_type = detect_type(raw_file, text)
    coverage = guess_coverage(raw_file, text, title)
    key_sections = guess_key_sections(text)
    kind = source_kind(text, source_type)
    source_refs = f"[{sid}]" if sid else "[]"
    id_line = f"id: {sid}\n" if sid else ""
    tag_values = ["source"] + [part for part in slugify(title).split("-") if part]
    tag_line = ", ".join(tag_values)
    frontmatter = (
        "---\n"
        "type: source\n"
        f"{id_line}"
        f"title: {title}\n"
        "agent: aristotle\n"
        "subagent: source-ingest\n"
        "cover:\n"
        "status: active\n"
        "claim_type: fact\n"
        "confidence: medium\n"
        f"source_kind: {kind}\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        f"tags: [{tag_line}]\n"
        f"sources: {source_refs}\n"
        "---\n"
    )
    content = (
        frontmatter
        + f"# Source: {title}\n\n"
        + "## Location\n"
        + f"[[{stem}|/{rel_raw}]]\n\n"
        + "## Type\n"
        + f"{source_type}\n\n"
        + "## Coverage\n"
        + "".join(f"- {item}\n" for item in coverage)
        + "\n"
        + "## Used by\n"
        + "- _Fill after compiled pages are created or updated._\n\n"
        + "## Key Sections\n"
        + "".join(f"- {item}\n" for item in key_sections)
        + "\n"
        + "## Notes\n"
        + "- Auto-generated skeleton. Review coverage and key sections before relying on this card.\n"
        + "- Navigation-only notes. Do not turn this source card into a summary page.\n"
    )
    return content


def frontmatter_value(text: str, key: str) -> str | None:
    value = load_frontmatter(text).data.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    return str(value)


def body_without_frontmatter(text: str) -> str:
    return load_frontmatter(text).body


def source_id_from_raw(raw_file: Path, text: str) -> str | None:
    for candidate in (frontmatter_value(text, "source_id"), frontmatter_value(text, "id")):
        if candidate and SRC_ID_RE.fullmatch(candidate):
            return candidate.upper()
    match = SRC_ID_RE.search(raw_file.name)
    return match.group(1).upper() if match else None


def title_from_raw(text: str, fallback: str) -> str:
    for candidate in (frontmatter_value(text, "title"), frontmatter_value(text, "name")):
        if candidate:
            return candidate
    for line in body_without_frontmatter(text).splitlines()[:30]:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line:
            return line[:80].strip()
    return fallback


def detect_type(raw_file: Path, text: str) -> str:
    suffix = raw_file.suffix.lower()
    body = body_without_frontmatter(text)
    source = frontmatter_value(text, "source") or ""
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".txt", ".log"}:
        return "transcript / text"
    if source.startswith("http") or "Source URL:" in body or "http://" in body or "https://" in body:
        return "web / md note"
    if "##" in body or "# " in body:
        return "md / note"
    return "note"


def guess_key_sections(text: str) -> list[str]:
    sections: list[str] = []
    for line in body_without_frontmatter(text).splitlines()[:120]:
        stripped = line.strip()
        if stripped.startswith("## "):
            sections.append(stripped[3:].strip())
        elif stripped.startswith("### "):
            sections.append(stripped[4:].strip())
        if len(sections) >= 6:
            break
    if not sections:
        sections = ["Opening section", "Most decision-relevant section"]
    return sections


def guess_coverage(raw_file: Path, text: str, title: str) -> list[str]:
    keywords = frontmatter_value(text, "keywords")
    base = slugify(raw_file.stem.replace("SRC-", "").split("-", 1)[-1])
    parts = [part for part in base.split("-") if part]
    items: list[str] = []
    if keywords and keywords.startswith("[") and keywords.endswith("]"):
        inner = keywords[1:-1].strip()
        items.extend(
            part.strip().strip("'\"")
            for part in inner.split(",")
            if part.strip()
        )
    if len(parts) >= 2:
        items.insert(0, " ".join(parts[:2]))
    items.append(title)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped[:4] if deduped else [title, base]


def source_kind(text: str, source_type: str) -> str:
    source = (frontmatter_value(text, "source") or "").strip()
    agent = (frontmatter_value(text, "agent") or "").strip()
    if source == "internal-chat" or agent:
        return "internal-note"
    if source.startswith("http") or source_type.startswith("web"):
        return "article"
    return "note"


def location_section(text: str) -> str:
    match = re.search(
        r"^## Location\s*\n(?P<section>.*?)(?:\n## |\Z)",
        text,
        flags=re.M | re.S,
    )
    if match is None:
        return ""
    return match.group("section")


def location_has_raw_link(location: str, target: str) -> bool:
    for match in WIKILINK_RE.finditer(location):
        link_target, _link_display = match.groups()
        if link_target == target:
            return True
    return False
