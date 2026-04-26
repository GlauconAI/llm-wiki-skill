from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


_REVIEW_ITEM_FIELDS = ("id", "title", "action", "status")


def _freeze_str_dict(value: object, field_name: str) -> Mapping[str, str]:
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} must be a mapping of strings to strings")
    if not all(isinstance(key, str) and isinstance(item, str) for key, item in value.items()):
        raise TypeError(f"{field_name} must be a mapping of strings to strings")
    return MappingProxyType(dict(value))


def _freeze_review_item(value: object, index: int) -> Mapping[str, str]:
    field_name = f"review_items[{index}]"
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} must be a mapping of strings to strings")

    copied = dict(value)
    if set(copied) != set(_REVIEW_ITEM_FIELDS):
        raise TypeError(
            f"{field_name} must include {', '.join(_REVIEW_ITEM_FIELDS)}"
        )
    if not all(isinstance(copied[name], str) for name in _REVIEW_ITEM_FIELDS):
        raise TypeError(
            f"{field_name} must include string id, title, action, and status fields"
        )
    return MappingProxyType(copied)


def _freeze_review_items(value: object, field_name: str) -> tuple[Mapping[str, str], ...]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list of mappings")
    return tuple(_freeze_review_item(item, index) for index, item in enumerate(value))


@dataclass(frozen=True)
class GenerationArtifact:
    outputs: Mapping[str, str]
    review_items: tuple[Mapping[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "outputs", _freeze_str_dict(self.outputs, "outputs"))
        object.__setattr__(self, "review_items", _freeze_review_items(self.review_items, "review_items"))

    def to_dict(self) -> dict[str, object]:
        return {
            "outputs": dict(self.outputs),
            "review_items": [dict(item) for item in self.review_items],
        }
