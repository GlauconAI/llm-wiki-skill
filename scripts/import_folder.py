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
        print("Usage: python3 scripts/import_folder.py <source-folder> [llm-wiki-root]")
        return 2
    source = Path(sys.argv[1]).expanduser().resolve()
    root_arg = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/import_folder.py <source-folder> [llm-wiki-root]")
        return 2
    result = LlmWikiRuntime(root).import_folder_with_adapter(source)
    print(f"{result.adapter.key}: {result.status.status}")
    print(f"imported {len(result.imported_paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
