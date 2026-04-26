from __future__ import annotations

from dataclasses import dataclass


def _freeze_str_list(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise TypeError(f"{field_name} must be a list of strings")
    return tuple(value)


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
