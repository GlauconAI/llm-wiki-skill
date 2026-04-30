from __future__ import annotations

from llm_wiki_maintainer.graph.community import page_communities
from llm_wiki_maintainer.graph.build import WikiGraph


def find_isolated_pages(graph: WikiGraph) -> list[str]:
    return sorted(
        node_id
        for node_id, meta in graph.nodes.items()
        if meta.get("kind") == "page" and int(meta.get("degree", 0)) == 0
    )


def find_bridge_pages(graph: WikiGraph) -> list[tuple[str, int]]:
    ranked = [
        (node_id, int(meta.get("degree", 0)))
        for node_id, meta in graph.nodes.items()
        if meta.get("kind") == "page" and int(meta.get("degree", 0)) >= 2
    ]
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return ranked


def find_orphaned_source_cards(graph: WikiGraph) -> list[str]:
    cited_sources = {
        str(edge["target"])
        for edge in graph.edges
        if edge.get("kind") == "source"
    }
    return sorted(
        node_id
        for node_id, meta in graph.nodes.items()
        if meta.get("kind") == "source" and node_id not in cited_sources
    )


def find_dense_page_clusters(graph: WikiGraph) -> list[list[str]]:
    clusters: list[list[str]] = []
    for community in page_communities(graph):
        if len(community) < 2:
            continue
        possible_edges = len(community) * (len(community) - 1) / 2
        actual_pairs: set[tuple[str, str]] = set()
        for edge in graph.edges:
            if edge.get("kind") not in {"wikilink", "shared_source"}:
                continue
            source = str(edge["source"])
            target = str(edge["target"])
            if source in community and target in community and source != target:
                actual_pairs.add(tuple(sorted((source, target))))
        density = len(actual_pairs) / possible_edges if possible_edges else 0.0
        if density >= 0.5:
            clusters.append(community)
    return clusters


def find_suspicious_isolates(graph: WikiGraph) -> list[str]:
    return find_isolated_pages(graph)


def cluster_cohesion_scores(graph: WikiGraph) -> list[tuple[list[str], float]]:
    scores: list[tuple[list[str], float]] = []
    for cluster in page_communities(graph):
        if len(cluster) < 2:
            continue
        possible_edges = len(cluster) * (len(cluster) - 1) / 2
        actual_pairs: set[tuple[str, str]] = set()
        for edge in graph.edges:
            if edge.get("kind") not in {"wikilink", "shared_source"}:
                continue
            source = str(edge["source"])
            target = str(edge["target"])
            if source in cluster and target in cluster and source != target:
                actual_pairs.add(tuple(sorted((source, target))))
        score = len(actual_pairs) / possible_edges if possible_edges else 0.0
        scores.append((cluster, score))
    scores.sort(key=lambda item: (-item[1], item[0]))
    return scores


def find_knowledge_gaps(graph: WikiGraph) -> list[str]:
    sourced_pages = {
        str(edge["source"])
        for edge in graph.edges
        if edge.get("kind") == "source"
    }
    return sorted(
        node_id
        for node_id, meta in graph.nodes.items()
        if meta.get("kind") == "page"
        and node_id not in sourced_pages
    )
