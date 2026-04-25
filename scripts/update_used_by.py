#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re
import sys

ROOT_DEFAULT = Path('/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.S)
TYPE_RE = re.compile(r'^type:\s*(.+)$', re.M)
SOURCE_ID_RE = re.compile(r'^id:\s*(SRC-\d+)', re.M)
SOURCES_FIELD_RE = re.compile(r'^sources:\s*(.+)$', re.M)
COMPILED_FACT_TYPES = {'overview', 'concept', 'entity', 'topic'}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def frontmatter_block(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ''


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


def section_bounds(text: str, heading: str):
    marker = heading + '\n'
    start = text.find(marker)
    if start == -1:
        return None
    body_start = start + len(marker)
    rest = text[body_start:]
    next_heading = rest.find('\n## ')
    end = len(text) if next_heading == -1 else body_start + next_heading + 1
    return body_start, end


def main() -> int:
    root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else ROOT_DEFAULT
    wiki_dir = root / 'wiki'
    if not root.exists():
        print(f'ERROR: root not found: {root}')
        return 2

    source_card_by_id = {}
    for path in sorted((wiki_dir / 'sources').glob('*.md')):
        sid = parse_source_id(path.read_text(encoding='utf-8'))
        if sid:
            source_card_by_id[sid] = path

    usage = {path: set() for path in source_card_by_id.values()}

    for path in sorted(wiki_dir.rglob('*.md')):
        if '/sources/' in rel(path, root):
            continue
        text = path.read_text(encoding='utf-8')
        page_type = parse_frontmatter_type(text)
        if page_type not in COMPILED_FACT_TYPES:
            continue
        page_ref = rel(path, root)[:-3]
        for sid in parse_sources_field(text):
            card = source_card_by_id.get(sid)
            if card:
                usage[card].add(page_ref)

    updated = 0
    for card, refs in sorted(usage.items()):
        text = card.read_text(encoding='utf-8')
        bounds = section_bounds(text, '## Used by')
        if not bounds:
            continue
        start, end = bounds
        body = ''.join(f'- [[{ref}]]\n' for ref in sorted(refs)) if refs else '- _No compiled wiki pages currently reference this source._\n'
        new_text = text[:start] + body + text[end:]
        if new_text != text:
            card.write_text(new_text, encoding='utf-8')
            updated += 1
            print(f'updated {card}')

    print(f'Updated {updated} source card(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
