from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.links import (
    RAW_WIKILINK_RE,
    rel,
    section_block,
    section_lines,
    target_exists,
    wikilink_targets,
)
from llm_wiki_maintainer.references import (
    COMPILED_FACT_TYPES,
    compute_used_by,
    declared_used_by,
    parse_frontmatter_type,
    parse_source_id,
)

SOURCE_REQUIRED = [
    "## Location",
    "## Type",
    "## Coverage",
    "## Used by",
    "## Key Sections",
    "## Notes",
]
WIKI_REQUIRED = [
    "## TL;DR",
    "## Core Knowledge",
    "## Decision-Relevant Details",
    "## Constraints / Exceptions",
    "## Related Pages",
    "## Raw Source Pointers",
]
PLACEHOLDER_PATTERNS = [
    re.compile(r"^<.+>$"),
    re.compile(r"^一句话结论$"),
    re.compile(r"^核心知识$"),
    re.compile(r"^影响判断的关键细节$"),
    re.compile(r"^限制、边界、例外$"),
    re.compile(r"^重要数字、日期、参数、定义$"),
    re.compile(r"^不确定性或冲突$"),
]
FORBIDDEN_SOURCE_HEADINGS = {
    "## TL;DR",
    "## Core Knowledge",
    "## Decision-Relevant Details",
    "## Procedures / Steps",
    "## Constraints / Exceptions",
    "## Numbers / Facts",
    "## Uncertainty / Conflicts",
    "## Related Pages",
    "## Raw Source Pointers",
    "## Thesis",
    "## Key Claims",
    "## Evidence / Data",
}
CLAIM_LEVEL_SECTIONS = [
    "## Core Knowledge",
    "## Decision-Relevant Details",
    "## Constraints / Exceptions",
    "## Numbers / Facts",
    "## Uncertainty / Conflicts",
]


@dataclass(frozen=True)
class LintProblem:
    path: str
    message: str
    severity: str = "error"


def body_without_frontmatter(text: str) -> str:
    try:
        return load_frontmatter(text).body
    except ValueError:
        return text


def frontmatter_error(text: str) -> str | None:
    try:
        load_frontmatter(text)
    except ValueError as exc:
        return str(exc)
    return None


