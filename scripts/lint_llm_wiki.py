#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re
import sys

ROOT_DEFAULT = Path('/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki')
SOURCE_REQUIRED = ['## Location', '## Type', '## Coverage', '## Used by', '## Key Sections', '## Notes']
WIKI_REQUIRED = [
    '## TL;DR',
    '## Core Knowledge',
    '## Decision-Relevant Details',
    '## Constraints / Exceptions',
    '## Related Pages',
    '## Raw Source Pointers',
]
COMPILED_FACT_TYPES = {'overview', 'concept', 'entity', 'topic'}
WIKILINK_RE = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]')
RAW_WIKILINK_RE = re.compile(r'\[\[(raw/sources/[^\]|]+)(?:\|[^\]]+)?\]\]')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n?', re.S)
TYPE_RE = re.compile(r'^type:\s*(.+)$', re.M)
SOURCE_ID_RE = re.compile(r'^id:\s*(SRC-\d+)', re.M)
SOURCES_FIELD_RE = re.compile(r'^sources:\s*(.+)$', re.M)
SOURCE_LINK_RE = re.compile(r'\[\[(wiki/[^\]|]+)')
PLACEHOLDER_PATTERNS = [
    re.compile(r'^<.+>$'),
    re.compile(r'^一句话结论$'),
    re.compile(r'^核心知识$'),
    re.compile(r'^影响判断的关键细节$'),
    re.compile(r'^限制、边界、例外$'),
    re.compile(r'^重要数字、日期、参数、定义$'),
    re.compile(r'^不确定性或冲突$'),
]
FORBIDDEN_SOURCE_HEADINGS = {
    '## TL;DR',
    '## Core Knowledge',
    '## Decision-Relevant Details',
    '## Procedures / Steps',
    '## Constraints / Exceptions',
    '## Numbers / Facts',
    '## Uncertainty / Conflicts',
    '## Related Pages',
    '## Raw Source Pointers',
    '## Thesis',
    '## Key Claims',
    '## Evidence / Data',
}
CLAIM_LEVEL_SECTIONS = [
    '## Core Knowledge',
    '## Decision-Relevant Details',
    '## Constraints / Exceptions',
    '## Numbers / Facts',
    '## Uncertainty / Conflicts',
]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def frontmatter_block(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ''


def body_without_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end():] if m else text


def parse_frontmatter_type(text: str):
    m = TYPE_RE.search(frontmatter_block(text))
    return m.group(1).strip() if m else None


def parse_source_id(text: str):
    m = SOURCE_ID_RE.search(frontmatter_block(text))
    return m.group(1) if m else None


def parse_sources_field(text: str):
    m = SOURCES_FIELD_RE.search(frontmatter_block(text))
    if not m:
        return []
    raw = m.group(1).strip()
    if raw.startswith('[') and raw.endswith(']'):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("'\"") for part in inner.split(',') if part.strip()]
    return []


def target_exists(base: Path, target: str) -> bool:
    cand = base / target
    return cand.exists() or cand.with_suffix('.md').exists()


def section_block(text: str, heading: str) -> str:
    marker = heading + '\n'
    if marker not in text:
        return ''
    block = text.split(marker, 1)[1]
    out = []
    for line in block.splitlines():
        if line.startswith('## '):
            break
        out.append(line)
    return '\n'.join(out).strip()


def section_lines(text: str, heading: str):
    return [line.rstrip() for line in section_block(text, heading).splitlines()]


def nonempty_lines(lines):
    return [line.strip() for line in lines if line.strip()]


def substantive_lines(lines):
    out = []
    for raw in nonempty_lines(lines):
        line = re.sub(r'^[-*]\s*', '', raw)
        line = re.sub(r'^\d+\.\s*', '', line)
        if any(p.fullmatch(line) for p in PLACEHOLDER_PATTERNS):
            continue
        if line.startswith('<') and line.endswith('>'):
            continue
        out.append(line)
    return out


