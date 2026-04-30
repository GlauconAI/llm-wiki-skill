from __future__ import annotations

from dataclasses import dataclass, field

from llm_wiki_maintainer.query.retrieve import RetrievalResult, RetrievedPage


@dataclass(frozen=True)
class QueryContextPackage:
    query: str
    tokens: list[str] = field(default_factory=list)
    pages: list[RetrievedPage] = field(default_factory=list)
    context: str = ""


@dataclass(frozen=True)
class QueryRuntimeResult:
    retrieval: RetrievalResult
    package: QueryContextPackage
