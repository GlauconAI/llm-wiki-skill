from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from llm_wiki_maintainer.links import normalize_wikilink_target, section_block, wikilink_targets
from llm_wiki_maintainer.source_cards import location_has_raw_link, location_section

_MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdx"}


@dataclass
class SourceRemovalImpact:
    source_cards_to_delete: list[Path] = field(default_factory=list)
    pages_to_update: list[Path] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)


def analyze_source_removal(root: Path | str, raw_path: Path | str) -> SourceRemovalImpact:
    root_path = Path(root).resolve()
    raw_file = _resolve_path(root_path, raw_path)
    raw_target = _path_target(root_path, raw_file)

    impact = SourceRemovalImpact()
    source_cards = _source_cards_for_raw(root_path, raw_target)
    impact.source_cards_to_delete.extend(source_cards)

    dependent_pages = _dependent_pages_from_source_cards(root_path, source_cards)
    _extend_unique(impact.pages_to_update, dependent_pages)

    removal_targets = {raw_target}
    removal_targets.update(_path_target(root_path, card) for card in source_cards)

    for page in _candidate_markdown_pages(root_path):
        if page in source_cards:
            continue

        text = _safe_read(page)
        if not text:
            continue

        matched_links = [
            link
            for link in wikilink_targets(text)
            if normalize_wikilink_target(link) in removal_targets
        ]
        if not matched_links:
            continue

        _extend_unique(impact.pages_to_update, [page])
        page_ref = page.relative_to(root_path).as_posix()
        impact.broken_links.extend(f"{page_ref} -> [[{link}]]" for link in matched_links)

    for source_card in source_cards:
        source_text = _safe_read(source_card)
        location = location_section(source_text)
        for link in wikilink_targets(location):
            if normalize_wikilink_target(link) == raw_target:
                impact.broken_links.append(
                    f"{source_card.relative_to(root_path).as_posix()} -> [[{link}]]"
                )

    return impact


def _resolve_path(root: Path, path: Path | str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    return resolved.resolve()


def _candidate_markdown_pages(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in _MARKDOWN_SUFFIXES:
            yield path.resolve()


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _path_target(root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = path
    return normalize_wikilink_target(relative.with_suffix("").as_posix())


def _source_cards_for_raw(root: Path, raw_target: str) -> list[Path]:
    source_dir = root / "wiki" / "sources"
    if not source_dir.exists():
        return []

    source_cards: list[Path] = []
    for card in sorted(source_dir.glob("*.md")):
        text = _safe_read(card)
        if not text:
            continue
        if location_has_raw_link(location_section(text), target=raw_target):
            source_cards.append(card.resolve())
    return source_cards


def _dependent_pages_from_source_cards(root: Path, source_cards: list[Path]) -> list[Path]:
    pages: list[Path] = []
    for source_card in source_cards:
        text = _safe_read(source_card)
        used_by = section_block(text, "## Used by")
        for target in wikilink_targets(used_by):
            page = _resolve_wikilink_target(root, target)
            if page is not None:
                _extend_unique(pages, [page])
    return pages


def _resolve_wikilink_target(root: Path, target: str) -> Path | None:
    normalized = normalize_wikilink_target(target)
    candidate = root / normalized

    if candidate.is_file():
        return candidate.resolve()

    if candidate.suffix:
        return candidate.resolve() if candidate.exists() else None

    for suffix in _MARKDOWN_SUFFIXES:
        with_suffix = candidate.with_suffix(suffix)
        if with_suffix.is_file():
            return with_suffix.resolve()

    return None


def _extend_unique(paths: list[Path], new_paths: Iterable[Path]) -> None:
    seen = {path.resolve() for path in paths}
    for path in new_paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        paths.append(resolved)
