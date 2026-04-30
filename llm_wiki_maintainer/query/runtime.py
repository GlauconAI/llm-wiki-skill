from __future__ import annotations

from pathlib import Path

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.query.assemble import assemble_context
from llm_wiki_maintainer.query.models import QueryRuntimeResult
from llm_wiki_maintainer.query.retrieve import RetrievalResult, RetrievedPage, retrieve_context
from llm_wiki_maintainer.query.vector import VectorSearchProvider


def query_runtime(
    query: str,
    root: Path | str,
    limit: int = 8,
    max_chars: int = 2000,
    vector_provider: VectorSearchProvider | None = None,
) -> QueryRuntimeResult:
    root_path = Path(root)
    retrieval = retrieve_context(query, root_path, limit=limit)
    if vector_provider is not None:
        retrieval = _merge_vector_matches(retrieval, root_path, vector_provider, limit=limit)
    package = assemble_context(retrieval, max_chars=max_chars)
    return QueryRuntimeResult(retrieval=retrieval, package=package)


def _merge_vector_matches(
    retrieval: RetrievalResult,
    root: Path,
    vector_provider: VectorSearchProvider,
    limit: int,
) -> RetrievalResult:
    pages_by_key = {
        page.path.relative_to(root).with_suffix("").as_posix(): page
        for page in retrieval.pages
    }
    for match in vector_provider.search(retrieval.query, root, limit=limit):
        existing = pages_by_key.get(match.path)
        if existing is not None:
            pages_by_key[match.path] = RetrievedPage(
                path=existing.path,
                title=existing.title,
                score=max(existing.score, float(match.score)),
                excerpt=match.excerpt or existing.excerpt,
            )
            continue

        page_path = root / f"{match.path}.md"
        if not page_path.is_file():
            continue
        text = page_path.read_text(encoding="utf-8", errors="replace")
        try:
            title = str(load_frontmatter(text).data.get("title") or page_path.stem)
        except Exception:
            title = page_path.stem
        pages_by_key[match.path] = RetrievedPage(
            path=page_path,
            title=title,
            score=float(match.score),
            excerpt=match.excerpt,
        )

    merged_pages = sorted(
        pages_by_key.values(),
        key=lambda page: (-page.score, page.title.lower(), str(page.path)),
    )[: max(0, int(limit))]
    return RetrievalResult(query=retrieval.query, tokens=list(retrieval.tokens), pages=merged_pages)
