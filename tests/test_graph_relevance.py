from llm_wiki_maintainer.graph.build import build_graph
from llm_wiki_maintainer.graph.relevance import related_pages


def test_related_pages_scores_direct_links_above_shared_source(wiki_root):
    related = wiki_root / "wiki" / "related.md"
    related.write_text(
        """---
type: concept
title: Related Page
sources: [SRC-1]
---

# Related Page

See [[wiki/overview]].
""",
        encoding="utf-8",
    )
    shared = wiki_root / "wiki" / "shared.md"
    shared.write_text(
        """---
type: concept
title: Shared Page
sources: [SRC-1]
---

# Shared Page
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    related_results = related_pages(graph, "wiki/related", limit=5)

    assert related_results
    assert related_results[0].page_id == "wiki/overview"
    assert related_results[0].score > related_results[-1].score


def test_related_pages_returns_empty_for_unknown_page(wiki_root):
    graph = build_graph(wiki_root)

    assert related_pages(graph, "wiki/does-not-exist", limit=5) == []
