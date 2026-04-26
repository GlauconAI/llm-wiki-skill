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


def test_retrieve_context_uses_title_for_title_only_matches(wiki_root):
    extra = wiki_root / "wiki" / "title-only.md"
    extra.write_text(
        """---
type: concept
title: Unique Title Match
---

Readable body text without the query term.
""",
        encoding="utf-8",
    )

    result = retrieve_context("unique", wiki_root, limit=5)

    assert result.pages
    assert result.pages[0].path.name == "title-only.md"
    assert result.pages[0].excerpt == "Unique Title Match"


def test_retrieve_context_uses_body_for_body_only_matches(wiki_root):
    extra = wiki_root / "wiki" / "body-only.md"
    extra.write_text(
        """---
type: concept
title: Generic Page
---

Readable body text with a unique bodyterm here.
""",
        encoding="utf-8",
    )

    result = retrieve_context("bodyterm", wiki_root, limit=5)

    assert result.pages
    assert result.pages[0].path.name == "body-only.md"
    assert result.pages[0].excerpt == "Readable body text with a unique bodyterm here."
    assert "Generic Page" not in result.pages[0].excerpt


@pytest.mark.parametrize("limit", [0, -1])
def test_retrieve_context_clamps_non_positive_limits(wiki_root, limit):
    result = retrieve_context("example", wiki_root, limit=limit)

    assert result.pages == []
