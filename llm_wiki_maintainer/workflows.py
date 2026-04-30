from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.frontmatter import dump_frontmatter
from llm_wiki_maintainer.graph.build import build_graph
from llm_wiki_maintainer.graph.insights import (
    cluster_cohesion_scores,
    find_bridge_pages,
    find_dense_page_clusters,
    find_knowledge_gaps,
    find_orphaned_source_cards,
)
from llm_wiki_maintainer.lifecycle import SourceRemovalImpact, analyze_source_removal
from llm_wiki_maintainer.query.runtime import query_runtime
from llm_wiki_maintainer.research_queue import RESEARCH_STATUSES, ResearchQueueStore
from llm_wiki_maintainer.review_queue import ReviewQueueStore
from llm_wiki_maintainer.runtime.jobs import JOB_STATUSES
from llm_wiki_maintainer.runtime.state import RuntimeStateStore
from llm_wiki_maintainer.wiki_io import write_text


@dataclass(frozen=True)
class WorkflowStatus:
    root: Path
    page_count: int
    source_card_count: int
    raw_count: int
    ingest_jobs: dict[str, int]
    review_items: dict[str, int]
    research_tasks: dict[str, int]


@dataclass(frozen=True)
class DigestNote:
    path: Path
    title: str
    query: str


@dataclass(frozen=True)
class QueryNote:
    path: Path
    title: str
    query: str


@dataclass(frozen=True)
class CrystalNote:
    path: Path
    title: str


@dataclass(frozen=True)
class DeleteSourceResult:
    impact: SourceRemovalImpact
    applied: bool
    deleted_paths: list[Path]


def project_status(root: Path | str) -> WorkflowStatus:
    root_path = Path(root).resolve()
    source_cards = sorted((root_path / "wiki" / "sources").glob("*.md"))
    pages = [
        path
        for path in sorted((root_path / "wiki").rglob("*.md"))
        if "sources" not in path.relative_to(root_path / "wiki").parts[:1]
    ]
    raw_files = sorted((root_path / "raw").rglob("*.md"))

    snapshot = RuntimeStateStore(root_path).load()
    review_items = ReviewQueueStore(root_path).load()
    research_tasks = ResearchQueueStore(root_path).load()

    return WorkflowStatus(
        root=root_path,
        page_count=len(pages),
        source_card_count=len(source_cards),
        raw_count=len(raw_files),
        ingest_jobs=_status_counts((job.status for job in snapshot.jobs.values()), JOB_STATUSES),
        review_items=_status_counts((item.status for item in review_items), {"pending", "approved", "rejected"}),
        research_tasks=_status_counts((task.status for task in research_tasks), RESEARCH_STATUSES),
    )


def create_digest(
    root: Path | str,
    query: str,
    title: str | None = None,
    limit: int = 8,
    max_chars: int = 2000,
) -> DigestNote:
    root_path = Path(root).resolve()
    config = RuntimeConfig.from_root(root_path)
    note_title = (title or query).strip() or "Digest"
    slug = _slugify(note_title, fallback_prefix="digest")
    path = _next_available_path(root_path / "wiki" / "digests" / f"{slug}.md")

    result = query_runtime(query, root_path, limit=limit, max_chars=max_chars)
    graph = build_graph(root_path)

    page_lines = [
        f"- [[{_wiki_target(root_path, page.path)}]] ({page.title or page.path.stem}, score={page.score:.1f})"
        for page in result.package.pages
    ] or ["- No matching compiled pages found."]

    bridge_pages = find_bridge_pages(graph)[:5]
    dense_clusters = find_dense_page_clusters(graph)[:3]
    knowledge_gaps = find_knowledge_gaps(graph)[:5]
    orphaned_cards = find_orphaned_source_cards(graph)[:5]
    top_cohesion = cluster_cohesion_scores(graph)[:5]

    body = "\n".join(
        [
            f"# {note_title}",
            "",
            "## Query",
            query,
            "",
            "## Context Package",
            *page_lines,
            "",
            "## Synthesized Context",
            result.package.context or "No bounded context available.",
            "",
            "## Graph Signals",
            _list_section(
                "Bridge Pages",
                [f"[[{page_id}]] (degree={degree})" for page_id, degree in bridge_pages],
            ),
            _list_section("Dense Clusters", [", ".join(f"[[{page_id}]]" for page_id in cluster) for cluster in dense_clusters]),
            _list_section("Knowledge Gaps", knowledge_gaps),
            _list_section("Orphaned Source Cards", [f"[[{page_id}]]" for page_id in orphaned_cards]),
            _list_section(
                "Top Cohesion Clusters",
                [f"{', '.join(f'[[{page_id}]]' for page_id in cluster)}: {score:.2f}" for cluster, score in top_cohesion],
            ),
            "",
        ]
    )

    write_text(
        path,
        dump_frontmatter(
            {
                "type": "digest",
                "title": note_title,
                "query": query,
                "created": config.today,
                "updated": config.today,
            },
            body,
        ),
    )
    return DigestNote(path=path, title=note_title, query=query)


