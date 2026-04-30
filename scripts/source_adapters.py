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

from llm_wiki_maintainer.runtime.api import LlmWikiRuntime
from llm_wiki_maintainer.registry import resolve_wiki_root


def main() -> int:
    root_arg = sys.argv[1] if len(sys.argv) >= 2 and sys.argv[1] != "--with-research-provider" else None
    extra_args = sys.argv[2:] if root_arg is not None else sys.argv[1:]
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print("Usage: python3 scripts/source_adapters.py [llm-wiki-root] [--with-research-provider]")
        return 2
    with_research_provider = "--with-research-provider" in extra_args
    runtime = LlmWikiRuntime(root)

    for spec in runtime.source_registry().list():
        print(
            f"{spec.key} mode={spec.input_mode} raw={spec.raw_subdir} "
            f"adapter={spec.adapter_name}"
        )
    for status in runtime.adapter_statuses(
        research_provider_available=with_research_provider
    ):
        print(f"status {status.key} {status.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
