from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.query.runtime import query_runtime


def test_query_runtime_returns_ranked_pages_and_context(wiki_root):
    page = wiki_root / "wiki" / "runtime-page.md"
    page.write_text(
        """---
type: concept
title: Runtime Page
sources: [SRC-42]
---

Runtime page body mentions orchestrator and runtime behavior.
""",
        encoding="utf-8",
    )

    result = query_runtime("orchestrator", wiki_root, limit=5, max_chars=160)

    assert result.retrieval.query == "orchestrator"
    assert result.package.pages
    assert result.package.pages[0].title == "Runtime Page"
    assert "orchestrator" in result.package.context.lower()


def test_query_context_cli_prints_pages_and_context(wiki_root):
    page = wiki_root / "wiki" / "runtime-page.md"
    page.write_text(
        """---
type: concept
title: Runtime Page
---

Runtime page body mentions orchestrator and runtime behavior.
""",
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "query_context.py"

    result = subprocess.run(
        [sys.executable, str(script), "orchestrator", str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Query: orchestrator" in result.stdout
    assert "Runtime Page" in result.stdout
    assert "Context:" in result.stdout
