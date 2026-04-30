from __future__ import annotations

from pathlib import Path

from llm_wiki_maintainer.graph.build import WikiGraph, build_graph
from llm_wiki_maintainer.graph.insights import (
    cluster_cohesion_scores,
    find_bridge_pages,
    find_dense_page_clusters,
    find_isolated_pages,
    find_knowledge_gaps,
    find_orphaned_source_cards,
    find_suspicious_isolates,
)
from llm_wiki_maintainer.graph.relevance import RelatedPage, related_pages
from llm_wiki_maintainer.importer import import_folder
from llm_wiki_maintainer.project import ProjectLayout
from llm_wiki_maintainer.query.models import QueryRuntimeResult
from llm_wiki_maintainer.query.runtime import query_runtime
from llm_wiki_maintainer.query.vector import VectorSearchProvider
from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_runtime import SearchProvider, execute_next_research, queue_research_from_review
from llm_wiki_maintainer.review import ReviewItem
from llm_wiki_maintainer.review_queue import ReviewQueueStore
from llm_wiki_maintainer.registry import WikiRegistry, resolve_wiki_root
from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue
from llm_wiki_maintainer.runtime.jobs import IngestJob
from llm_wiki_maintainer.source_adapters import (
    AdapterStatus,
    FolderImportResult,
    ResearchAdapterResult,
    SourceRegistry,
    execute_research_adapter,
    import_folder_adapter,
)
from llm_wiki_maintainer.workflows import (
    CrystalNote,
    DeleteSourceResult,
    DigestNote,
    QueryNote,
    WorkflowStatus,
    create_digest,
    crystallize_note,
    delete_source,
    project_status,
    save_query_note,
)


class LlmWikiRuntime:
    @classmethod
    def from_registry_or_cwd(
        cls,
        root: Path | str | None = None,
        cwd: Path | str | None = None,
        registry: WikiRegistry | None = None,
    ) -> "LlmWikiRuntime":
        return cls(resolve_wiki_root(root=root, cwd=cwd, registry=registry))

    def __init__(self, root: Path | str):
        self.layout = ProjectLayout.from_root(root)
        self.layout.ensure_runtime_dirs()

    @property
    def root(self) -> Path:
        return self.layout.root

    def ingest_queue(self) -> IngestQueue:
        return IngestQueue(self.root)

    def review_queue(self) -> ReviewQueueStore:
        return ReviewQueueStore(self.root)

    def enqueue_ingest(self, raw_path: Path | str) -> IngestJob:
        return self.ingest_queue().enqueue(raw_path)

    def run_next_ingest(self) -> IngestJob | None:
        return self.ingest_queue().run_next()

    def retry_ingest(self, job_id: str) -> IngestJob:
        return self.ingest_queue().retry(job_id)

    def cancel_ingest(self, job_id: str) -> IngestJob:
        return self.ingest_queue().cancel(job_id)

    def import_folder(self, source_dir: Path | str) -> list[Path]:
        return import_folder(source_dir, self.root)

    def import_folder_with_adapter(self, source_dir: Path | str) -> FolderImportResult:
        return import_folder_adapter(source_dir, self.root)

    def import_review_artifact(self, artifact_path: Path | str) -> list[ReviewItem]:
        return self.review_queue().import_generation_artifact(artifact_path)

    def approve_review(self, review_id: str) -> ReviewItem:
        return self.review_queue().approve(review_id)

    def reject_review(self, review_id: str) -> ReviewItem:
        return self.review_queue().reject(review_id)

    def queue_research(
        self,
        review_id: str,
        topic: str,
        queries: list[str],
        override: bool = False,
    ) -> ResearchTask:
        return queue_research_from_review(
            self.root,
            review_id=review_id,
            topic=topic,
            queries=queries,
            override=override,
        )

    def execute_next_research(self, provider: SearchProvider) -> tuple[ResearchTask, Path]:
        return execute_next_research(self.root, provider)

    def execute_next_research_with_adapter(
        self,
        provider: SearchProvider | None,
    ) -> ResearchAdapterResult:
        return execute_research_adapter(self.root, provider)

    def query(
        self,
        query_text: str,
        limit: int = 8,
        max_chars: int = 2000,
        vector_provider: VectorSearchProvider | None = None,
    ) -> QueryRuntimeResult:
        return query_runtime(
            query_text,
            self.root,
            limit=limit,
            max_chars=max_chars,
            vector_provider=vector_provider,
        )

    def build_graph(self) -> WikiGraph:
        return build_graph(self.root)

    def related_pages(self, page_id: str, limit: int = 5) -> list[RelatedPage]:
        return related_pages(self.build_graph(), page_id, limit=limit)

    def graph_insights(self) -> dict[str, object]:
        graph = self.build_graph()
        return {
            "isolated_pages": find_isolated_pages(graph),
            "bridge_pages": find_bridge_pages(graph),
            "orphaned_source_cards": find_orphaned_source_cards(graph),
            "dense_page_clusters": find_dense_page_clusters(graph),
            "cluster_cohesion_scores": cluster_cohesion_scores(graph),
            "knowledge_gaps": find_knowledge_gaps(graph),
            "suspicious_isolates": find_suspicious_isolates(graph),
        }

    def source_registry(self) -> SourceRegistry:
        return SourceRegistry.default(self.root)

    def adapter_statuses(self, research_provider_available: bool = False) -> list[AdapterStatus]:
        return self.source_registry().statuses(research_provider_available=research_provider_available)

    def status(self) -> WorkflowStatus:
        return project_status(self.root)

    def create_digest(
        self,
        query_text: str,
        title: str | None = None,
        limit: int = 8,
        max_chars: int = 2000,
    ) -> DigestNote:
        return create_digest(self.root, query_text, title=title, limit=limit, max_chars=max_chars)

    def save_query(
        self,
        query_text: str,
        title: str | None = None,
        limit: int = 8,
        max_chars: int = 2000,
    ) -> QueryNote:
        return save_query_note(self.root, query_text, title=title, limit=limit, max_chars=max_chars)

    def crystallize(
        self,
        title: str,
        summary: str,
        bullets: list[str] | None = None,
        sources: list[str] | None = None,
    ) -> CrystalNote:
        return crystallize_note(
            self.root,
            title=title,
            summary=summary,
            bullets=bullets,
            sources=sources,
        )

    def delete_source(self, raw_path: Path | str, apply: bool = False) -> DeleteSourceResult:
        return delete_source(self.root, raw_path, apply=apply)
