from __future__ import annotations

from dataclasses import dataclass, field, replace
from uuid import uuid4


JOB_STATUSES = {"pending", "running", "completed", "failed", "cancelled", "skipped"}


@dataclass(frozen=True)
class IngestJob:
    id: str
    raw_path: str
    status: str = "pending"
    attempts: int = 0
    analysis_artifact: str = ""
    generation_artifact: str = ""
    review_items: tuple[str, ...] = field(default_factory=tuple)
    research_tasks: tuple[str, ...] = field(default_factory=tuple)
    last_error: str = ""

    def __post_init__(self) -> None:
        if self.status not in JOB_STATUSES:
            raise ValueError(f"invalid job status: {self.status}")

    @classmethod
    def new(cls, raw_path: str) -> "IngestJob":
        return cls(id=f"ingest-{uuid4().hex[:12]}", raw_path=raw_path)

    def with_status(self, status: str, **changes: object) -> "IngestJob":
        if status not in JOB_STATUSES:
            raise ValueError(f"invalid job status: {status}")
        return replace(self, status=status, **changes)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "raw_path": self.raw_path,
            "status": self.status,
            "attempts": self.attempts,
            "analysis_artifact": self.analysis_artifact,
            "generation_artifact": self.generation_artifact,
            "review_items": list(self.review_items),
            "research_tasks": list(self.research_tasks),
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "IngestJob":
        return cls(
            id=str(data["id"]),
            raw_path=str(data["raw_path"]),
            status=str(data.get("status", "pending")),
            attempts=int(data.get("attempts", 0)),
            analysis_artifact=str(data.get("analysis_artifact", "")),
            generation_artifact=str(data.get("generation_artifact", "")),
            review_items=tuple(str(item) for item in data.get("review_items", [])),
            research_tasks=tuple(str(item) for item in data.get("research_tasks", [])),
            last_error=str(data.get("last_error", "")),
        )
