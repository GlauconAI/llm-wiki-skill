from __future__ import annotations

from dataclasses import dataclass, field


def _ensure_str_dict(value: object, field_name: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} must be a mapping of strings to strings")
    if not all(isinstance(key, str) and isinstance(item, str) for key, item in value.items()):
        raise TypeError(f"{field_name} must be a mapping of strings to strings")
    return value


def _ensure_dict_list(value: object, field_name: str) -> list[dict]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list of mappings")
    if not all(isinstance(item, dict) for item in value):
        raise TypeError(f"{field_name} must be a list of mappings")
    return value


@dataclass(frozen=True)
class GenerationArtifact:
    outputs: dict[str, str]
    review_items: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        _ensure_str_dict(self.outputs, "outputs")
        _ensure_dict_list(self.review_items, "review_items")

    def to_dict(self) -> dict[str, object]:
        return {
            "outputs": dict(self.outputs),
            "review_items": [dict(item) for item in self.review_items],
        }
