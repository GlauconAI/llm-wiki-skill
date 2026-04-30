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
    if len(sys.argv) < 3:
        print(
            "Usage: python3 scripts/crystallize_note.py "
            "<title> <summary> [llm-wiki-root] [source-id ...]"
        )
        return 2

    title = sys.argv[1]
    summary = sys.argv[2]
    root_arg = None
    sources: list[str] = []
    if len(sys.argv) >= 4:
        candidate = sys.argv[3]
        if looks_like_wiki_root(candidate):
            root_arg = candidate
            sources = sys.argv[4:]
        else:
            sources = sys.argv[3:]
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print(
            "Usage: python3 scripts/crystallize_note.py "
            "<title> <summary> [llm-wiki-root] [source-id ...]"
        )
        return 2
    note = LlmWikiRuntime(root).crystallize(title=title, summary=summary, sources=sources)
    print(f"created crystal {note.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
