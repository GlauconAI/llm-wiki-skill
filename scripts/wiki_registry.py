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

from llm_wiki_maintainer.registry import WikiRegistry


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage: python3 scripts/wiki_registry.py "
            "<add|activate|list|show-active> <args...> <registry-path>"
        )
        return 2

    command = sys.argv[1]

    if command == "list":
        registry = WikiRegistry(sys.argv[2])
        for entry in registry.list():
            marker = "*" if entry.active else "-"
            print(f"{marker} {entry.name} {entry.path}")
        return 0

    if command == "show-active":
        registry = WikiRegistry(sys.argv[2])
        active = registry.active()
        print(f"{active.name} {active.path}")
        return 0

    if command == "add":
        if len(sys.argv) < 5:
            print("Usage: python3 scripts/wiki_registry.py add <name> <root> <registry-path>")
            return 2
        registry = WikiRegistry(sys.argv[4])
        entry = registry.register(sys.argv[2], sys.argv[3])
        print(f"registered {entry.name} {entry.path}")
        return 0

    if command == "activate":
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/wiki_registry.py activate <name> <registry-path>")
            return 2
        registry = WikiRegistry(sys.argv[3])
        entry = registry.activate(sys.argv[2])
        print(f"active {entry.name} {entry.path}")
        return 0

    print(f"ERROR: unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
