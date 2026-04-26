from __future__ import annotations

from dataclasses import dataclass, field


def _freeze_str_list(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise TypeError(f"{field_name} must be a list of strings")
    return tuple(value)


@dataclass(frozen=True)
class AnalysisArtifact:
    raw_path: str
    key_claims: tuple[str, ...]
    target_pages: tuple[str, ...]
    tensions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.raw_path, str):
            raise TypeError("raw_path must be a string")
        object.__setattr__(self, "key_claims", _freeze_str_list(self.key_claims, "key_claims"))
        object.__setattr__(self, "target_pages", _freeze_str_list(self.target_pages, "target_pages"))
        object.__setattr__(self, "tensions", _freeze_str_list(self.tensions, "tensions"))

    def to_dict(self) -> dict[str, object]:
        return {
            "raw_path": self.raw_path,
            "key_claims": list(self.key_claims),
            "target_pages": list(self.target_pages),
            "tensions": list(self.tensions),
        }