def contains_placeholder_only(text: str, heading: str) -> bool:
    lines = section_lines(text, heading)
    if not nonempty_lines(lines):
        return True
    return not substantive_lines(lines)


def count_bullets(lines):
    return sum(1 for line in nonempty_lines(lines) if line.startswith(('-', '*')) or re.match(r'^\d+\.', line))


def section_char_count(text: str, heading: str) -> int:
    return len(' '.join(substantive_lines(section_lines(text, heading))))


def has_raw_pointer(lines) -> bool:
    return any(RAW_WIKILINK_RE.search(line) for line in lines)


def claim_level_pointer_count(text: str) -> int:
    return sum(1 for heading in CLAIM_LEVEL_SECTIONS if has_raw_pointer(section_lines(text, heading)))


def page_has_template_only_sections(text: str) -> bool:
    checked = 0
    placeholder_only = 0
    for heading in ['## TL;DR', '## Core Knowledge', '## Decision-Relevant Details', '## Constraints / Exceptions']:
        if heading in text:
            checked += 1
            if contains_placeholder_only(text, heading):
                placeholder_only += 1
    return checked > 0 and placeholder_only == checked


def is_thin_page(text: str):
    ck_lines = section_lines(text, '## Core Knowledge')
    drd_lines = section_lines(text, '## Decision-Relevant Details')
    cex_lines = section_lines(text, '## Constraints / Exceptions')
    pointer_lines = section_lines(text, '## Raw Source Pointers')
    issues = []
    if not substantive_lines(ck_lines) or section_char_count(text, '## Core Knowledge') < 80:
        issues.append('Core Knowledge empty or too short')
    if not substantive_lines(drd_lines) or section_char_count(text, '## Decision-Relevant Details') < 60:
        issues.append('Decision-Relevant Details missing or too short')
    if not substantive_lines(cex_lines) or section_char_count(text, '## Constraints / Exceptions') < 30:
        issues.append('Constraints / Exceptions missing or too short')
    if not has_raw_pointer(pointer_lines):
        issues.append('Raw Source Pointers missing')
    if page_has_template_only_sections(text):
        issues.append('page appears to contain only template headings/placeholders')
    return issues


def parse_index_links(index_text: str):
    return set(WIKILINK_RE.findall(index_text))


def used_by_links(text: str):
    return set(SOURCE_LINK_RE.findall(section_block(text, '## Used by')))


def source_card_summary_issues(text: str):
    issues = []
    body = body_without_frontmatter(text)
    nonempty = [line for line in body.splitlines() if line.strip()]
    if len(nonempty) > 40:
        issues.append('source card too long; may contain summary-layer content')
    if len(body) > 2400:
        issues.append('source card body too long; may contain knowledge prose')
    for heading in FORBIDDEN_SOURCE_HEADINGS:
        if heading in text:
            issues.append(f'source card contains forbidden knowledge-layer heading: {heading}')
    notes = section_lines(text, '## Notes')
    long_note_lines = [line for line in substantive_lines(notes) if len(line) > 180]
    if len(long_note_lines) >= 2:
        issues.append('source card notes contain long prose; may be summary-as-source')
    coverage = section_lines(text, '## Coverage')
    if count_bullets(coverage) > 8:
        issues.append('source card coverage too long; tighten to navigation topics only')
    key_sections = section_lines(text, '## Key Sections')
    if count_bullets(key_sections) > 10:
        issues.append('source card key sections too long; likely acting as summary')
    prose_like = 0
    for heading in ['## Coverage', '## Key Sections', '## Notes']:
        for line in substantive_lines(section_lines(text, heading)):
            if len(line) > 140 and RAW_WIKILINK_RE.search(line) is None:
                prose_like += 1
    if prose_like >= 3:
        issues.append('source card contains too much prose-like content')
    return issues


