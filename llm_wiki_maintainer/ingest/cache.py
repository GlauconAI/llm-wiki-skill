from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

MANIFEST_PATH = ".llm-wiki/ingest-manifest.yaml"


@dataclass
class SourceManifest:
    root: Path | None = None
    hashes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def empty(cls, root: Path | None = None) -> "SourceManifest":
        return cls(root=Path(root).resolve() if root is not None else None)

    @classmethod
    def load(cls, root: Path) -> "SourceManifest":
        root_path = Path(root).resolve()
        path = root_path / MANIFEST_PATH
        if not path.exists():
            return cls.empty(root_path)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError("ingest manifest must decode to a mapping")
        hashes = data.get("hashes", {})
        if not isinstance(hashes, dict):
            raise ValueError("ingest manifest hashes must be a mapping")
        return cls(
            root=root_path,
            hashes={str(key): str(value) for key, value in hashes.items()},
        )

    def _key(self, path: Path) -> str:
        path = Path(path)
        if self.root is None:
            return path.resolve(strict=False).as_posix()

        root = self.root
        resolved = path if path.is_absolute() else root / path
        resolved = resolved.resolve(strict=False)
        try:
            return resolved.relative_to(root).as_posix()
        except ValueError:
            return resolved.as_posix()

    def _resolved_path(self, path: Path) -> Path:
        path = Path(path)
        if self.root is None or path.is_absolute():
            return path
        return (self.root / path).resolve(strict=False)

    def has_changed(self, path: Path) -> bool:
        key = self._key(path)
        try:
            digest = hashlib.sha256(self._resolved_path(path).read_bytes()).hexdigest()
        except FileNotFoundError:
            return True
        previous = self.hashes.get(key)
        return previous != digest

    def remember(self, path: Path) -> None:
        self.hashes[self._key(path)] = hashlib.sha256(self._resolved_path(path).read_bytes()).hexdigest()

    def save(self, root: Path) -> Path:
        path = Path(root) / MANIFEST_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump({"hashes": self.hashes}, sort_keys=True),
            encoding="utf-8",
        )
        return path
