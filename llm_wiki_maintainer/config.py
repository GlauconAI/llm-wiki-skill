from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Union


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    today: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", Path(self.root).expanduser())

    @classmethod
    def from_root(cls, root: Union[str, Path]) -> "RuntimeConfig":
        return cls(root=Path(root).expanduser(), today=date.today().isoformat())
