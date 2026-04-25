#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import date
import sys

ROOT_DEFAULT = Path('/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki')

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
    return '-'.join(text.lower().strip().split())


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/create_ingest_report.py <title> [llm-wiki-root]')
        return 2
    title = sys.argv[1].strip()
    root = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else ROOT_DEFAULT
    today = date.today()
    date_iso = today.isoformat()
    slug = slugify(title)
    out = root / 'wiki' / 'reports' / f'{date_iso}-{slug}-ingest.md'
    if out.exists():
        print(f'ERROR: report already exists: {out}')
        return 1
    out.write_text(TEMPLATE.format(date_compact=date_iso.replace('-', ''), slug_upper=slug.upper().replace('-', '_'), date_iso=date_iso, title=title), encoding='utf-8')
    print(f'Created ingest report scaffold: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
