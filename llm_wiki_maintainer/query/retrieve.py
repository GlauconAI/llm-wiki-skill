from __future__ import annotations

from dataclasses import dataclass, field
import re
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
    return ""


def _page_text(path: Path, text: str) -> str:
    try:
        document = load_frontmatter(text)
    except Exception:
        return text.strip()
    return document.body.strip()


def _page_excerpt_source(path: Path, text: str, tokens: Iterable[str], sources: Iterable[str]) -> str:
    try:
        document = load_frontmatter(text)
    except Exception:
        body = text.strip()
        title = ""
    else:
        body = document.body.strip()
        title = _page_title(path, text)

    body_matches = body and any(_token_match(body.lower(), token) is not None for token in tokens if token)
    if body_matches:
        return body

    title_matches = title and any(_token_match(title.lower(), token) is not None for token in tokens if token)
    if title_matches:
        return title

    for source in sources:
        source_text = source.lower()
        if any(_token_match(source_text, token) is not None for token in tokens if token):
            return f"Source match: {source}"

    if body:
        return body
    if title:
        return title
    return path.stem.replace("-", " ").strip() or path.stem


def _excerpt(text: str, tokens: Iterable[str]) -> str:
    lower_text = text.lower()
    for token in tokens:
        if not token:
            continue
        match = _token_match(lower_text, token)
        if match is None:
            continue
        start, end_index = match
        end = min(len(text), end_index + 80)
        start = max(0, start - 40)
        snippet = text[start:end].replace("\n", " ").strip()
        if snippet:
            return snippet
    return text.splitlines()[0].strip() if text else ""


def _token_match(text: str, token: str) -> tuple[int, int] | None:
    lowered = token.lower()
    if lowered.isascii():
        match = re.search(rf"\b{re.escape(lowered)}\b", text)
        if match is None:
            return None
        return match.span()
    index = text.find(lowered)
    if index == -1:
        return None
    return index, index + len(lowered)


def _score_page(query_tokens: list[str], title: str, content: str, sources: list[str]) -> float:
    if not query_tokens:
        return 0.0
    title_text = title.lower()
    content_text = content.lower()
    source_text = " ".join(sources).lower()
    score = 0.0
    for token in query_tokens:
        if _token_match(title_text, token) is not None:
            score += 3.0
        if _token_match(content_text, token) is not None:
            score += 1.0
        if _token_match(source_text, token) is not None:
            score += 1.5
    return score


def retrieve_context(query: str, root: Path, limit: int = 8) -> RetrievalResult:
    root_path = Path(root)
    query_tokens = tokenize_query(query)
    limit = max(0, int(limit))
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
                excerpt=_excerpt(_page_excerpt_source(path, text, query_tokens, sources), query_tokens),
            )
        )

    pages.sort(key=lambda page: (-page.score, page.title.lower(), str(page.path)))
    return RetrievalResult(query=query, tokens=query_tokens, pages=pages[:limit])
