from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re

from llm_wiki_maintainer.frontmatter import load_frontmatter

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}|[\u4e00-\u9fff]{2,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "what",
    "when",
    "where",
    "which",
    "openclaw",
    "wiki",
    "page",
    "pages",
    "topic",
    "topics",
    "concept",
    "concepts",
    "entity",
    "entities",
    "agent",
    "agents",
    "system",
    "systems",
    "note",
    "notes",
    "raw",
    "source",
    "sources",
    "overview",
    "当前",
    "可以",
    "什么",
    "如何",
    "以及",
    "不是",
    "一个",
    "这类",
    "页面",
    "系统",
    "主题",
    "知识",
}
COMPILED_PAGE_TYPES = {"overview", "concept", "entity", "topic"}


@dataclass(frozen=True)
class TargetPageCandidate:
    score: int
    path: str
    title: str
    page_type: str


def _document_parts(text: str) -> tuple[dict[str, object], str]:
    try:
        document = load_frontmatter(text)
    except ValueError:
        return {}, text
    return document.data, document.body


def _parse_title(text: str, fallback: str) -> str:
    data, _body = _document_parts(text)
    value = data.get("title")
    return str(value).strip() if value else fallback


def _parse_type(text: str) -> str | None:
    data, _body = _document_parts(text)
    value = data.get("type")
    return str(value).strip() if value else None


def _body_without_frontmatter(text: str) -> str:
    _data, body = _document_parts(text)
    return body


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in WORD_RE.findall(text.lower())
        if len(token) >= 2 and token not in STOPWORDS
    ]


def weighted_tokens(raw_text: str, raw_file: Path) -> Counter[str]:
    body = _body_without_frontmatter(raw_text)
    title = _parse_title(raw_text, raw_file.stem)
    tokens: list[str] = []
    tokens.extend(tokenize(raw_file.stem) * 4)
    tokens.extend(tokenize(title) * 5)
    tokens.extend(tokenize(body[:4000]))
    return Counter(tokens)


def page_score(raw_counter: Counter[str], title: str, rel_path: str, text: str) -> int:
    title_tokens = tokenize(title)
    path_tokens = tokenize(rel_path.replace("/", " "))
    body_tokens = tokenize(_body_without_frontmatter(text)[:2500])
    score = 0
    for token in title_tokens:
        score += raw_counter[token] * 5
    for token in path_tokens:
        score += raw_counter[token] * 3
    for token in set(body_tokens):
        score += min(raw_counter[token], 2)
    return score


def suggest_target_pages(raw_file: Path, root: Path) -> list[TargetPageCandidate]:
    raw_path = Path(raw_file)
    root_path = Path(root)
    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
    raw_counter = weighted_tokens(raw_text, raw_path)
    candidates: list[TargetPageCandidate] = []

    for path in sorted((root_path / "wiki").rglob("*.md")):
        relative_path = path.relative_to(root_path).as_posix()
        if "/sources/" in relative_path or "/reports/" in relative_path:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        page_type = _parse_type(text)
        if page_type not in COMPILED_PAGE_TYPES:
            continue
        title = _parse_title(text, path.stem)
        page_path = relative_path[:-3]
        score = page_score(raw_counter, title, page_path, text)
        if score > 0:
            candidates.append(
                TargetPageCandidate(
                    score=score,
                    path=page_path,
                    title=title,
                    page_type=page_type,
                )
            )

    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
