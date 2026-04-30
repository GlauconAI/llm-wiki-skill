from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class VectorMatch:
    path: str
    score: float
    excerpt: str


class VectorSearchProvider(Protocol):
    def search(self, query: str, root: Path, limit: int = 8) -> list[VectorMatch]:
        ...
