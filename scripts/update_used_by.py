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


def _looks_like_llm_wiki_root(root: Path) -> bool:
    return (root / 'raw').is_dir() and (root / 'wiki').is_dir()


def _resolve_root_from_cwd() -> Path | None:
    cwd = Path.cwd().resolve()
    return cwd if _looks_like_llm_wiki_root(cwd) else None


def main() -> int:
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).expanduser().resolve()
        if not root.exists():
            print(f'ERROR: root not found: {root}')
            return 2
    else:
        root = _resolve_root_from_cwd()
        if root is None:
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
