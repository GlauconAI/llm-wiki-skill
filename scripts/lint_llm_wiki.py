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

from llm_wiki_maintainer.linting import lint_root
from llm_wiki_maintainer.registry import resolve_wiki_root

def main() -> int:
    try:
        root = resolve_wiki_root(root=sys.argv[1] if len(sys.argv) > 1 else None)
    except ValueError:
        print('ERROR: current directory does not look like an llm-wiki root; pass an explicit root argument.')
        return 2

    problems = lint_root(root)

    if problems:
        print(f'LLM Wiki lint: FAIL ({len(problems)} issue(s))')
        for problem in problems:
            print(f'- {problem.path}: {problem.message}')
        return 1

    print('LLM Wiki lint: PASS')
    print(f'Checked root: {root}')
    print('Validated source-card hygiene, compiled-page density, claim-level and page-level raw pointers, wikilink targets, Used by consistency, and index coverage.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
