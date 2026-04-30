from llm_wiki_maintainer.graph.build import build_graph
from llm_wiki_maintainer.graph.insights import cluster_cohesion_scores, find_knowledge_gaps


def test_cluster_cohesion_scores_reports_dense_components(wiki_root):
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
    scores = cluster_cohesion_scores(graph)

    assert scores
    assert any({"wiki/cluster-a", "wiki/cluster-b"}.issubset(set(cluster)) for cluster, _ in scores)


def test_find_knowledge_gaps_flags_source_light_pages(wiki_root):
    thin = wiki_root / "wiki" / "thin-gap.md"
    thin.write_text(
        """---
type: concept
title: Thin Gap
sources: []
---

# Thin Gap

See [[wiki/overview]].
""",
        encoding="utf-8",
    )

    graph = build_graph(wiki_root)
    gaps = find_knowledge_gaps(graph)

    assert "wiki/thin-gap" in gaps
