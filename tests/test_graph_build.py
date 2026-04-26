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


def test_build_graph_normalizes_scalar_source_ids(wiki_root):
    graph = build_graph(wiki_root)

    assert "src-1" not in graph.nodes
    assert "SRC-1" in graph.nodes
    assert any(
        edge["kind"] == "source"
        and edge["source"] == "wiki/scalar"
        and edge["target"] == "SRC-1"
        for edge in graph.edges
    )


def test_build_graph_deduplicates_repeated_wikilinks(wiki_root):
    graph = build_graph(wiki_root)

    repeated_edges = [
        edge
        for edge in graph.edges
        if edge["kind"] == "wikilink"
        and edge["source"] == "wiki/dup"
        and edge["target"] == "wiki/overview"
    ]

    assert len(repeated_edges) == 1
    assert graph.nodes["wiki/dup"]["degree"] == 1


def test_build_graph_deduplicates_repeated_links_and_sources(wiki_root):
    repeated = wiki_root / "wiki" / "repeated.md"
    repeated.write_text(
        """---
type: concept
title: Repeated
sources: [SRC-1, src-1, SRC-1]
---

# Repeated

See [[wiki/overview]] and [[wiki/overview]].
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)

    source_edges = [
        edge
        for edge in graph.edges
        if edge["kind"] == "source"
        and edge["source"] == "wiki/repeated"
        and edge["target"] == "SRC-1"
    ]
    wikilink_edges = [
        edge
        for edge in graph.edges
        if edge["kind"] == "wikilink"
        and edge["source"] == "wiki/repeated"
        and edge["target"] == "wiki/overview"
    ]

    assert len(source_edges) == 1
    assert len(wikilink_edges) == 1
    assert graph.nodes["wiki/repeated"]["degree"] == 4


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


def test_build_graph_skips_parseable_source_cards_missing_ids(wiki_root):
    missing_id_source = wiki_root / "wiki" / "sources" / "missing-id.md"
    missing_id_source.write_text(
        """---
type: source
title: Missing Id Source
---

# Missing Id Source

## Used by
- [[wiki/overview]]
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)

    assert "missing-id" not in graph.nodes
    assert "Missing Id Source" not in {
        node.get("title") for node in graph.nodes.values() if node.get("kind") == "source"
    }


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


def test_find_isolated_pages_ignores_degree_one_pages(wiki_root):
    linked = wiki_root / "wiki" / "linked-once.md"
    linked.write_text(
        """---
type: concept
title: Linked Once
---

# Linked Once

See [[wiki/not-loaded]].
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    result = find_isolated_pages(graph)

    assert graph.nodes["wiki/linked-once"]["degree"] == 1
    assert "wiki/linked-once" not in result
