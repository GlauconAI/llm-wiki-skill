from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable


def _freeze_str_list(value: object, field_name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{field_name} must be an iterable of strings")
    if not isinstance(value, Iterable):
        raise TypeError(f"{field_name} must be an iterable of strings")
    items = tuple(value)
    if not all(isinstance(item, str) for item in items):
        raise TypeError(f"{field_name} must be an iterable of strings")
    return items


@dataclass(frozen=True)
class ResearchTask:
    topic: str
    queries: tuple[str, ...]
    status: str = "pending"

    def __post_init__(self) -> None:
        if not isinstance(self.topic, str):
            raise TypeError("topic must be a string")
        object.__setattr__(self, "queries", _freeze_str_list(self.queries, "queries"))
        if not isinstance(self.status, str):
            raise TypeError("status must be a string")
