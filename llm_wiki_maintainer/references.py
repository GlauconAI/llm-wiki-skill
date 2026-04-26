from __future__ import annotations

from pathlib import Path
import re

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.links import rel, section_block, section_bounds

COMPILED_FACT_TYPES = {"overview", "concept", "entity", "topic"}
SOURCE_ID_RE = re.compile(r"SRC-\d+", re.I)


def frontmatter_value(text: str, key: str) -> str | None:
    value = load_frontmatter(text).data.get(key)
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    return str(value)


def parse_frontmatter_type(text: str) -> str | None:
    return frontmatter_value(text, "type")


def parse_source_id(text: str) -> str | None:
    for key in ("id", "source_id"):
        candidate = frontmatter_value(text, key)
        if candidate and SOURCE_ID_RE.fullmatch(candidate):
            return candidate.upper()
    return None


def parse_sources_field(text: str) -> list[str]:
    raw_sources = load_frontmatter(text).data.get("sources")
    if raw_sources is None:
        return []
    if isinstance(raw_sources, str):
        return [raw_sources.strip()] if raw_sources.strip() else []
    if isinstance(raw_sources, (list, tuple)):
        sources: list[str] = []
        for item in raw_sources:
            if item is None:
                continue
            value = str(item).strip()
            if value:
                sources.append(value)
        return sources
    value = str(raw_sources).strip()
    return [value] if value else []


def used_by_links(text: str) -> set[str]:
    links: set[str] = set()
    for target in re.findall(r"\[\[(wiki/[^\]|#]+)", section_block(text, "## Used by")):
        links.add(target)
    return links


def source_card_paths_by_id(root: Path) -> dict[str, str]:
    cards: dict[str, str] = {}
    for path in sorted((root / "wiki" / "sources").glob("*.md")):
        source_id = parse_source_id(path.read_text(encoding="utf-8"))
        if source_id:
            cards[source_id] = rel(path, root)
    return cards


def declared_used_by(root: Path) -> dict[str, set[str]]:
    declared: dict[str, set[str]] = {}
    for path in sorted((root / "wiki" / "sources").glob("*.md")):
        declared[rel(path, root)] = used_by_links(path.read_text(encoding="utf-8"))
    return declared


def compute_used_by(root: Path) -> dict[str, set[str]]:
    wiki_dir = root / "wiki"
    source_card_by_id = source_card_paths_by_id(root)
    usage = {card: set() for card in source_card_by_id.values()}

    for path in sorted(wiki_dir.rglob("*.md")):
        page_ref = rel(path, root)
        if "/sources/" in page_ref:
            continue
        text = path.read_text(encoding="utf-8")
        if parse_frontmatter_type(text) not in COMPILED_FACT_TYPES:
            continue
        for source_id in parse_sources_field(text):
            card = source_card_by_id.get(source_id)
            if card:
                usage.setdefault(card, set()).add(page_ref[:-3])

    return usage


def render_used_by(refs: set[str]) -> str:
    if not refs:
        return "- _No compiled wiki pages currently reference this source._\n"
    return "".join(f"- [[{ref}]]\n" for ref in sorted(refs))


def sync_used_by(root: Path) -> list[Path]:
    usage = compute_used_by(root)
    card_paths = {
        rel(path, root): path
        for path in sorted((root / "wiki" / "sources").glob("*.md"))
    }
    updated: list[Path] = []

    for card_ref, refs in sorted(usage.items()):
        card = card_paths[card_ref]
        text = card.read_text(encoding="utf-8")
        bounds = section_bounds(text, "## Used by")
        if bounds is None:
            continue
        start, end = bounds
        new_text = text[:start] + render_used_by(refs) + text[end:]
        if new_text != text:
            card.write_text(new_text, encoding="utf-8")
            updated.append(card)

    return updated
