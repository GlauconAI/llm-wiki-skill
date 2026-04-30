#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VENDOR_ROOT = REPO_ROOT / ".vendor"
if VENDOR_ROOT.exists() and str(VENDOR_ROOT) not in sys.path:
    sys.path.insert(0, str(VENDOR_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from llm_wiki_maintainer.references import MalformedFrontmatterError, sync_used_by
from llm_wiki_maintainer.registry import resolve_wiki_root


def main() -> int:
    try:
        root = resolve_wiki_root(root=sys.argv[1] if len(sys.argv) > 1 else None)
    except ValueError:
        print('ERROR: current directory does not look like an llm-wiki root; pass an explicit root argument.')
        return 2

    try:
        updated_cards = sync_used_by(root)
    except MalformedFrontmatterError as exc:
        print(f"ERROR: invalid source metadata or malformed frontmatter: {exc}")
        return 1
    for card in updated_cards:
        print(f'updated {card}')

    print(f'Updated {len(updated_cards)} source card(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
