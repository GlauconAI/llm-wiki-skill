from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

MANIFEST_PATH = ".llm-wiki/ingest-manifest.yaml"


@dataclass
class SourceManifest:
    hashes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def empty(cls) -> "SourceManifest":
        return cls()

    @classmethod
    def load(cls, root: Path) -> "SourceManifest":
        path = Path(root) / MANIFEST_PATH
        if not path.exists():
            return cls.empty()
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        hashes = data.get("hashes", {})
        if not isinstance(hashes, dict):
            raise ValueError("ingest manifest hashes must be a mapping")
        return cls(hashes={str(key): str(value) for key, value in hashes.items()})

    def has_changed(self, path: Path) -> bool:
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        previous = self.hashes.get(str(Path(path)))
        return previous != digest

    def remember(self, path: Path) -> None:
        self.hashes[str(Path(path))] = hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def save(self, root: Path) -> Path:
        path = Path(root) / MANIFEST_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump({"hashes": self.hashes}, sort_keys=True),
            encoding="utf-8",
        )
        return path
