#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import date
import sys

TEMPLATE = '''---
type: report
id: RPT-{date_compact}-{slug_upper}
title: {date_iso} {title}
agent: aristotle
subagent: librarian
cover:
status: active
claim_type: synthesis
confidence: medium
created: {date_iso}
updated: {date_iso}
tags: [report, audit, llm-wiki]
sources: []
---

# {date_iso} {title}

## Scope
- <what was audited>

## Structural Health
- <broken links / missing sections / thin pages>
- <source-card hygiene>

## Knowledge Fidelity
- <can common questions be answered from wiki without reopening raw?>
- <do raw pointers actually support the page conclusions?>
- <any source laundering: source card cited as evidence instead of raw?>
- <any summary-as-source behavior or wiki page over-relying on second-order summaries?>

## Raw Pointer Coverage
- <what now points directly to raw>
- <what still lacks direct raw support>
- <where claim-level raw pointers are still missing>

## Remaining Gaps
- <uncompiled raw>
- <weak evidence areas>
- <thin pages or unresolved conflicts>

## Verdict
- <does the system meet “日常使用看 wiki，必要时回 raw”?>
'''


def slugify(text: str) -> str:
    return '-'.join(text.lower().strip().split())


def _looks_like_llm_wiki_root(root: Path) -> bool:
    return (root / 'raw').is_dir() and (root / 'wiki').is_dir()


def _resolve_root_from_cwd() -> Path | None:
    cwd = Path.cwd().resolve()
    return cwd if _looks_like_llm_wiki_root(cwd) else None


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/create_audit_report.py <title> [llm-wiki-root]')
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
    out = root / 'wiki' / 'reports' / f'{date_iso}-{slug}.md'
    if out.exists():
        print(f'ERROR: report already exists: {out}')
        return 1
    out.write_text(TEMPLATE.format(date_compact=date_iso.replace('-', ''), slug_upper=slug.upper().replace('-', '_'), date_iso=date_iso, title=title), encoding='utf-8')
    print(f'Created audit report scaffold: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
