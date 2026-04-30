from __future__ import annotations

from llm_wiki_maintainer.query.models import QueryContextPackage
from llm_wiki_maintainer.query.retrieve import RetrievalResult


def assemble_context(retrieval: RetrievalResult, max_chars: int = 2000) -> QueryContextPackage:
    limit = max(0, int(max_chars))
    blocks: list[str] = []
    used = 0
    for page in retrieval.pages:
        block = f"{page.title}\n{page.excerpt}".strip()
        if not block:
            continue
        separator = "\n\n" if blocks else ""
        available = limit - used - len(separator)
        if available <= 0:
            break
        if len(block) > available:
            block = block[:available].rstrip()
        blocks.append(block)
        used += len(separator) + len(block)
        if used >= limit:
            break

    return QueryContextPackage(
        query=retrieval.query,
        tokens=list(retrieval.tokens),
        pages=list(retrieval.pages),
        context="\n\n".join(blocks),
    )
