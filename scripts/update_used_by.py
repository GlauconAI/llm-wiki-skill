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

ROOT_DEFAULT = Path('/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki')


def main() -> int:
    root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else ROOT_DEFAULT
    if not root.exists():
        print(f'ERROR: root not found: {root}')
        return 2

    try:
        updated_cards = sync_used_by(root)
    except MalformedFrontmatterError as exc:
        print(f"ERROR: malformed frontmatter in compiled pages: {exc}")
        return 1
    for card in updated_cards:
        print(f'updated {card}')

    print(f'Updated {len(updated_cards)} source card(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
