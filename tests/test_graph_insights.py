from llm_wiki_maintainer.graph.build import build_graph
from llm_wiki_maintainer.graph.insights import (
    find_bridge_pages,
    find_dense_page_clusters,
    find_orphaned_source_cards,
    find_suspicious_isolates,
)


def test_find_bridge_pages_returns_high_degree_pages(wiki_root):
    page = wiki_root / "wiki" / "bridge.md"
    page.write_text(
        """---
type: concept
title: Bridge
sources: [SRC-1]
---

# Bridge

See [[wiki/overview]] and [[wiki/dup]].
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    bridges = find_bridge_pages(graph)

    assert bridges
    assert any(page_id == "wiki/bridge" for page_id, _score in bridges)


def test_find_orphaned_source_cards_returns_uncited_sources(wiki_root):
    orphan = wiki_root / "wiki" / "sources" / "orphan.md"
    orphan.write_text(
        """---
type: source
id: SRC-99
title: Orphan Source
---

# Source: Orphan Source

## Location
[[raw/sources/example-raw]]

## Type
md

## Coverage
- orphan

## Used by

## Key Sections
- opening

## Notes
- orphan
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    orphaned = find_orphaned_source_cards(graph)

    assert "SRC-99" in orphaned


def test_find_dense_page_clusters_groups_connected_pages(wiki_root):
    a = wiki_root / "wiki" / "cluster-a.md"
    b = wiki_root / "wiki" / "cluster-b.md"
    a.write_text(
        """---
type: concept
title: Cluster A
sources: [SRC-1]
---

See [[wiki/cluster-b]].
""",
        encoding="utf-8",
    )
    b.write_text(
        """---
type: concept
title: Cluster B
sources: [SRC-1]
---

See [[wiki/cluster-a]].
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    clusters = find_dense_page_clusters(graph)

    assert clusters
    assert any({"wiki/cluster-a", "wiki/cluster-b"}.issubset(set(cluster)) for cluster in clusters)


def test_find_suspicious_isolates_flags_pages_without_sources(wiki_root):
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
    suspicious = find_suspicious_isolates(graph)

    assert "wiki/isolated" in suspicious
