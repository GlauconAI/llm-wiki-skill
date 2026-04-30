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

from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.registry import resolve_wiki_root
from llm_wiki_maintainer.source_cards import create_source_card

def _root_from_raw_path(raw_file: Path) -> Path | None:
    resolved = raw_file.expanduser().resolve()
    for candidate in (resolved.parent, *resolved.parents):
        try:
            return resolve_wiki_root(root=candidate)
        except ValueError:
            continue
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/create_source_card.py <raw-file> [llm-wiki-root]")
        return 2

    raw_file = Path(sys.argv[1]).expanduser()
    if not raw_file.is_absolute():
        raw_file = (Path.cwd() / raw_file).resolve()
    else:
        raw_file = raw_file.resolve()

    if not raw_file.is_file():
        print(f"ERROR: raw file not found: {raw_file}")
        return 2

    if len(sys.argv) > 2:
        root_arg = Path(sys.argv[2]).expanduser().resolve()
        if not root_arg.exists():
            print(f"ERROR: root not found: {root_arg}")
            return 2
    else:
        try:
            root_arg = resolve_wiki_root()
        except ValueError:
            root_arg = _root_from_raw_path(raw_file)
            if root_arg is None:
                print(
                    "ERROR: current directory does not look like an llm-wiki root and the raw file did not reveal one; "
                    "pass an explicit root argument."
                )
                return 2

    cfg = RuntimeConfig.from_root(root_arg)

    try:
        relative = raw_file.relative_to(cfg.root)
    except ValueError:
        print(f"ERROR: raw file must live under llm-wiki root: {cfg.root}")
        return 2

    if not str(relative).startswith("raw/"):
        print("ERROR: raw file must be inside the raw/ tree")
        return 2

    result = create_source_card(raw_file, cfg.root, today=cfg.today)
    print(f"{result.status}: {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
