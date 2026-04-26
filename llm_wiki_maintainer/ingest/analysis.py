from __future__ import annotations

from dataclasses import dataclass, field


def _ensure_str_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise TypeError(f"{field_name} must be a list of strings")
    return value


@dataclass(frozen=True)
class AnalysisArtifact:
    raw_path: str
    key_claims: list[str]
    target_pages: list[str]
    tensions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.raw_path, str):
            raise TypeError("raw_path must be a string")
        _ensure_str_list(self.key_claims, "key_claims")
        _ensure_str_list(self.target_pages, "target_pages")
        _ensure_str_list(self.tensions, "tensions")

    def to_dict(self) -> dict[str, object]:
        return {
            "raw_path": self.raw_path,
            "key_claims": list(self.key_claims),
            "target_pages": list(self.target_pages),
            "tensions": list(self.tensions),
        }
