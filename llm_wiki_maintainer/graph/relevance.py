from __future__ import annotations

from dataclasses import dataclass, field

from llm_wiki_maintainer.graph.build import WikiGraph


@dataclass(frozen=True)
class RelatedPage:
    page_id: str
    score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)


def related_pages(graph: WikiGraph, page_id: str, limit: int = 5) -> list[RelatedPage]:
    node = graph.nodes.get(page_id)
    if not node or node.get("kind") != "page":
        return []

    scores: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}

    for edge in graph.edges:
        kind = edge.get("kind")
        source = edge.get("source")
        target = edge.get("target")

        if kind == "wikilink" and source == page_id and _is_page(graph, str(target)):
            _add(scores, reasons, str(target), 5.0, "direct_wikilink")
        elif kind == "wikilink" and target == page_id and _is_page(graph, str(source)):
            _add(scores, reasons, str(source), 4.0, "backlink")
        elif kind == "shared_source":
            if source == page_id and _is_page(graph, str(target)):
                _add(scores, reasons, str(target), 3.0, "shared_source")
            elif target == page_id and _is_page(graph, str(source)):
                _add(scores, reasons, str(source), 3.0, "shared_source")

    ranked = [
        RelatedPage(page_id=other, score=score, reasons=tuple(reasons.get(other, [])))
        for other, score in scores.items()
        if other != page_id
    ]
    ranked.sort(key=lambda item: (-item.score, item.page_id))
    return ranked[: max(0, int(limit))]


def _is_page(graph: WikiGraph, node_id: str) -> bool:
    return graph.nodes.get(node_id, {}).get("kind") == "page"


def _add(
    scores: dict[str, float],
    reasons: dict[str, list[str]],
    page_id: str,
    amount: float,
    reason: str,
) -> None:
    scores[page_id] = scores.get(page_id, 0.0) + amount
    reasons.setdefault(page_id, []).append(reason)
