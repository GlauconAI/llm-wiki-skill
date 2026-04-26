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


def test_build_graph_preserves_source_card_metadata_when_cited(wiki_root):
    graph = build_graph(wiki_root)

    source_node = graph.nodes["SRC-1"]

    assert source_node["kind"] == "source"
    assert source_node["title"] == "Example Source"
    assert source_node["path"] == "wiki/sources/example-source.md"


def test_build_graph_records_wikilink_edges_for_missing_targets(wiki_root):
    page = wiki_root / "wiki" / "missing-link.md"
    page.write_text(
        """---
type: concept
title: Missing Link
---

# Missing Link

See [[wiki/not-loaded]].
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)

    assert any(
        edge["kind"] == "wikilink"
        and edge["source"] == "wiki/missing-link"
        and edge["target"] == "wiki/not-loaded"
        for edge in graph.edges
    )
    assert "wiki/not-loaded" not in graph.nodes


def test_build_graph_does_not_materialize_raw_source_wikilinks_as_nodes(wiki_root):
    graph = build_graph(wiki_root)

    assert any(
        edge["kind"] == "wikilink"
        and edge["source"] == "wiki/overview"
        and edge["target"] == "raw/sources/example-raw"
        for edge in graph.edges
    )
    assert "raw/sources/example-raw" not in graph.nodes


def test_build_graph_skips_malformed_files_without_aborting(wiki_root):
    broken_page = wiki_root / "wiki" / "broken.md"
    broken_page.write_text("---\ntype: [oops\n---\n", encoding="utf-8")
    broken_source = wiki_root / "wiki" / "sources" / "broken-source.md"
    broken_source.write_text("---\ntype: source\nid: [oops\n---\n", encoding="utf-8")

    graph = build_graph(wiki_root)

    assert "wiki/overview" in graph.nodes
    assert "SRC-1" in graph.nodes
    assert "wiki/broken" not in graph.nodes
    assert "broken-source" not in graph.nodes


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
