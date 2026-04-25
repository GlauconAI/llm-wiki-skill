from dataclasses import dataclass
from typing import Any


@dataclass
class FrontmatterDocument:
    data: dict[str, Any]
    body: str