def nonempty_lines(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def substantive_lines(lines: list[str]) -> list[str]:
    out = []
    for raw in nonempty_lines(lines):
        line = re.sub(r"^[-*]\s*", "", raw)
        line = re.sub(r"^\d+\.\s*", "", line)
        if any(pattern.fullmatch(line) for pattern in PLACEHOLDER_PATTERNS):
            continue
        if line.startswith("<") and line.endswith(">"):
            continue
        out.append(line)
    return out


def contains_placeholder_only(text: str, heading: str) -> bool:
    lines = section_lines(text, heading)
    if not nonempty_lines(lines):
        return True
    return not substantive_lines(lines)


def count_bullets(lines: list[str]) -> int:
    return sum(
        1
        for line in nonempty_lines(lines)
        if line.startswith(("-", "*")) or re.match(r"^\d+\.", line)
    )


def section_char_count(text: str, heading: str) -> int:
    return len(" ".join(substantive_lines(section_lines(text, heading))))


def has_raw_pointer(lines: list[str]) -> bool:
    return any(RAW_WIKILINK_RE.search(line) for line in lines)


def claim_level_pointer_count(text: str) -> int:
    return sum(
        1 for heading in CLAIM_LEVEL_SECTIONS if has_raw_pointer(section_lines(text, heading))
    )


def page_has_template_only_sections(text: str) -> bool:
    checked = 0
    placeholder_only = 0
    for heading in [
        "## TL;DR",
        "## Core Knowledge",
        "## Decision-Relevant Details",
        "## Constraints / Exceptions",
    ]:
        if heading in text:
            checked += 1
            if contains_placeholder_only(text, heading):
                placeholder_only += 1
    return checked > 0 and placeholder_only == checked


def is_thin_page(text: str) -> list[str]:
    core_knowledge = section_lines(text, "## Core Knowledge")
    details = section_lines(text, "## Decision-Relevant Details")
    constraints = section_lines(text, "## Constraints / Exceptions")
    pointers = section_lines(text, "## Raw Source Pointers")
    issues = []
    if not substantive_lines(core_knowledge) or section_char_count(text, "## Core Knowledge") < 80:
        issues.append("Core Knowledge empty or too short")
    if not substantive_lines(details) or section_char_count(text, "## Decision-Relevant Details") < 60:
        issues.append("Decision-Relevant Details missing or too short")
    if not substantive_lines(constraints) or section_char_count(text, "## Constraints / Exceptions") < 30:
        issues.append("Constraints / Exceptions missing or too short")
    if not has_raw_pointer(pointers):
        issues.append("Raw Source Pointers missing")
    if page_has_template_only_sections(text):
        issues.append("page appears to contain only template headings/placeholders")
    return issues


def parse_index_links(index_text: str) -> set[str]:
    return set(wikilink_targets(index_text))


def source_card_summary_issues(text: str) -> list[str]:
    issues = []
    body = body_without_frontmatter(text)
    nonempty = [line for line in body.splitlines() if line.strip()]
    if len(nonempty) > 40:
        issues.append("source card too long; may contain summary-layer content")
    if len(body) > 2400:
        issues.append("source card body too long; may contain knowledge prose")
    for heading in FORBIDDEN_SOURCE_HEADINGS:
        if heading in text:
            issues.append(f"source card contains forbidden knowledge-layer heading: {heading}")
    notes = section_lines(text, "## Notes")
    long_note_lines = [line for line in substantive_lines(notes) if len(line) > 180]
    if len(long_note_lines) >= 2:
        issues.append("source card notes contain long prose; may be summary-as-source")
    coverage = section_lines(text, "## Coverage")
    if count_bullets(coverage) > 8:
        issues.append("source card coverage too long; tighten to navigation topics only")
    key_sections = section_lines(text, "## Key Sections")
    if count_bullets(key_sections) > 10:
        issues.append("source card key sections too long; likely acting as summary")
    prose_like = 0
    for heading in ["## Coverage", "## Key Sections", "## Notes"]:
        for line in substantive_lines(section_lines(text, heading)):
            if len(line) > 140 and RAW_WIKILINK_RE.search(line) is None:
                prose_like += 1
    if prose_like >= 3:
        issues.append("source card contains too much prose-like content")
    return issues


def raw_pointer_block_issues(text: str) -> list[str]:
    issues = []
    if "## Raw Source Pointers" not in text:
        return issues
    block = section_block(text, "## Raw Source Pointers")
    ptr_count = 0
    for line in block.splitlines():
        if line.strip().startswith("- "):
            ptr_count += 1
        if "/raw/sources/" in line and "[[" not in line and "](" not in line:
            issues.append("non-clickable raw source pointer")
    if ptr_count < 1:
        issues.append("compiled page missing raw source pointer bullets")
    return issues


def lint_root(root: Path) -> list[LintProblem]:
    wiki_dir = root / "wiki"
    raw_dir = root / "raw"
    index_path = root / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    index_links = parse_index_links(index_text)
    problems: list[LintProblem] = []
    actual_compiled_pages: set[str] = set()
    declared_used_by_by_card = declared_used_by(root)
    actual_usage_by_card = compute_used_by(root)

    def add_problem(path: str, message: str) -> None:
        problems.append(LintProblem(path=path, message=message))

    for path in sorted((wiki_dir / "sources").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        card_ref = rel(path, root)
        error = frontmatter_error(text)
        if error:
            add_problem(card_ref, f"malformed frontmatter: {error}")
        if parse_source_id(text):
            actual_usage_by_card.setdefault(card_ref, set())
        for section in SOURCE_REQUIRED:
            if section not in text:
                add_problem(card_ref, f"missing source-card section: {section}")
        for issue in source_card_summary_issues(text):
            add_problem(card_ref, issue)
        for line in text.splitlines():
            if "/raw/sources/" in line and "[[" not in line and "](" not in line:
                add_problem(card_ref, "plain raw source path found")
        for target in wikilink_targets(text):
            if target.startswith("http://") or target.startswith("https://"):
                continue
            if not target_exists(root, target):
                add_problem(card_ref, f"broken wikilink target: {target}")

    for path in sorted(wiki_dir.rglob("*.md")):
        page_ref = rel(path, root)
        if "/sources/" in page_ref:
            continue
        text = path.read_text(encoding="utf-8")
        error = frontmatter_error(text)
        if error:
            add_problem(page_ref, f"malformed frontmatter: {error}")
        page_type = parse_frontmatter_type(text)

        if page_type in COMPILED_FACT_TYPES:
            actual_compiled_pages.add(page_ref[:-3])
            for section in WIKI_REQUIRED:
                if section not in text:
                    add_problem(page_ref, f"missing compiled-page section: {section}")
            for issue in is_thin_page(text):
                add_problem(page_ref, issue)
            if claim_level_pointer_count(text) < 1:
                add_problem(page_ref, "missing claim-level raw pointer support in key sections")

        for issue in raw_pointer_block_issues(text):
            add_problem(page_ref, issue)
        for line in text.splitlines():
            if "/raw/sources/" in line and "[[" not in line and "](" not in line:
                add_problem(page_ref, "plain raw source path found")
        for target in wikilink_targets(text):
            if target.startswith("http://") or target.startswith("https://"):
                continue
            if not target_exists(root, target):
                add_problem(page_ref, f"broken wikilink target: {target}")

    for page in sorted(actual_compiled_pages):
        if page == "wiki/overview":
            continue
        if page not in index_links:
            add_problem("index.md", f"missing index link for {page}")

    for source_card, declared in sorted(declared_used_by_by_card.items()):
        actual = actual_usage_by_card.get(source_card, set())
        missing = sorted(actual - declared)
        extra = sorted(declared - actual)
        if missing:
            add_problem(source_card, f"Used by missing actual references: {missing}")
        if extra:
            add_problem(source_card, f"Used by lists non-actual references: {extra}")

    for path in sorted(raw_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        raw_ref = rel(path, root)
        error = frontmatter_error(text)
        if error:
            add_problem(raw_ref, f"malformed frontmatter: {error}")
        for target in wikilink_targets(text):
            if target.startswith("http://") or target.startswith("https://"):
                continue
            if not target_exists(root, target):
                add_problem(raw_ref, f"broken wikilink target: {target}")

    return problems
