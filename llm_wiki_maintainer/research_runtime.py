from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Protocol

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_queue import ResearchQueueStore
from llm_wiki_maintainer.review_queue import ReviewQueueStore
from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str


class SearchProvider(Protocol):
    def search(self, query: str) -> list[SearchHit]:
        ...


def queue_research_from_review(
    root: Path | str,
    review_id: str,
    topic: str,
    queries: list[str],
    override: bool = False,
) -> ResearchTask:
    review_item = ReviewQueueStore(root).get(review_id)
    if review_item.status != "approved" and not override:
        raise PermissionError("review item must be approved before queueing research")
    if review_item.action != "deep_research" and not override:
        raise PermissionError("review item action must be deep_research before queueing research")

    task = ResearchTask(topic=topic, queries=queries)
    ResearchQueueStore(root).enqueue(task)
    return task


def execute_next_research(root: Path | str, provider: SearchProvider) -> tuple[ResearchTask, Path]:
    root_path = Path(root).resolve()
    store = ResearchQueueStore(root_path)
    pending = next((task for task in store.load() if task.status == "pending"), None)
    if pending is None:
        raise LookupError("no pending research tasks")

    store.update_status(pending.topic, "in_progress")
    hits: list[SearchHit] = []
    for query in pending.queries:
        hits.extend(provider.search(query))

    raw_dir = root_path / "raw" / "research"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{_slugify(pending.topic)}.md"
    raw_path.write_text(_render_research_note(pending, hits), encoding="utf-8")

    completed = store.update_status(pending.topic, "completed")
    IngestQueue(root_path).enqueue(raw_path)
    return completed, raw_path


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "research-task"


def _render_research_note(task: ResearchTask, hits: list[SearchHit]) -> str:
    body = [
        f"# Research: {task.topic}",
        "",
        "## Queries",
        *[f"- {query}" for query in task.queries],
        "",
        "## Findings",
    ]
    if hits:
        for hit in hits:
            body.extend(
                [
                    f"- [{hit.title}]({hit.url})",
                    f"  - {hit.snippet}",
                ]
            )
    else:
        body.append("- No search results returned.")
    body.append("")
    return "\n".join(body)
