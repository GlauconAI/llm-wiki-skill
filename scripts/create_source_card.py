#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.source_cards import create_source_card

ROOT_DEFAULT = Path("/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/create_source_card.py <raw-file> [llm-wiki-root]")
        return 2

    raw_file = Path(sys.argv[1]).expanduser()
    cfg = RuntimeConfig.from_root(sys.argv[2] if len(sys.argv) > 2 else ROOT_DEFAULT)

    if not raw_file.is_file():
        print(f"ERROR: raw file not found: {raw_file}")
        return 2

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
