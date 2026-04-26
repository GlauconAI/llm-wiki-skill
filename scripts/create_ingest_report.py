#!/usr/bin/env python3
from __future__ import annotations
from datetime import date
from pathlib import Path
import re
import sys

TEMPLATE = '''---
type: report
id: ING-{date_compact}-{slug_upper}
title: {date_iso} {title}
agent: aristotle
subagent: curator
cover:
status: active
claim_type: synthesis
confidence: medium
created: {date_iso}
updated: {date_iso}
tags: [report, ingest, llm-wiki]
sources: []
---

# {date_iso} {title}

## Raw Reviewed
- <raw files reviewed>

## Pages Added or Updated
- <compiled pages>
- <source cards>

## Claims Absorbed
- <claim or structure now reflected in wiki> -> [[wiki/...]]

## Not Absorbed
- <raw item not absorbed>
- <why excluded: off-scope / low confidence / duplicate / weakly evidenced / waiting for more raw>

## Follow-up
- <additional raw needed>
- <pages still thin>
- <unresolved conflicts>
'''


def slugify(text: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug or 'report'


def _looks_like_llm_wiki_root(root: Path) -> bool:
    return (root / 'raw').is_dir() and (root / 'wiki').is_dir()


def _resolve_root_from_cwd() -> Path | None:
    cwd = Path.cwd().resolve()
    return cwd if _looks_like_llm_wiki_root(cwd) else None


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/create_ingest_report.py <title> [llm-wiki-root]')
        return 2
    title = sys.argv[1].strip()
    if len(sys.argv) > 2:
        root = Path(sys.argv[2]).expanduser().resolve()
        if not root.exists():
            print(f'ERROR: root not found: {root}')
            return 2
    else:
        root = _resolve_root_from_cwd()
        if root is None:
            print('ERROR: current directory does not look like an llm-wiki root; pass an explicit root argument.')
            return 2
    today = date.today()
    date_iso = today.isoformat()
    slug = slugify(title)
    report_dir = root / 'wiki' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f'{date_iso}-{slug}-ingest.md'
    if out.exists():
        print(f'ERROR: report already exists: {out}')
        return 1
    out.write_text(TEMPLATE.format(date_compact=date_iso.replace('-', ''), slug_upper=slug.upper().replace('-', '_'), date_iso=date_iso, title=title), encoding='utf-8')
    print(f'Created ingest report scaffold: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
