import pytest

from llm_wiki_maintainer.query.retrieve import retrieve_context
from llm_wiki_maintainer.query.tokenize import tokenize_query


def test_tokenize_query_supports_english_words():
    assert "strategy" in tokenize_query("strategy memo")


def test_tokenize_query_supports_chinese_bigrams():
    tokens = tokenize_query("知识图谱")
    assert tokens == ["知识", "识图", "图谱"]


def test_retrieve_context_ignores_short_ascii_substrings(wiki_root):
    result = retrieve_context("ex", wiki_root, limit=5)

    assert result.pages == []


def test_retrieve_context_returns_ranked_pages(wiki_root):
    extra = wiki_root / "wiki" / "example-heavy.md"
    extra.write_text(
        """---
type: concept
title: Example Heavy
---

# Example Heavy

example example example example example example
""",
        encoding="utf-8",
    )

    result = retrieve_context("example", wiki_root, limit=5)

    assert result.pages
    assert result.pages[0].path.name == "example-heavy.md"
    assert result.pages[0].score >= result.pages[-1].score


def test_retrieve_context_uses_body_for_metadata_only_matches(wiki_root):
    extra = wiki_root / "wiki" / "metadata-only.md"
    extra.write_text(
        """---
type: concept
title: Metadata Driven Page
sources: [metadata-source]
---

Readable body text only.
""",
        encoding="utf-8",
    )

    result = retrieve_context("metadata", wiki_root, limit=5)

    assert result.pages
    assert result.pages[0].path.name == "metadata-only.md"
    assert result.pages[0].excerpt == "Readable body text only."
    assert "---" not in result.pages[0].excerpt
    assert "title:" not in result.pages[0].excerpt.lower()


@pytest.mark.parametrize("limit", [0, -1])
def test_retrieve_context_clamps_non_positive_limits(wiki_root, limit):
    result = retrieve_context("example", wiki_root, limit=limit)

    assert result.pages == []
