from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

import yaml


DEFAULT_REGISTRY_PATH = Path(
    os.environ.get(
        "LLM_WIKI_REGISTRY_PATH",
        Path.home() / ".codex" / "memories" / "llm-wiki-roots.yaml",
    )
).expanduser()


@dataclass(frozen=True)
class WikiRegistryEntry:
    name: str
    path: Path
    active: bool = False


class WikiRegistry:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path or DEFAULT_REGISTRY_PATH).expanduser().resolve()

    def list(self) -> list[WikiRegistryEntry]:
        data = self._load()
        entries = data.get("entries", [])
        return [
            WikiRegistryEntry(
                name=str(item["name"]),
                path=Path(str(item["path"])).expanduser().resolve(),
                active=bool(item.get("active", False)),
            )
            for item in entries
        ]

    def register(self, name: str, root: Path | str) -> WikiRegistryEntry:
        root_path = Path(root).expanduser().resolve()
        if not looks_like_wiki_root(root_path):
            raise ValueError(f"not an llm-wiki root: {root_path}")
        existing = {entry.name: entry for entry in self.list()}
        entries = [entry for entry in existing.values() if entry.name != name]
        previous = existing.get(name)
        entry = WikiRegistryEntry(name=name, path=root_path, active=previous.active if previous else False)
        entries.append(entry)
        self._save(entries)
        return entry

    def activate(self, name: str) -> WikiRegistryEntry:
        result: WikiRegistryEntry | None = None
        updated: list[WikiRegistryEntry] = []
        for entry in self.list():
            active = entry.name == name
            next_entry = WikiRegistryEntry(name=entry.name, path=entry.path, active=active)
            updated.append(next_entry)
            if active:
                result = next_entry
        if result is None:
            raise KeyError(name)
        self._save(updated)
        return result

    def active(self) -> WikiRegistryEntry:
        for entry in self.list():
            if entry.active:
                return entry
        raise LookupError("no active wiki root")

    def _load(self) -> dict[str, object]:
        if not self.path.exists():
            return {"entries": []}
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError("wiki registry must decode to a mapping")
        entries = data.get("entries", [])
        if not isinstance(entries, list):
            raise ValueError("wiki registry entries must be a list")
        return {"entries": entries}

    def _save(self, entries: list[WikiRegistryEntry]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "entries": [
                {"name": entry.name, "path": str(entry.path), "active": entry.active}
                for entry in sorted(entries, key=lambda item: item.name.lower())
            ]
        }
        self.path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return self.path


def looks_like_wiki_root(root: Path | str) -> bool:
    root_path = Path(root).expanduser().resolve()
    return (root_path / "raw").is_dir() and (root_path / "wiki").is_dir()


def resolve_wiki_root(
    root: Path | str | None = None,
    cwd: Path | str | None = None,
    registry: WikiRegistry | None = None,
) -> Path:
    if root is not None:
        resolved = Path(root).expanduser().resolve()
        if not looks_like_wiki_root(resolved):
            raise ValueError(f"not an llm-wiki root: {resolved}")
        return resolved

    cwd_path = Path(cwd or Path.cwd()).expanduser().resolve()
    if looks_like_wiki_root(cwd_path):
        return cwd_path

    registry_obj = registry or WikiRegistry()
    try:
        return registry_obj.active().path
    except LookupError as exc:
        raise ValueError("no explicit root, cwd wiki root, or active registry root") from exc
