from llm_wiki_maintainer.query.assemble import assemble_context
from llm_wiki_maintainer.query.retrieve import retrieve_context


def test_assemble_context_returns_bounded_package(wiki_root):
    page = wiki_root / "wiki" / "body-only.md"
    page.write_text(
        """---
type: concept
title: Generic Page
sources: [SRC-42]
---

Readable body text with a unique bodyterm here.
""",
        encoding="utf-8",
    )

    retrieval = retrieve_context("bodyterm", wiki_root, limit=5)
    package = assemble_context(retrieval, max_chars=120)

    assert package.query == "bodyterm"
    assert package.pages
    assert len(package.context) <= 120
    assert "Generic Page" in package.context
    assert "Readable body text with a unique bodyterm here." in package.context


def test_assemble_context_respects_empty_retrieval(wiki_root):
    retrieval = retrieve_context("zzzz-no-match", wiki_root, limit=5)
    package = assemble_context(retrieval, max_chars=120)

    assert package.pages == []
    assert package.context == ""
