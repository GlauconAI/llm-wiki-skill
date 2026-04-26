from __future__ import annotations

from llm_wiki_maintainer.graph.build import WikiGraph


def find_isolated_pages(graph: WikiGraph) -> list[str]:
    return sorted(
        node_id
        for node_id, meta in graph.nodes.items()
        if meta.get("kind") == "page" and int(meta.get("degree", 0)) == 0
    )
