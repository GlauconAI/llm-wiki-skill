#!/usr/bin/env python3
from __future__ import annotations
from datetime import date
from pathlib import Path
import re
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

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VENDOR_ROOT = REPO_ROOT / ".vendor"
if VENDOR_ROOT.exists() and str(VENDOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VENDOR_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from llm_wiki_maintainer.registry import resolve_wiki_root


def slugify(text: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug or 'report'

def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/create_audit_report.py <title> [llm-wiki-root]')
        return 2
    title = sys.argv[1].strip()
    try:
        root = resolve_wiki_root(root=sys.argv[2] if len(sys.argv) > 2 else None)
    except ValueError:
        print('Usage: python3 scripts/create_audit_report.py <title> [llm-wiki-root]')
        return 2
    today = date.today()
    date_iso = today.isoformat()
    slug = slugify(title)
    report_dir = root / 'wiki' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f'{date_iso}-{slug}.md'
    if out.exists():
        print(f'ERROR: report already exists: {out}')
        return 1
    out.write_text(TEMPLATE.format(date_compact=date_iso.replace('-', ''), slug_upper=slug.upper().replace('-', '_'), date_iso=date_iso, title=title), encoding='utf-8')
    print(f'Created audit report scaffold: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
