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

from llm_wiki_maintainer.query.runtime import query_runtime
from llm_wiki_maintainer.registry import resolve_wiki_root


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/query_context.py <query> [llm-wiki-root]")
        return 2
    query = sys.argv[1]
    root_arg = sys.argv[2] if len(sys.argv) >= 3 else None
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/query_context.py <query> [llm-wiki-root]")
        return 2
    result = query_runtime(query, root)

    print(f"Query: {result.retrieval.query}")
    print("Pages:")
    for page in result.package.pages:
        print(f"- {page.title} [{page.path.as_posix()[:-3]}] score={page.score}")
    print("Context:")
    print(result.package.context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
