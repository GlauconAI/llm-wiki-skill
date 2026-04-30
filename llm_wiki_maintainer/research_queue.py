from __future__ import annotations

from pathlib import Path

import yaml

from llm_wiki_maintainer.research import ResearchTask


RESEARCH_QUEUE_PATH = ".llm-wiki/state/research-queue.yaml"
RESEARCH_STATUSES = {"pending", "in_progress", "completed", "rejected"}


class ResearchQueueStore:
    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.path = self.root / RESEARCH_QUEUE_PATH

    def load(self) -> list[ResearchTask]:
        if not self.path.exists():
            return []
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError("research queue must decode to a mapping")
        items = data.get("items", [])
        if not isinstance(items, list):
            raise ValueError("research queue items must be a list")
        return [ResearchTask(**dict(item)) for item in items]

    def save(self, tasks: list[ResearchTask]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "items": [
                {
                    "topic": task.topic,
                    "queries": list(task.queries),
                    "status": task.status,
                }
                for task in tasks
            ]
        }
        self.path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return self.path

    def enqueue(self, task: ResearchTask) -> ResearchTask:
        tasks = self.load()
        tasks.append(task)
        self.save(tasks)
        return task

    def update_status(self, topic: str, status: str) -> ResearchTask:
        if status not in RESEARCH_STATUSES:
            raise ValueError(f"invalid research status: {status}")
        tasks = self.load()
        updated: list[ResearchTask] = []
        result: ResearchTask | None = None
        for task in tasks:
            if task.topic == topic:
                result = ResearchTask(topic=task.topic, queries=task.queries, status=status)
                updated.append(result)
            else:
                updated.append(task)
        if result is None:
            raise KeyError(topic)
        self.save(updated)
        return result
