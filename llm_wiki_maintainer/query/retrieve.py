from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.query.tokenize import tokenize_query
from llm_wiki_maintainer.references import COMPILED_FACT_TYPES, parse_frontmatter_type, parse_sources_field


@dataclass(frozen=True)
class RetrievedPage:
    path: Path
    title: str
    score: float
    excerpt: str


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    tokens: list[str] = field(default_factory=list)
    pages: list[RetrievedPage] = field(default_factory=list)


def _page_title(path: Path, text: str) -> str:
    try:
        frontmatter = load_frontmatter(text).data
    except Exception:
        frontmatter = {}
    title = frontmatter.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    return path.stem.replace("-", " ").strip() or path.stem


def _page_text(path: Path, text: str) -> str:
    try:
        body = load_frontmatter(text).body
    except Exception:
        body = text
    return f"{path.stem}\n{text}\n{body}"


def _excerpt(text: str, tokens: Iterable[str]) -> str:
    lower_text = text.lower()
    for token in tokens:
        if not token:
            continue
        index = lower_text.find(token.lower())
        if index == -1:
            continue
        start = max(0, index - 40)
        end = min(len(text), index + len(token) + 80)
        snippet = text[start:end].replace("\n", " ").strip()
        if snippet:
            return snippet
    return text.splitlines()[0].strip() if text else ""


def _score_page(query_tokens: list[str], title: str, content: str, sources: list[str]) -> float:
    if not query_tokens:
        return 0.0
    title_text = title.lower()
    content_text = content.lower()
    source_text = " ".join(sources).lower()
    score = 0.0
    for token in query_tokens:
        lowered = token.lower()
        if lowered in title_text:
            score += 3.0
        if lowered in content_text:
            score += 1.0
        if lowered in source_text:
            score += 1.5
    return score


def retrieve_context(query: str, root: Path, limit: int = 8) -> RetrievalResult:
    root_path = Path(root)
    query_tokens = tokenize_query(query)
    pages: list[RetrievedPage] = []

    for path in sorted((root_path / "wiki").rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if parse_frontmatter_type(text) not in COMPILED_FACT_TYPES:
            continue
        title = _page_title(path, text)
        content = _page_text(path, text)
        sources = parse_sources_field(text)
        score = _score_page(query_tokens, title, content, sources)
        if score <= 0:
            continue
        pages.append(
            RetrievedPage(
                path=path,
                title=title,
                score=score,
                excerpt=_excerpt(content, query_tokens),
            )
        )

    pages.sort(key=lambda page: (-page.score, page.title.lower(), str(page.path)))
    return RetrievalResult(query=query, tokens=query_tokens, pages=pages[:limit])
