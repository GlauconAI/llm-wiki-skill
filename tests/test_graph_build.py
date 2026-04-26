from llm_wiki_maintainer.graph.build import build_graph
from llm_wiki_maintainer.graph.insights import find_isolated_pages


def test_build_graph_extracts_page_and_source_edges(wiki_root):
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

    graph = build_graph(wiki_root)

    assert "wiki/overview" in graph.nodes
    assert "wiki/related" in graph.nodes
    assert "SRC-1" in graph.nodes

    page_source_edges = [
        edge
        for edge in graph.edges
        if edge["kind"] == "source"
        and edge["source"] == "wiki/overview"
        and edge["target"] == "SRC-1"
    ]
    assert page_source_edges

    shared_source_edges = [
        edge
        for edge in graph.edges
        if edge["kind"] == "shared_source"
        and {edge["source"], edge["target"]} == {"wiki/overview", "wiki/related"}
    ]
    assert shared_source_edges


def test_find_isolated_pages_returns_list(wiki_root):
    isolated = wiki_root / "wiki" / "isolated.md"
    isolated.write_text(
        """---
type: concept
title: Isolated Page
sources: []
---

# Isolated Page
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    result = find_isolated_pages(graph)

    assert isinstance(result, list)
    assert "wiki/isolated" in result
