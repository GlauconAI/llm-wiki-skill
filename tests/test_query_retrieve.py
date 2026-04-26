from llm_wiki_maintainer.query.retrieve import retrieve_context
from llm_wiki_maintainer.query.tokenize import tokenize_query


def test_tokenize_query_supports_english_words():
    assert "strategy" in tokenize_query("strategy memo")


def test_tokenize_query_supports_chinese_bigrams():
    tokens = tokenize_query("知识图谱")
    assert any(len(token) >= 2 for token in tokens)


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