def save_query_note(
    root: Path | str,
    query: str,
    title: str | None = None,
    limit: int = 8,
    max_chars: int = 2000,
) -> QueryNote:
    root_path = Path(root).resolve()
    config = RuntimeConfig.from_root(root_path)
    note_title = (title or query).strip() or "Saved Query"
    slug = _slugify(note_title, fallback_prefix="query")
    path = _next_available_path(root_path / "wiki" / "queries" / f"{slug}.md")

    result = query_runtime(query, root_path, limit=limit, max_chars=max_chars)
    page_lines = [
        f"- [[{_wiki_target(root_path, page.path)}]] ({page.title or page.path.stem}, score={page.score:.1f})"
        for page in result.package.pages
    ] or ["- No matching compiled pages found."]

    body = "\n".join(
        [
            f"# {note_title}",
            "",
            "## Query",
            query,
            "",
            "## Retrieved Pages",
            *page_lines,
            "",
            "## Context Package",
            result.package.context or "No bounded context available.",
            "",
        ]
    )

    write_text(
        path,
        dump_frontmatter(
            {
                "type": "query",
                "title": note_title,
                "query": query,
                "created": config.today,
                "updated": config.today,
            },
            body,
        ),
    )
    return QueryNote(path=path, title=note_title, query=query)


def crystallize_note(
    root: Path | str,
    title: str,
    summary: str,
    bullets: list[str] | None = None,
    sources: list[str] | None = None,
) -> CrystalNote:
    root_path = Path(root).resolve()
    config = RuntimeConfig.from_root(root_path)
    note_title = title.strip() or "Crystal"
    path = _next_available_path(
        root_path / "wiki" / "crystallized" / f"{_slugify(note_title, fallback_prefix='crystal')}.md"
    )
    bullet_lines = [f"- {bullet.strip()}" for bullet in (bullets or []) if bullet.strip()]
    sources_list = [source.strip() for source in (sources or []) if source.strip()]

    body_lines = [
        f"# {note_title}",
        "",
        "## Summary",
        summary.strip(),
        "",
    ]
    if bullet_lines:
        body_lines.extend(["## Durable Points", *bullet_lines, ""])
    if sources_list:
        body_lines.extend(["## Source IDs", *[f"- {source}" for source in sources_list], ""])

    write_text(
        path,
        dump_frontmatter(
            {
                "type": "crystal",
                "title": note_title,
                "sources": sources_list,
                "created": config.today,
                "updated": config.today,
            },
            "\n".join(body_lines),
        ),
    )
    return CrystalNote(path=path, title=note_title)


def delete_source(root: Path | str, raw_path: Path | str, apply: bool = False) -> DeleteSourceResult:
    root_path = Path(root).resolve()
    impact = analyze_source_removal(root_path, raw_path)
    deleted_paths: list[Path] = []
    raw_file = _resolve_under_root(root_path, raw_path)

    if apply:
        for path in [raw_file, *impact.source_cards_to_delete]:
            if path.exists():
                path.unlink()
                deleted_paths.append(path.resolve())

    return DeleteSourceResult(impact=impact, applied=apply, deleted_paths=deleted_paths)


def _resolve_under_root(root: Path, path: Path | str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = root / resolved
    return resolved.resolve()


def _status_counts(statuses: object, allowed: set[str]) -> dict[str, int]:
    counts = Counter(statuses)
    return {status: int(counts.get(status, 0)) for status in sorted(allowed)}


def _slugify(value: str, fallback_prefix: str = "note") -> str:
    normalized = value.strip().lower().replace("_", "-")
    slug = re.sub(r"[^\w-]+", "-", normalized, flags=re.UNICODE)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or fallback_prefix


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = path.with_name(f"{stem}-{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _wiki_target(root: Path, path: Path) -> str:
    return path.relative_to(root).with_suffix("").as_posix()


def _list_section(title: str, items: list[str]) -> str:
    if not items:
        return f"### {title}\n- None"
    return "\n".join([f"### {title}", *[f"- {item}" for item in items]])
