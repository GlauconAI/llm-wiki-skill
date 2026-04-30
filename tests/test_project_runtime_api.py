from pathlib import Path

from dataclasses import dataclass

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.review import ReviewItem
from llm_wiki_maintainer.project import ProjectLayout
from llm_wiki_maintainer.registry import WikiRegistry
from llm_wiki_maintainer.runtime.api import LlmWikiRuntime
from llm_wiki_maintainer.research_runtime import SearchHit
from llm_wiki_maintainer.query.vector import VectorMatch


def test_project_layout_derives_runtime_paths(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    layout = ProjectLayout.from_root(root)

    assert layout.root == root.resolve()
    assert layout.runtime_dir == root.resolve() / ".llm-wiki"
    assert layout.state_dir == root.resolve() / ".llm-wiki" / "state"
    assert layout.analysis_dir == root.resolve() / ".llm-wiki" / "analysis"
    assert layout.generation_dir == root.resolve() / ".llm-wiki" / "generation"


def test_project_layout_ensure_runtime_dirs_creates_expected_directories(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    layout = ProjectLayout.from_root(root)

    created = layout.ensure_runtime_dirs()

    assert layout.runtime_dir.is_dir()
    assert layout.state_dir.is_dir()
    assert layout.analysis_dir.is_dir()
    assert layout.generation_dir.is_dir()
    assert created == [
        layout.runtime_dir,
        layout.state_dir,
        layout.analysis_dir,
        layout.generation_dir,
    ]


def test_runtime_facade_exposes_ingest_query_and_governance_flows(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)
    raw = wiki_root / "raw" / "sources" / "example-raw.md"

    job = runtime.enqueue_ingest(raw)
    completed = runtime.run_next_ingest()
    review_items = runtime.import_review_artifact(runtime.layout.root / completed.generation_artifact)
    runtime.review_queue().save(
        [
            ReviewItem(
                id="rv-research-1",
                title="Research example",
                action="deep_research",
                status="pending",
            )
        ]
    )
    approved = runtime.approve_review("rv-research-1")
    task = runtime.queue_research(
        review_id=approved.id,
        topic="example research",
        queries=["example research 2026"],
    )
    result = runtime.query("example", limit=5, max_chars=200)
    graph = runtime.build_graph()
    related = runtime.related_pages("wiki/overview", limit=5)

    assert job.status == "pending"
    assert completed is not None
    assert completed.status == "completed"
    assert review_items
    assert review_items
    assert approved.status == "approved"
    assert task.topic == "example research"
    assert result.package.pages
    assert "wiki/overview" in graph.nodes
    assert isinstance(related, list)


def test_runtime_facade_reports_graph_insights(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)
    isolated = wiki_root / "wiki" / "isolated.md"
    isolated.write_text(
        """---
type: concept
title: Isolated
sources: []
---

# Isolated
""",
        encoding="utf-8",
    )

    insights = runtime.graph_insights()

    assert "isolated_pages" in insights
    assert "suspicious_isolates" in insights
    assert "wiki/isolated" in insights["isolated_pages"]


def test_runtime_facade_can_be_constructed_from_registry(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    registry = WikiRegistry(tmp_path / "registry.yaml")
    registry.register("main", root)
    registry.activate("main")

    runtime = LlmWikiRuntime.from_registry_or_cwd(cwd=tmp_path, registry=registry)

    assert runtime.root == root.resolve()


@dataclass
class FakeResearchProvider:
    def search(self, query: str) -> list[SearchHit]:
        return [SearchHit(title=f"Result {query}", url="https://example.com", snippet="snippet")]


@dataclass
class FakeVectorProvider:
    def search(self, query: str, root: Path, limit: int = 8) -> list[VectorMatch]:
        return [VectorMatch(path="wiki/overview", score=8.0, excerpt=f"Vector result for {query}")]


def test_runtime_facade_supports_folder_import_research_execution_and_vector_query(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    (root / "wiki" / "overview.md").write_text(
        """---
type: overview
title: Overview
---

# Overview

Example overview page.
""",
        encoding="utf-8",
    )
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.md").write_text("# A\n", encoding="utf-8")

    runtime = LlmWikiRuntime(root)
    imported = runtime.import_folder(source)
    research_store_root = runtime.root
    from llm_wiki_maintainer.research_queue import ResearchQueueStore
    ResearchQueueStore(research_store_root).save([])
    ResearchQueueStore(research_store_root).enqueue(ResearchTask(topic="market map", queries=["market map 2026"]))
    task, raw_path = runtime.execute_next_research(FakeResearchProvider())
    result = runtime.query("example", vector_provider=FakeVectorProvider())
    insights = runtime.graph_insights()

    assert imported
    assert task.status == "completed"
    assert raw_path.is_file()
    assert result.package.pages
    assert "cluster_cohesion_scores" in insights
    assert "knowledge_gaps" in insights
