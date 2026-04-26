#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm_wiki_maintainer.ingest.planner import suggest_target_pages


def _looks_like_llm_wiki_root(root: Path) -> bool:
    return (root / "raw").is_dir() and (root / "wiki").is_dir()


def _root_from_raw_path(raw_file: Path) -> Path | None:
    resolved = raw_file.expanduser().resolve()
    for candidate in (resolved.parent, *resolved.parents):
        if _looks_like_llm_wiki_root(candidate):
            return candidate
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/suggest_target_pages.py <raw-file> [llm-wiki-root]")
        return 2
    raw_file = Path(sys.argv[1]).expanduser()
    if not raw_file.exists():
        print(f"ERROR: raw file not found: {raw_file}")
        return 2
    if len(sys.argv) > 2:
        root = Path(sys.argv[2]).expanduser().resolve()
        if not root.exists():
            print(f"ERROR: root not found: {root}")
            return 2
    else:
        cwd = Path.cwd().resolve()
        if _looks_like_llm_wiki_root(cwd):
            root = cwd
        else:
            root = _root_from_raw_path(raw_file)
            if root is None:
                print(
                    "ERROR: current directory does not look like an llm-wiki root and the raw path did not reveal one; "
                    "pass an explicit root argument."
                )
                return 2

    candidates = suggest_target_pages(raw_file, root)
    print("Suggested affected pages:")
    if not candidates:
        print("- No strong candidates found. Consider creating a new topic or concept page.")
        return 0

    for candidate in candidates[:12]:
        print(f"- [[{candidate.path}|{candidate.title}]] (score: {candidate.score})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
