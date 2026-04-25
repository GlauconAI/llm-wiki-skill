#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re
import sys

ROOT_DEFAULT = Path('/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n?', re.S)
FIELD_RE = re.compile(r'^([A-Za-z0-9_-]+):\s*(.+)$', re.M)
SRC_ID_RE = re.compile(r'(SRC-\d+)', re.I)


def slugify(text: str) -> str:
    text = text.strip().lower().replace('_', '-')
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9\-\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'untitled-source'


def frontmatter_block(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ''


def body_without_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end():] if m else text


def parse_frontmatter_value(text: str, key: str):
    block = frontmatter_block(text)
    for field, value in FIELD_RE.findall(block):
        if field == key:
            return value.strip().strip('"\'')
    return None


def source_id_from_raw(raw_file: Path, text: str) -> str | None:
    for candidate in (parse_frontmatter_value(text, 'source_id'), parse_frontmatter_value(text, 'id')):
        if candidate and SRC_ID_RE.fullmatch(candidate):
            return candidate.upper()
    m = SRC_ID_RE.search(raw_file.name)
    return m.group(1).upper() if m else None


def title_from_raw(text: str, fallback: str) -> str:
    for candidate in (parse_frontmatter_value(text, 'title'), parse_frontmatter_value(text, 'name')):
        if candidate:
            return candidate
    for line in body_without_frontmatter(text).splitlines()[:30]:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        if line:
            return line[:80].strip()
    return fallback


def detect_type(raw_file: Path, text: str) -> str:
    suffix = raw_file.suffix.lower()
    body = body_without_frontmatter(text)
    source = parse_frontmatter_value(text, 'source') or ''
    if suffix == '.pdf':
        return 'pdf'
    if suffix in {'.txt', '.log'}:
        return 'transcript / text'
    if source.startswith('http') or 'Source URL:' in body or 'http://' in body or 'https://' in body:
        return 'web / md note'
    if '##' in body or '# ' in body:
        return 'md / note'
    return 'note'


def guess_key_sections(text: str):
    sections = []
    for line in body_without_frontmatter(text).splitlines()[:120]:
        s = line.strip()
        if s.startswith('## '):
            sections.append(s[3:].strip())
        elif s.startswith('### '):
            sections.append(s[4:].strip())
        if len(sections) >= 6:
            break
    if not sections:
        sections = ['Opening section', 'Most decision-relevant section']
    return sections


def guess_coverage(raw_file: Path, title: str):
    keywords = parse_frontmatter_value(raw_file.read_text(encoding='utf-8', errors='replace'), 'keywords')
    base = slugify(raw_file.stem.replace('SRC-', '').split('-', 1)[-1])
    parts = [p for p in base.split('-') if p]
    items = []
    if keywords and keywords.startswith('[') and keywords.endswith(']'):
        inner = keywords[1:-1].strip()
        items.extend(part.strip().strip("'\"") for part in inner.split(',') if part.strip())
    if len(parts) >= 2:
        items.insert(0, ' '.join(parts[:2]))
    items.append(title)
    deduped = []
    seen = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped[:4] if deduped else [title, base]


def existing_card_for_raw(root: Path, rel_raw: str):
    needle = f'|/{rel_raw}]]'
    for p in sorted((root / 'wiki' / 'sources').glob('*.md')):
        text = p.read_text(encoding='utf-8', errors='replace')
        if needle in text:
            return p
    return None


def source_kind(text: str, source_type: str) -> str:
    source = (parse_frontmatter_value(text, 'source') or '').strip()
    agent = (parse_frontmatter_value(text, 'agent') or '').strip()
    if source == 'internal-chat' or agent:
        return 'internal-note'
    if source.startswith('http') or source_type.startswith('web'):
        return 'article'
    return 'note'


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/create_source_card.py <raw-file> [llm-wiki-root]')
        return 2

    raw_file = Path(sys.argv[1]).expanduser()
    root = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else ROOT_DEFAULT

    if not raw_file.exists():
        print(f'ERROR: raw file not found: {raw_file}')
        return 2

    try:
        relative = raw_file.relative_to(root)
    except ValueError:
        print(f'ERROR: raw file must live under llm-wiki root: {root}')
        return 2

    if not str(relative).startswith('raw/'):
        print('ERROR: raw file must be inside the raw/ tree')
        return 2

    rel_raw = relative.as_posix()
    existing = existing_card_for_raw(root, rel_raw)
    if existing:
        print(f'Existing source card: {existing}')
        return 0

    text = raw_file.read_text(encoding='utf-8', errors='replace')
    title = title_from_raw(text, raw_file.stem)
    sid = source_id_from_raw(raw_file, text)
    default_name = slugify(raw_file.stem.replace('SRC-', '').split('-', 1)[-1]) + '.md'
    out = root / 'wiki' / 'sources' / default_name
    i = 2
    while out.exists():
        out = root / 'wiki' / 'sources' / f'{default_name[:-3]}-{i}.md'
        i += 1

    stem = relative.with_suffix('').as_posix()
    source_type = detect_type(raw_file, text)
    coverage = guess_coverage(raw_file, title)
    key_sections = guess_key_sections(text)
    kind = source_kind(text, source_type)
    source_refs = f'[{sid}]' if sid else '[]'
    id_line = f'id: {sid}\n' if sid else ''
    tag_values = ['source'] + [part for part in slugify(title).split('-') if part]
    tag_line = ', '.join(tag_values)
    frontmatter = (
        '---\n'
        'type: source\n'
        f'{id_line}'
        f'title: {title}\n'
        'agent: aristotle\n'
        'subagent: source-ingest\n'
        'cover:\n'
        'status: active\n'
        'claim_type: fact\n'
        'confidence: medium\n'
        f'source_kind: {kind}\n'
        'created: 2026-04-24\n'
        'updated: 2026-04-24\n'
        f'tags: [{tag_line}]\n'
        f'sources: {source_refs}\n'
        '---\n'
    )
    content = (
        frontmatter +
        f'# Source: {title}\n\n'
        f'## Location\n'
        f'[[{stem}|/{rel_raw}]]\n\n'
        f'## Type\n'
        f'{source_type}\n\n'
        f'## Coverage\n' + ''.join(f'- {item}\n' for item in coverage) + '\n'
        f'## Used by\n'
        f'- _Fill after compiled pages are created or updated._\n\n'
        f'## Key Sections\n' + ''.join(f'- {item}\n' for item in key_sections) + '\n'
        f'## Notes\n'
        f'- Auto-generated skeleton. Review coverage and key sections before relying on this card.\n'
        f'- Navigation-only notes. Do not turn this source card into a summary page.\n'
    )
    out.write_text(content, encoding='utf-8')
    print(f'Created source card: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
