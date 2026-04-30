from __future__ import annotations

from llm_wiki_maintainer.graph.build import WikiGraph


def page_communities(graph: WikiGraph) -> list[list[str]]:
    adjacency: dict[str, set[str]] = {
        node_id: set()
        for node_id, meta in graph.nodes.items()
        if meta.get("kind") == "page"
    }
    for edge in graph.edges:
        if edge.get("kind") not in {"wikilink", "shared_source"}:
            continue
        source = str(edge["source"])
        target = str(edge["target"])
        if source in adjacency and target in adjacency:
            adjacency[source].add(target)
            adjacency[target].add(source)

    seen: set[str] = set()
    communities: list[list[str]] = []
    for page_id in sorted(adjacency):
        if page_id in seen:
            continue
        stack = [page_id]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component.append(current)
            stack.extend(sorted(adjacency[current] - seen, reverse=True))
        communities.append(sorted(component))
    return communities
