from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectLayout:
    root: Path
    runtime_dir: Path
    state_dir: Path
    analysis_dir: Path
    generation_dir: Path

    @classmethod
    def from_root(cls, root: Path | str) -> "ProjectLayout":
        root_path = Path(root).resolve()
        runtime_dir = root_path / ".llm-wiki"
        return cls(
            root=root_path,
            runtime_dir=runtime_dir,
            state_dir=runtime_dir / "state",
            analysis_dir=runtime_dir / "analysis",
            generation_dir=runtime_dir / "generation",
        )

    def ensure_runtime_dirs(self) -> list[Path]:
        created = [self.runtime_dir, self.state_dir, self.analysis_dir, self.generation_dir]
        for path in created:
            path.mkdir(parents=True, exist_ok=True)
        return created
