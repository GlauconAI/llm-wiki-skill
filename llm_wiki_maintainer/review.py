from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ReviewItem:
    id: str
    title: str
    action: str
    status: str

    def approve(self) -> ReviewItem:
        return replace(self, status="approved")
