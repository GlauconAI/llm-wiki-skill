#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm_wiki_maintainer.ingest.planner import suggest_target_pages

ROOT_DEFAULT = Path("/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/suggest_target_pages.py <raw-file> [llm-wiki-root]")
        return 2
    raw_file = Path(sys.argv[1]).expanduser()
    root = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else ROOT_DEFAULT
    if not raw_file.exists():
        print(f"ERROR: raw file not found: {raw_file}")
        return 2

    candidates = [
        candidate
        for candidate in suggest_target_pages(raw_file, root)
        if candidate.score >= 6
    ]
    print("Suggested affected pages:")
    if not candidates:
        print("- No strong candidates found. Consider creating a new topic or concept page.")
        return 0

    for candidate in candidates[:12]:
        print(f"- [[{candidate.path}|{candidate.title}]] (score: {candidate.score})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
