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
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/delete_source.py <raw-file> [llm-wiki-root] [--apply]")
        return 2

    raw_path = sys.argv[1]
    root_arg = None
    extra_args = sys.argv[2:]
    if extra_args and extra_args[0] != "--apply":
        root_arg = extra_args[0]
        extra_args = extra_args[1:]
    apply = "--apply" in extra_args
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/delete_source.py <raw-file> [llm-wiki-root] [--apply]")
        return 2
    result = LlmWikiRuntime(root).delete_source(raw_path, apply=apply)

    print(f"applied: {result.applied}")
    print(f"source_cards_to_delete: {len(result.impact.source_cards_to_delete)}")
    print(f"pages_to_update: {len(result.impact.pages_to_update)}")
    for page in result.impact.pages_to_update:
        print(f"page: {page}")
    for broken in result.impact.broken_links:
        print(f"broken: {broken}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
