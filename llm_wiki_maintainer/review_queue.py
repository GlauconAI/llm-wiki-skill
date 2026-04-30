from __future__ import annotations

from pathlib import Path

import yaml

from llm_wiki_maintainer.review import ReviewItem


REVIEW_QUEUE_PATH = ".llm-wiki/state/review-queue.yaml"


class ReviewQueueStore:
    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.path = self.root / REVIEW_QUEUE_PATH

    def load(self) -> list[ReviewItem]:
        if not self.path.exists():
            return []
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError("review queue must decode to a mapping")
        items = data.get("items", [])
        if not isinstance(items, list):
            raise ValueError("review queue items must be a list")
        return [ReviewItem(**dict(item)) for item in items]

    def save(self, items: list[ReviewItem]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "action": item.action,
                    "status": item.status,
                }
                for item in items
            ]
        }
        self.path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return self.path

    def import_generation_artifact(self, path: Path | str) -> list[ReviewItem]:
        artifact_path = Path(path)
        data = yaml.safe_load(artifact_path.read_text(encoding="utf-8")) or {}
        items = data.get("review_items", [])
        existing = {item.id: item for item in self.load()}
        imported: list[ReviewItem] = []
        for item_data in items:
            item = ReviewItem(**dict(item_data))
            existing[item.id] = item
            imported.append(item)
        self.save(list(existing.values()))
        return imported

    def get(self, review_id: str) -> ReviewItem:
        for item in self.load():
            if item.id == review_id:
                return item
        raise KeyError(review_id)

    def approve(self, review_id: str) -> ReviewItem:
        return self._update_status(review_id, "approved")

    def reject(self, review_id: str) -> ReviewItem:
        return self._update_status(review_id, "rejected")

    def _update_status(self, review_id: str, status: str) -> ReviewItem:
        items = self.load()
        updated: list[ReviewItem] = []
        result: ReviewItem | None = None
        for item in items:
            if item.id == review_id:
                result = ReviewItem(id=item.id, title=item.title, action=item.action, status=status)
                updated.append(result)
            else:
                updated.append(item)
        if result is None:
            raise KeyError(review_id)
        self.save(updated)
        return result