def raw_pointer_block_issues(text: str):
    issues = []
    if '## Raw Source Pointers' not in text:
        return issues
    block = text.split('## Raw Source Pointers', 1)[1]
    ptr_count = 0
    for line in block.splitlines()[1:]:
        if line.startswith('## '):
            break
        if line.strip().startswith('- '):
            ptr_count += 1
        if '/raw/sources/' in line and '[[' not in line and '](' not in line:
            issues.append('non-clickable raw source pointer')
    if ptr_count < 1:
        issues.append('compiled page missing raw source pointer bullets')
    return issues


def main() -> int:
    root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else ROOT_DEFAULT
    wiki_dir = root / 'wiki'
    raw_dir = root / 'raw'
    problems = []

    if not root.exists():
        print(f'ERROR: root not found: {root}')
        return 2

    index_path = root / 'index.md'
    index_text = index_path.read_text(encoding='utf-8') if index_path.exists() else ''
    index_links = parse_index_links(index_text)
    actual_compiled_pages = set()

    source_card_by_id = {}
    declared_used_by_by_card = {}
    for path in sorted((wiki_dir / 'sources').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        sid = parse_source_id(text)
        if sid:
            source_card_by_id[sid] = rel(path, root)
        declared_used_by_by_card[rel(path, root)] = used_by_links(text)

    actual_usage_by_card = {card: set() for card in declared_used_by_by_card}

    for path in sorted(wiki_dir.rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        r = rel(path, root)
        page_type = parse_frontmatter_type(text)

        if '/sources/' in r:
            for sec in SOURCE_REQUIRED:
                if sec not in text:
                    problems.append((r, f'missing source-card section: {sec}'))
            for issue in source_card_summary_issues(text):
                problems.append((r, issue))
        else:
            if page_type in COMPILED_FACT_TYPES:
                actual_compiled_pages.add(r[:-3])
                for sec in WIKI_REQUIRED:
                    if sec not in text:
                        problems.append((r, f'missing compiled-page section: {sec}'))
                for issue in is_thin_page(text):
                    problems.append((r, issue))
                if claim_level_pointer_count(text) < 1:
                    problems.append((r, 'missing claim-level raw pointer support in key sections'))
            for issue in raw_pointer_block_issues(text):
                problems.append((r, issue))

        for line in text.splitlines():
            if '/raw/sources/' in line and '[[' not in line and '](' not in line:
                problems.append((r, 'plain raw source path found'))

        for target in WIKILINK_RE.findall(text):
            if target.startswith('http://') or target.startswith('https://'):
                continue
            if not target_exists(root, target):
                problems.append((r, f'broken wikilink target: {target}'))

        if page_type in COMPILED_FACT_TYPES:
            for sid in parse_sources_field(text):
                card = source_card_by_id.get(sid)
                if card:
                    actual_usage_by_card.setdefault(card, set()).add(r[:-3])

    for page in sorted(actual_compiled_pages):
        if page == 'wiki/overview':
            continue
        if page not in index_links:
            problems.append(('index.md', f'missing index link for {page}'))

    for source_card, declared in sorted(declared_used_by_by_card.items()):
        actual = actual_usage_by_card.get(source_card, set())
        if declared != actual:
            missing = sorted(actual - declared)
            extra = sorted(declared - actual)
            if missing:
                problems.append((source_card, f'Used by missing actual references: {missing}'))
            if extra:
                problems.append((source_card, f'Used by lists non-actual references: {extra}'))

    for path in sorted(raw_dir.rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        r = rel(path, root)
        for target in WIKILINK_RE.findall(text):
            if target.startswith('http://') or target.startswith('https://'):
                continue
            if not target_exists(root, target):
                problems.append((r, f'broken wikilink target: {target}'))

    if problems:
        print(f'LLM Wiki lint: FAIL ({len(problems)} issue(s))')
        for file, msg in problems:
            print(f'- {file}: {msg}')
        return 1

    print('LLM Wiki lint: PASS')
    print(f'Checked root: {root}')
    print('Validated source-card hygiene, compiled-page density, claim-level and page-level raw pointers, wikilink targets, Used by consistency, and index coverage.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
