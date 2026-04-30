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

from llm_wiki_maintainer.review_queue import ReviewQueueStore
from llm_wiki_maintainer.registry import resolve_wiki_root


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: python3 scripts/review_queue.py "
            "<list|import|approve|reject|show> <arg|llm-wiki-root> [llm-wiki-root]"
        )
        return 2

    command = sys.argv[1]
    if command == "list":
        root_arg = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            root = resolve_wiki_root(root=root_arg)
        except ValueError:
            print(
                "Usage: python3 scripts/review_queue.py "
                "<list|import|approve|reject|show> <arg|llm-wiki-root> [llm-wiki-root]"
            )
            return 2
        for item in ReviewQueueStore(root).load():
            print(f"{item.id} {item.status} {item.action} {item.title}")
        return 0
    if command == "import":
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/review_queue.py import <generation-artifact> [llm-wiki-root]")
            return 2
        artifact = Path(sys.argv[2]).expanduser().resolve()
        root_arg = sys.argv[3] if len(sys.argv) > 3 else None
        try:
            root = resolve_wiki_root(root=root_arg)
        except ValueError:
            print("Usage: python3 scripts/review_queue.py import <generation-artifact> [llm-wiki-root]")
            return 2
        imported = ReviewQueueStore(root).import_generation_artifact(artifact)
        print(f"imported {len(imported)} review item(s)")
        return 0

    if len(sys.argv) < 3:
        print("Usage: python3 scripts/review_queue.py <approve|reject|show> <review-id> [llm-wiki-root]")
        return 2

    review_id = sys.argv[2]
    root_arg = sys.argv[3] if len(sys.argv) > 3 else None
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/review_queue.py <approve|reject|show> <review-id> [llm-wiki-root]")
        return 2
    store = ReviewQueueStore(root)

    if command == "approve":
        item = store.approve(review_id)
        print(f"approved {item.id}")
        return 0
    if command == "reject":
        item = store.reject(review_id)
        print(f"rejected {item.id}")
        return 0
    if command == "show":
        item = store.get(review_id)
        print(f"{item.id} {item.status} {item.action} {item.title}")
        return 0

    print(f"ERROR: unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
