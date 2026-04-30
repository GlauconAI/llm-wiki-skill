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
from llm_wiki_maintainer.registry import looks_like_wiki_root, resolve_wiki_root


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/create_digest.py <query> [llm-wiki-root] [title]")
        return 2

    query = sys.argv[1]
    root_arg = None
    title = None
    if len(sys.argv) >= 3:
        candidate = sys.argv[2]
        if looks_like_wiki_root(candidate):
            root_arg = candidate
            title = sys.argv[3] if len(sys.argv) > 3 else None
        else:
            title = candidate
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/create_digest.py <query> [llm-wiki-root] [title]")
        return 2
    digest = LlmWikiRuntime(root).create_digest(query, title=title)
    print(f"created digest {digest.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
