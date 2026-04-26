from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

import yaml

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.links import rel, wikilink_targets
from llm_wiki_maintainer.references import parse_source_id, parse_sources_field


@dataclass
class WikiGraph:
    nodes: dict[str, dict[str, object]] = field(default_factory=dict)
    edges: list[dict[str, object]] = field(default_factory=list)


def build_graph(root: Path) -> WikiGraph:
    graph = WikiGraph()
    page_records: list[tuple[str, str, object]] = []
    source_records: list[tuple[str, str, object]] = []
    pages_by_source: dict[str, set[str]] = {}
    wiki_dir = root / "wiki"

    for path in sorted(wiki_dir.rglob("*.md")):
        relative = rel(path, root)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            document = load_frontmatter(text)
        except (OSError, ValueError, yaml.YAMLError):
            continue

        if relative.startswith("wiki/sources/"):
            source_id = parse_source_id(text) or path.with_suffix("").name
            add_node(
                graph,
                source_id,
                kind="source",
                path=relative,
                title=document.data.get("title") or path.stem,
            )
            source_records.append((source_id, text, document))
            continue

        page_id = relative[:-3]
        add_node(
            graph,
            page_id,
            kind="page",
            path=relative,
            title=document.data.get("title") or path.stem,
        )
        page_records.append((page_id, text, document))

    for page_id, text, document in page_records:
        for target in wikilink_targets(document.body):
            add_edge(graph, page_id, target, kind="wikilink")

        for source_id in parse_sources_field(text):
            pages_by_source.setdefault(source_id, set()).add(page_id)
            add_node(graph, source_id, kind="source", title=source_id)
            add_edge(graph, page_id, source_id, kind="source")

    for source_id, _text, document in source_records:
        for target in wikilink_targets(document.body):
            add_edge(graph, source_id, target, kind="wikilink")

    for source_id, page_ids in pages_by_source.items():
        if source_id not in graph.nodes:
            add_node(graph, source_id, kind="source", title=source_id)
        for left, right in combinations(sorted(page_ids), 2):
            add_edge(graph, left, right, kind="shared_source", source_id=source_id)

    return graph


def add_node(graph: WikiGraph, node_id: str, **attrs: object) -> None:
    node = graph.nodes.setdefault(node_id, {"degree": 0})
    for key, value in attrs.items():
        if key == "title" and node.get("title"):
            continue
        node.setdefault(key, value)


def add_edge(graph: WikiGraph, source: str, target: str, **attrs: object) -> None:
    edge = {"source": source, "target": target, **attrs}
    graph.edges.append(edge)
    increment_degree(graph, source)
    if target != source:
        increment_degree(graph, target)


def increment_degree(graph: WikiGraph, node_id: str) -> None:
    node = graph.nodes.setdefault(node_id, {"degree": 0})
    node["degree"] = int(node.get("degree", 0)) + 1
