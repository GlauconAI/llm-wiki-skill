#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
VENDOR_DIR = ROOT_DIR / ".vendor"
if VENDOR_DIR.exists() and str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

from llm_wiki_maintainer.runtime.api import LlmWikiRuntime
from llm_wiki_maintainer.registry import resolve_wiki_root


def main() -> int:
    if len(sys.argv) >= 2:
        root_arg = sys.argv[1]
    else:
        root_arg = None

    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/wiki_status.py [llm-wiki-root]")
        return 2
    runtime = LlmWikiRuntime(root)
    summary = runtime.status()
    print(f"root: {summary.root}")
    print(f"pages: {summary.page_count}")
    print(f"source_cards: {summary.source_card_count}")
    print(f"raw: {summary.raw_count}")
    print(f"ingest_jobs: {summary.ingest_jobs}")
    print(f"review_items: {summary.review_items}")
    print(f"research_tasks: {summary.research_tasks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
