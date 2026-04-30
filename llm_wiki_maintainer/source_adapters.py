from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from llm_wiki_maintainer.importer import import_folder
from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_runtime import SearchProvider, execute_next_research


ADAPTER_STATUS_CODES = {
    "ready",
    "not_installed",
    "env_unavailable",
    "runtime_failed",
    "unsupported",
    "empty_result",
}


@dataclass(frozen=True)
class AdapterSpec:
    key: str
    input_mode: str
    raw_subdir: str
    adapter_name: str
    fallback_hint: str


@dataclass(frozen=True)
class AdapterStatus:
    key: str
    status: str
    detail: str = ""
    fallback_hint: str = ""

    def __post_init__(self) -> None:
        if self.status not in ADAPTER_STATUS_CODES:
            raise ValueError(f"invalid adapter status: {self.status}")


@dataclass(frozen=True)
class FolderImportResult:
    adapter: AdapterSpec
    status: AdapterStatus
    imported_paths: list[Path]


@dataclass(frozen=True)
class ResearchAdapterResult:
    adapter: AdapterSpec
    status: AdapterStatus
    task: ResearchTask | None = None
    raw_path: Path | None = None


class SourceRegistry:
    def __init__(self, root: Path | str, specs: list[AdapterSpec]):
        self.root = Path(root).resolve()
        self._specs = list(specs)

    @classmethod
    def default(cls, root: Path | str) -> "SourceRegistry":
        return cls(
            root,
            specs=[
                AdapterSpec(
                    key="local_file",
                    input_mode="file",
                    raw_subdir="raw/sources",
                    adapter_name="filesystem",
                    fallback_hint="Place the file directly under raw/sources/ if needed.",
                ),
                AdapterSpec(
                    key="folder_import",
                    input_mode="directory",
                    raw_subdir="raw/imports",
                    adapter_name="filesystem_batch",
                    fallback_hint="Use scripts/import_folder.py to batch-copy local materials.",
                ),
                AdapterSpec(
                    key="research_task",
                    input_mode="query_batch",
                    raw_subdir="raw/research",
                    adapter_name="search_provider",
                    fallback_hint="Provide a search provider before running queued research.",
                ),
            ],
        )

    def list(self) -> list[AdapterSpec]:
        return list(self._specs)

    def get(self, key: str) -> AdapterSpec:
        for spec in self._specs:
            if spec.key == key:
                return spec
        raise KeyError(key)

    def statuses(self, research_provider_available: bool = False) -> list[AdapterStatus]:
        results: list[AdapterStatus] = []
        for spec in self._specs:
            if spec.key == "research_task" and not research_provider_available:
                results.append(
                    AdapterStatus(
                        key=spec.key,
                        status="env_unavailable",
                        detail="No search provider is attached to the runtime.",
                        fallback_hint=spec.fallback_hint,
                    )
                )
                continue
            results.append(AdapterStatus(key=spec.key, status="ready", fallback_hint=spec.fallback_hint))
        return results


def import_folder_adapter(source_dir: Path | str, root: Path | str) -> FolderImportResult:
    registry = SourceRegistry.default(root)
    adapter = registry.get("folder_import")
    imported = import_folder(source_dir, root)
    status_code = "ready" if imported else "empty_result"
    detail = "" if imported else "The source directory produced no importable files."
    return FolderImportResult(
        adapter=adapter,
        status=AdapterStatus(
            key=adapter.key,
            status=status_code,
            detail=detail,
            fallback_hint=adapter.fallback_hint,
        ),
        imported_paths=imported,
    )


def execute_research_adapter(
    root: Path | str,
    provider: SearchProvider | None,
) -> ResearchAdapterResult:
    registry = SourceRegistry.default(root)
    adapter = registry.get("research_task")
    if provider is None:
        return ResearchAdapterResult(
            adapter=adapter,
            status=AdapterStatus(
                key=adapter.key,
                status="env_unavailable",
                detail="No search provider is attached to the runtime.",
                fallback_hint=adapter.fallback_hint,
            ),
        )
    try:
        task, raw_path = execute_next_research(root, provider)
    except LookupError as exc:
        return ResearchAdapterResult(
            adapter=adapter,
            status=AdapterStatus(
                key=adapter.key,
                status="empty_result",
                detail=str(exc),
                fallback_hint=adapter.fallback_hint,
            ),
        )
    except Exception as exc:
        return ResearchAdapterResult(
            adapter=adapter,
            status=AdapterStatus(
                key=adapter.key,
                status="runtime_failed",
                detail=str(exc),
                fallback_hint=adapter.fallback_hint,
            ),
        )
    return ResearchAdapterResult(
        adapter=adapter,
        status=AdapterStatus(key=adapter.key, status="ready", fallback_hint=adapter.fallback_hint),
        task=task,
        raw_path=raw_path,
    )
