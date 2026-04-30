from pathlib import Path

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_queue import ResearchQueueStore
from llm_wiki_maintainer.research_runtime import SearchHit
from llm_wiki_maintainer.runtime.api import LlmWikiRuntime
from llm_wiki_maintainer.source_adapters import (
    ADAPTER_STATUS_CODES,
    SourceRegistry,
    execute_research_adapter,
    import_folder_adapter,
)


class FakeSearchProvider:
    def search(self, query: str) -> list[SearchHit]:
        return [SearchHit(title=f"Result {query}", url="https://example.com", snippet="snippet")]


def test_source_registry_exposes_known_adapter_specs(tmp_path: Path):
    registry = SourceRegistry.default(tmp_path / "llm-wiki")

    specs = {spec.key: spec for spec in registry.list()}

    assert ADAPTER_STATUS_CODES == {
        "ready",
        "not_installed",
        "env_unavailable",
        "runtime_failed",
        "unsupported",
        "empty_result",
    }
    assert specs["local_file"].raw_subdir == "raw/sources"
    assert specs["folder_import"].raw_subdir == "raw/imports"
    assert specs["research_task"].raw_subdir == "raw/research"


def test_runtime_facade_reports_adapter_statuses(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)

    statuses = {status.key: status for status in runtime.adapter_statuses()}

    assert statuses["local_file"].status == "ready"
    assert statuses["folder_import"].status == "ready"
    assert statuses["research_task"].status == "env_unavailable"


def test_folder_import_adapter_returns_ready_result_and_enqueues(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.md").write_text("# A\n", encoding="utf-8")
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)

    result = import_folder_adapter(source, root)

    assert result.adapter.key == "folder_import"
    assert result.status.status == "ready"
    assert len(result.imported_paths) == 1
    assert result.imported_paths[0].is_file()


def test_research_adapter_reports_env_unavailable_without_provider(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    ResearchQueueStore(root).save([ResearchTask(topic="market map", queries=["market map 2026"])])

    result = execute_research_adapter(root, provider=None)

    assert result.adapter.key == "research_task"
    assert result.status.status == "env_unavailable"
    assert result.task is None
    assert result.raw_path is None


def test_research_adapter_executes_and_reports_ready_with_provider(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    ResearchQueueStore(root).save([ResearchTask(topic="market map", queries=["market map 2026"])])

    result = execute_research_adapter(root, provider=FakeSearchProvider())

    assert result.adapter.key == "research_task"
    assert result.status.status == "ready"
    assert result.task is not None
    assert result.task.status == "completed"
    assert result.raw_path is not None
    assert result.raw_path.is_file()
