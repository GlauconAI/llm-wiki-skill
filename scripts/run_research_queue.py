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

from llm_wiki_maintainer.research_runtime import SearchHit
from llm_wiki_maintainer.registry import resolve_wiki_root
from llm_wiki_maintainer.runtime.api import LlmWikiRuntime


class ScriptSearchProvider:
    def search(self, query: str) -> list[SearchHit]:
        return [
            SearchHit(
                title=f"Result for {query}",
                url=f"https://example.com/{query.replace(' ', '-')}",
                snippet=f"Snippet for {query}",
            )
        ]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/run_research_queue.py <run> [llm-wiki-root]")
        return 2
    command = sys.argv[1]
    if command != "run":
        print(f"ERROR: unknown command: {command}")
        return 2
    root_arg = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/run_research_queue.py <run> [llm-wiki-root]")
        return 2

    result = LlmWikiRuntime(root).execute_next_research_with_adapter(ScriptSearchProvider())
    if result.status.status != "ready" or result.task is None:
        print(f"research_task {result.status.status}: {result.status.detail}")
        return 1
    print(f"completed research task: {result.task.topic}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
