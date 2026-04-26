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
