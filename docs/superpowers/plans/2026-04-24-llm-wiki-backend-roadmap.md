# LLM Wiki Backend Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve this repository from a rule-heavy agent skill plus helper scripts into a reliable LLM Wiki backend, then extend that backend into a full runtime that closes ingest, query, graph, review, research, and lifecycle loops.

**Architecture:** Stage A builds a reusable Python backend under a real package boundary and converts the current scripts into thin CLI wrappers. Stage B layers higher-order runtime modules on top of that backend: two-step ingest orchestration, lexical query retrieval, graph analysis, review queues, research hooks, and source lifecycle reconciliation. The backend remains Obsidian-compatible and retains the current raw/wiki/wiki-sources discipline.

**Tech Stack:** Python 3.9+, `pytest`, `dataclasses`, `pathlib`, `yaml` parsing via `PyYAML` or `ruamel.yaml`, optional `networkx` for graph operations, markdown-based fixtures.

**Current constraints:** This workspace is not currently a git worktree, so commit steps should be treated as checkpoints. If implementation later happens in a git repo, use the commit messages shown below.

---

## File Structure Map

### Existing files to keep and refactor
- `SKILL.md` — skill contract and operator guidance.
- `scripts/create_source_card.py` — CLI wrapper for source-card creation.
- `scripts/create_audit_report.py` — CLI wrapper for audit-report scaffold generation.
- `scripts/create_ingest_report.py` — CLI wrapper for ingest-report scaffold generation.
- `scripts/suggest_target_pages.py` — CLI wrapper for query-time candidate discovery.
- `scripts/update_used_by.py` — CLI wrapper for source-card dependency reconciliation.
- `scripts/lint_llm_wiki.py` — CLI wrapper for structural linting.

### New package layout
- Create: `llm_wiki_maintainer/__init__.py` — package marker.
- Create: `llm_wiki_maintainer/config.py` — root paths, dates, and runtime settings.
- Create: `llm_wiki_maintainer/models.py` — core dataclasses for pages, sources, reports, queue items, review items.
- Create: `llm_wiki_maintainer/frontmatter.py` — robust frontmatter load/dump helpers.
- Create: `llm_wiki_maintainer/wiki_io.py` — file reads, writes, existence checks, safe directory creation.
- Create: `llm_wiki_maintainer/links.py` — wikilink parsing and validation.
- Create: `llm_wiki_maintainer/source_cards.py` — source-card generation and duplicate detection.
- Create: `llm_wiki_maintainer/reports.py` — audit and ingest report scaffold generation.
- Create: `llm_wiki_maintainer/linting.py` — reusable lint engine.
- Create: `llm_wiki_maintainer/references.py` — `Used by` synchronization and source-reference helpers.
- Create: `llm_wiki_maintainer/ingest/cache.py` — hash-based source manifest.
- Create: `llm_wiki_maintainer/ingest/planner.py` — affected-page planning and ingest actions.
- Create: `llm_wiki_maintainer/ingest/analysis.py` — Stage-B analysis artifact schema.
- Create: `llm_wiki_maintainer/ingest/generation.py` — Stage-B generation artifact schema and validation.
- Create: `llm_wiki_maintainer/query/tokenize.py` — lexical tokenization for EN/ZH.
- Create: `llm_wiki_maintainer/query/retrieve.py` — lexical ranking and context assembly.
- Create: `llm_wiki_maintainer/graph/build.py` — graph extraction from pages and sources.
- Create: `llm_wiki_maintainer/graph/insights.py` — gaps, bridges, and weak-cluster heuristics.
- Create: `llm_wiki_maintainer/review.py` — review-item storage and state transitions.
- Create: `llm_wiki_maintainer/research.py` — research task schema and provider hooks.
- Create: `llm_wiki_maintainer/lifecycle.py` — source deletion and rename reconciliation.

### Tests and fixtures
- Create: `tests/conftest.py`
- Create: `tests/fixtures/wiki_minimal/...`
- Create: `tests/test_frontmatter.py`
- Create: `tests/test_source_cards.py`
- Create: `tests/test_linting.py`
- Create: `tests/test_references.py`
- Create: `tests/test_ingest_cache.py`
- Create: `tests/test_ingest_planner.py`
- Create: `tests/test_query_retrieve.py`
- Create: `tests/test_graph_build.py`
- Create: `tests/test_review.py`
- Create: `tests/test_lifecycle.py`

## Stage A: Strong Backend + Strong Rules Layer

### Task 1: Establish Package Boundary and Test Harness

**Files:**
- Create: `llm_wiki_maintainer/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/fixtures/wiki_minimal/index.md`
- Create: `tests/fixtures/wiki_minimal/wiki/overview.md`
- Create: `tests/fixtures/wiki_minimal/wiki/sources/example-source.md`
- Create: `tests/fixtures/wiki_minimal/raw/sources/example-raw.md`

- [ ] **Step 1: Create the package marker**

```python
"""Core backend for the llm-wiki-maintainer skill."""
```

- [ ] **Step 2: Create fixture-copy helper**

```python
from pathlib import Path
import shutil

import pytest


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    src = Path(__file__).parent / "fixtures" / "wiki_minimal"
    dst = tmp_path / "llm-wiki"
    shutil.copytree(src, dst)
    return dst
```

- [ ] **Step 3: Add a minimal fixture vault**

```md
---
type: overview
title: Overview
sources: []
---

# Overview

## TL;DR
- Minimal fixture.

## Core Knowledge
- Fixture knowledge with [[raw/sources/example-raw|/raw/sources/example-raw.md]].

## Decision-Relevant Details
- Example detail.

## Constraints / Exceptions
- Example constraint.

## Related Pages
- [[wiki/overview]]

## Raw Source Pointers
- [[raw/sources/example-raw|/raw/sources/example-raw.md]]
```

- [ ] **Step 4: Run the empty harness**

Run: `pytest tests -q`  
Expected: collection succeeds once tests are added.

- [ ] **Step 5: Checkpoint**

If in git: `git commit -m "chore: add backend package scaffold and fixtures"`

### Task 2: Replace Fragile Regex-Only Frontmatter Handling

**Files:**
- Create: `llm_wiki_maintainer/frontmatter.py`
- Create: `llm_wiki_maintainer/models.py`
- Create: `tests/test_frontmatter.py`

- [ ] **Step 1: Write the failing tests**

```python
from llm_wiki_maintainer.frontmatter import load_frontmatter


def test_load_frontmatter_supports_inline_sources():
    text = "---\ntype: concept\nsources: [SRC-1, SRC-2]\n---\nbody\n"
    doc = load_frontmatter(text)
    assert doc.data["sources"] == ["SRC-1", "SRC-2"]


def test_load_frontmatter_supports_multiline_yaml_list():
    text = "---\ntype: concept\nsources:\n  - SRC-1\n  - SRC-2\n---\nbody\n"
    doc = load_frontmatter(text)
    assert doc.data["sources"] == ["SRC-1", "SRC-2"]
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_frontmatter.py -q`  
Expected: FAIL because `load_frontmatter` does not exist.

- [ ] **Step 3: Implement normalized frontmatter helpers**

```python
from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class FrontmatterDocument:
    data: dict[str, Any]
    body: str


def load_frontmatter(text: str) -> FrontmatterDocument:
    if not text.startswith("---\n"):
        return FrontmatterDocument(data={}, body=text)
    _, raw_block, body = text.split("---\n", 2)
    data = yaml.safe_load(raw_block) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must decode to a mapping")
    return FrontmatterDocument(data=data, body=body)
```

- [ ] **Step 4: Add dump helper with stable list normalization**

```python
def dump_frontmatter(data: dict[str, Any], body: str) -> str:
    normalized = dict(data)
    if isinstance(normalized.get("sources"), tuple):
        normalized["sources"] = list(normalized["sources"])
    return "---\n" + yaml.safe_dump(normalized, sort_keys=False).strip() + "\n---\n" + body.lstrip("\n")
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_frontmatter.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add robust frontmatter parsing"`

### Task 3: Centralize Config, Dates, and Safe File IO

**Files:**
- Create: `llm_wiki_maintainer/config.py`
- Create: `llm_wiki_maintainer/wiki_io.py`
- Create: `tests/test_source_cards.py`

- [ ] **Step 1: Write failing tests for date generation and parent-directory creation**

```python
from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.wiki_io import write_text


def test_runtime_config_uses_dynamic_today():
    cfg = RuntimeConfig(root="/tmp/wiki", today="2026-04-24")
    assert cfg.today == "2026-04-24"


def test_write_text_creates_parent_directories(tmp_path):
    target = tmp_path / "wiki" / "reports" / "report.md"
    write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_source_cards.py -q`  
Expected: FAIL because helpers do not exist.

- [ ] **Step 3: Implement runtime config and safe writes**

```python
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    today: str

    @classmethod
    def from_root(cls, root: str | Path) -> "RuntimeConfig":
        return cls(root=Path(root).expanduser(), today=date.today().isoformat())
```

```python
from pathlib import Path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
```

- [ ] **Step 4: Re-run tests**

Run: `pytest tests/test_source_cards.py -q`  
Expected: PASS

- [ ] **Step 5: Checkpoint**

If in git: `git commit -m "feat: add runtime config and safe file io"`

### Task 4: Refactor Source-Card Creation into a Real Library Module

**Files:**
- Create: `llm_wiki_maintainer/source_cards.py`
- Modify: `scripts/create_source_card.py`
- Create: `tests/test_source_cards.py`

- [ ] **Step 1: Add failing tests for duplicate detection and dynamic dates**

```python
from llm_wiki_maintainer.source_cards import create_source_card


def test_create_source_card_avoids_duplicate_when_location_matches(wiki_root):
    raw_file = wiki_root / "raw" / "sources" / "example-raw.md"
    result = create_source_card(raw_file, wiki_root, today="2026-04-24")
    assert result.status == "exists"


def test_create_source_card_writes_today_in_metadata(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "new-note.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# New Note\n", encoding="utf-8")
    result = create_source_card(raw, root, today="2026-04-24")
    assert "created: 2026-04-24" in result.path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_source_cards.py -q`  
Expected: FAIL because `create_source_card` is not implemented.

- [ ] **Step 3: Implement library-first source-card creation**

```python
from dataclasses import dataclass
from pathlib import Path

from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.wiki_io import write_text


@dataclass
class SourceCardResult:
    status: str
    path: Path


def create_source_card(raw_file: Path, root: Path, today: str) -> SourceCardResult:
    existing = find_existing_card_for_raw(root, raw_file)
    if existing is not None:
        return SourceCardResult(status="exists", path=existing)
    out = build_source_card_path(raw_file, root)
    write_text(out, render_source_card(raw_file, root, today=today))
    return SourceCardResult(status="created", path=out)
```

- [ ] **Step 4: Detect existing cards by parsing `## Location` wikilinks, not raw string equality**

```python
def find_existing_card_for_raw(root: Path, raw_file: Path) -> Path | None:
    rel_raw = raw_file.relative_to(root).as_posix()
    for card in (root / "wiki" / "sources").glob("*.md"):
        text = card.read_text(encoding="utf-8", errors="replace")
        if f"[[raw/sources/{raw_file.stem}" in text or f"|/{rel_raw}]]" in text:
            return card
    return None
```

- [ ] **Step 5: Convert script to thin CLI wrapper**

```python
from llm_wiki_maintainer.source_cards import create_source_card

result = create_source_card(raw_file, root, today=cfg.today)
print(f"{result.status}: {result.path}")
```

- [ ] **Step 6: Re-run tests**

Run: `pytest tests/test_source_cards.py -q`  
Expected: PASS

- [ ] **Step 7: Checkpoint**

If in git: `git commit -m "refactor: move source-card generation into backend module"`

### Task 5: Refactor Linting and Reference Sync into Shared Services

**Files:**
- Create: `llm_wiki_maintainer/links.py`
- Create: `llm_wiki_maintainer/linting.py`
- Create: `llm_wiki_maintainer/references.py`
- Modify: `scripts/lint_llm_wiki.py`
- Modify: `scripts/update_used_by.py`
- Create: `tests/test_linting.py`
- Create: `tests/test_references.py`

- [ ] **Step 1: Write failing tests for multiline `sources:` and Used-by reconciliation**

```python
from llm_wiki_maintainer.references import compute_used_by


def test_compute_used_by_supports_multiline_sources(wiki_root):
    page = wiki_root / "wiki" / "topic-a.md"
    page.write_text(
        "---\ntype: topic\nsources:\n  - SRC-1\n---\n# Topic\n",
        encoding="utf-8",
    )
    mapping = compute_used_by(wiki_root)
    assert mapping
```

```python
from llm_wiki_maintainer.linting import lint_root


def test_lint_root_returns_problem_objects(wiki_root):
    problems = lint_root(wiki_root)
    assert isinstance(problems, list)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_linting.py tests/test_references.py -q`  
Expected: FAIL because services do not exist.

- [ ] **Step 3: Implement reusable lint and reference services**

```python
from dataclasses import dataclass


@dataclass
class LintProblem:
    path: str
    message: str
    severity: str = "error"
```

```python
def compute_used_by(root):
    # walk compiled pages, parse normalized frontmatter, map source ids to pages
    ...
```

```python
def lint_root(root):
    # return list[LintProblem] instead of printing directly
    ...
```

- [ ] **Step 4: Keep scripts as formatters over service results**

```python
problems = lint_root(root)
if problems:
    print(f"LLM Wiki lint: FAIL ({len(problems)} issue(s))")
    for problem in problems:
        print(f"- {problem.path}: {problem.message}")
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_linting.py tests/test_references.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "refactor: extract linting and references services"`

### Task 6: Add Ingest Cache and Planner

**Files:**
- Create: `llm_wiki_maintainer/ingest/cache.py`
- Create: `llm_wiki_maintainer/ingest/planner.py`
- Modify: `scripts/suggest_target_pages.py`
- Create: `tests/test_ingest_cache.py`
- Create: `tests/test_ingest_planner.py`

- [ ] **Step 1: Write failing tests for source hashing and changed-source detection**

```python
from llm_wiki_maintainer.ingest.cache import SourceManifest


def test_manifest_marks_source_changed_on_first_seen(tmp_path):
    raw = tmp_path / "a.md"
    raw.write_text("hello", encoding="utf-8")
    manifest = SourceManifest.empty()
    assert manifest.has_changed(raw) is True
```

```python
from llm_wiki_maintainer.ingest.planner import suggest_target_pages


def test_suggest_target_pages_returns_ranked_candidates(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    ranked = suggest_target_pages(raw, wiki_root)
    assert isinstance(ranked, list)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_ingest_cache.py tests/test_ingest_planner.py -q`  
Expected: FAIL because modules do not exist.

- [ ] **Step 3: Implement manifest storage and planner**

```python
import hashlib
from dataclasses import dataclass, field


@dataclass
class SourceManifest:
    hashes: dict[str, str] = field(default_factory=dict)

    def has_changed(self, path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        previous = self.hashes.get(str(path))
        return previous != digest
```

```python
def suggest_target_pages(raw_file, root):
    # keep current lexical heuristic but return structured candidate objects
    ...
```

- [ ] **Step 4: Add a persisted manifest path**

```python
MANIFEST_PATH = ".llm-wiki/ingest-manifest.yaml"
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_ingest_cache.py tests/test_ingest_planner.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add ingest manifest and planner"`

## Stage B: Runtime Capabilities

### Task 7: Introduce Two-Step Ingest Artifacts and Validation

**Files:**
- Create: `llm_wiki_maintainer/ingest/analysis.py`
- Create: `llm_wiki_maintainer/ingest/generation.py`
- Create: `tests/test_ingest_planner.py`
- Modify: `SKILL.md`

- [ ] **Step 1: Write failing tests for analysis and generation artifact validation**

```python
from llm_wiki_maintainer.ingest.analysis import AnalysisArtifact


def test_analysis_artifact_requires_source_and_claims():
    artifact = AnalysisArtifact(
        raw_path="raw/sources/example-raw.md",
        key_claims=["a"],
        target_pages=["wiki/overview"],
    )
    assert artifact.raw_path.endswith(".md")
```

```python
from llm_wiki_maintainer.ingest.generation import GenerationArtifact


def test_generation_artifact_tracks_outputs():
    artifact = GenerationArtifact(outputs={"wiki/overview.md": "# Overview"})
    assert "wiki/overview.md" in artifact.outputs
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_ingest_planner.py -q`  
Expected: FAIL because artifact classes do not exist.

- [ ] **Step 3: Implement artifact schemas and validation**

```python
from dataclasses import dataclass, field


@dataclass
class AnalysisArtifact:
    raw_path: str
    key_claims: list[str]
    target_pages: list[str]
    tensions: list[str] = field(default_factory=list)
```

```python
@dataclass
class GenerationArtifact:
    outputs: dict[str, str]
    review_items: list[dict] = field(default_factory=list)
```

- [ ] **Step 4: Update `SKILL.md` to describe new machine-backed ingest contract**

```md
- Store ingest analysis artifacts under `.llm-wiki/analysis/`.
- Store generation artifacts under `.llm-wiki/generation/`.
- Validate artifacts before applying file writes.
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_ingest_planner.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add two-step ingest artifact contracts"`

### Task 8: Add Query Engine with Lexical Retrieval and Context Assembly

**Files:**
- Create: `llm_wiki_maintainer/query/tokenize.py`
- Create: `llm_wiki_maintainer/query/retrieve.py`
- Create: `tests/test_query_retrieve.py`
- Modify: `SKILL.md`

- [ ] **Step 1: Write failing tests for English/Chinese tokenization and ranking**

```python
from llm_wiki_maintainer.query.tokenize import tokenize_query


def test_tokenize_query_supports_english_words():
    assert "strategy" in tokenize_query("strategy memo")


def test_tokenize_query_supports_chinese_bigrams():
    tokens = tokenize_query("知识图谱")
    assert any(len(token) >= 2 for token in tokens)
```

```python
from llm_wiki_maintainer.query.retrieve import retrieve_context


def test_retrieve_context_returns_ranked_pages(wiki_root):
    result = retrieve_context("example", wiki_root, limit=5)
    assert result.pages
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_query_retrieve.py -q`  
Expected: FAIL because query engine does not exist.

- [ ] **Step 3: Implement tokenization and retrieval**

```python
import re


def tokenize_query(text: str) -> list[str]:
    ascii_tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]{1,}", text.lower())
    cjk = [text[i:i+2] for i in range(len(text) - 1) if "\u4e00" <= text[i] <= "\u9fff"]
    return ascii_tokens + cjk
```

```python
def retrieve_context(query, root, limit=8):
    # score compiled pages by title hits, body hits, and source overlap
    ...
```

- [ ] **Step 4: Add a documented query protocol to the skill**

```md
When answering from llm-wiki, use the retrieval engine to rank pages before reading raw.
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_query_retrieve.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add lexical query retrieval engine"`

### Task 9: Build Graph Extraction and Insight Heuristics

**Files:**
- Create: `llm_wiki_maintainer/graph/build.py`
- Create: `llm_wiki_maintainer/graph/insights.py`
- Create: `tests/test_graph_build.py`

- [ ] **Step 1: Write failing tests for link graph and isolated-page detection**

```python
from llm_wiki_maintainer.graph.build import build_graph


def test_build_graph_extracts_page_and_source_edges(wiki_root):
    graph = build_graph(wiki_root)
    assert graph.nodes
```

```python
from llm_wiki_maintainer.graph.insights import find_isolated_pages


def test_find_isolated_pages_returns_list(wiki_root):
    graph = build_graph(wiki_root)
    assert isinstance(find_isolated_pages(graph), list)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_graph_build.py -q`  
Expected: FAIL because graph modules do not exist.

- [ ] **Step 3: Implement graph extraction**

```python
from dataclasses import dataclass, field


@dataclass
class WikiGraph:
    nodes: dict[str, dict] = field(default_factory=dict)
    edges: dict[tuple[str, str], float] = field(default_factory=dict)
```

```python
def build_graph(root):
    # nodes from compiled pages and source cards
    # edges from wikilinks and shared sources
    ...
```

- [ ] **Step 4: Implement first insight heuristics**

```python
def find_isolated_pages(graph):
    return [node for node, meta in graph.nodes.items() if meta.get("degree", 0) <= 1]
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_graph_build.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add wiki graph extraction and insight heuristics"`

### Task 10: Add Review Queue and Research Task Schema

**Files:**
- Create: `llm_wiki_maintainer/review.py`
- Create: `llm_wiki_maintainer/research.py`
- Create: `tests/test_review.py`
- Modify: `SKILL.md`

- [ ] **Step 1: Write failing tests for review-item state transitions**

```python
from llm_wiki_maintainer.review import ReviewItem


def test_review_item_transitions_to_approved():
    item = ReviewItem(id="rv-1", title="Need page", action="create_page", status="pending")
    approved = item.approve()
    assert approved.status == "approved"
```

```python
from llm_wiki_maintainer.research import ResearchTask


def test_research_task_tracks_queries():
    task = ResearchTask(topic="market map", queries=["market map 2026"])
    assert task.queries == ["market map 2026"]
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_review.py -q`  
Expected: FAIL because review and research models do not exist.

- [ ] **Step 3: Implement review and research schemas**

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class ReviewItem:
    id: str
    title: str
    action: str
    status: str

    def approve(self):
        return replace(self, status="approved")
```

```python
@dataclass
class ResearchTask:
    topic: str
    queries: list[str]
    status: str = "pending"
```

- [ ] **Step 4: Document review/research responsibilities**

```md
- Review items are the required bridge between ingest uncertainty and human judgment.
- Research tasks are queued only after review approval or explicit user request.
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_review.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add review and research task models"`

### Task 11: Add Source Lifecycle Reconciliation

**Files:**
- Create: `llm_wiki_maintainer/lifecycle.py`
- Create: `tests/test_lifecycle.py`
- Modify: `SKILL.md`

- [ ] **Step 1: Write failing tests for source deletion impact analysis**

```python
from llm_wiki_maintainer.lifecycle import analyze_source_removal


def test_analyze_source_removal_reports_dependent_pages(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    result = analyze_source_removal(wiki_root, raw)
    assert isinstance(result.pages_to_update, list)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_lifecycle.py -q`  
Expected: FAIL because lifecycle module does not exist.

- [ ] **Step 3: Implement dependency-aware source removal analysis**

```python
from dataclasses import dataclass, field


@dataclass
class SourceRemovalImpact:
    source_cards_to_delete: list[str] = field(default_factory=list)
    pages_to_update: list[str] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)
```

```python
def analyze_source_removal(root, raw_path):
    # inspect source cards, compiled pages, index links, and outgoing wikilinks
    ...
```

- [ ] **Step 4: Document lifecycle rules**

```md
- Source deletion must first run impact analysis.
- Shared pages should drop the removed source from `sources:` before deletion is considered.
```

- [ ] **Step 5: Re-run tests**

Run: `pytest tests/test_lifecycle.py -q`  
Expected: PASS

- [ ] **Step 6: Checkpoint**

If in git: `git commit -m "feat: add source lifecycle reconciliation analysis"`

### Task 12: End-to-End Verification and Documentation Pass

**Files:**
- Modify: `SKILL.md`
- Modify: `references/templates.md`
- Create: `README.md`
- Modify: `scripts/*.py`

- [ ] **Step 1: Add repository-level README explaining backend/runtime split**

```md
# llm-wiki-maintainer

This repository contains the backend and operator skill for maintaining an LLM Wiki knowledge base.

## Stage A
- Robust parsing
- Safe scaffolding
- Shared lint/reference services

## Stage B
- Two-step ingest artifacts
- Query retrieval
- Graph insights
- Review and lifecycle services
```

- [ ] **Step 2: Align templates and skill instructions with implemented backend modules**

```md
Run `pytest tests -q` before claiming backend health.
Run `python3 scripts/lint_llm_wiki.py <root>` for wiki structural verification.
```

- [ ] **Step 3: Run the full verification suite**

Run: `PYTHONPYCACHEPREFIX=/tmp/pycache pytest tests -q`  
Expected: PASS

Run: `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile scripts/*.py llm_wiki_maintainer/**/*.py`  
Expected: PASS

- [ ] **Step 4: Run a fixture lint smoke test**

Run: `python3 scripts/lint_llm_wiki.py tests/fixtures/wiki_minimal`  
Expected: PASS

- [ ] **Step 5: Final checkpoint**

If in git: `git commit -m "docs: finalize backend roadmap and verification workflow"`

## Program Milestones

### Milestone A1: Reliable Skill Backend
- Tasks 1-5 complete
- Outcome: current scripts are no longer isolated regex utilities; they share parsing, IO, and lint services.

### Milestone A2: Ingest Foundations
- Task 6 complete
- Outcome: changed-source detection and structured ingest planning exist.

### Milestone B1: Runtime Query + Ingest Contracts
- Tasks 7-8 complete
- Outcome: two-step ingest artifacts and lexical query retrieval exist.

### Milestone B2: Graph + Review + Research Foundations
- Tasks 9-10 complete
- Outcome: graph analysis and human-in-the-loop governance exist as backend modules.

### Milestone B3: Lifecycle Closure
- Tasks 11-12 complete
- Outcome: deletion impact analysis, end-to-end verification, and backend/runtime documentation are complete.

## Scope Guardrails

- Do not build UI-specific concerns in this repository yet.
- Do not add vector search before lexical retrieval, graph extraction, and artifact persistence are stable.
- Do not add live web-search providers before the review queue and research task schema exist.
- Prefer backend contracts and deterministic tests over LLM-coupled behavior in the first two milestones.

## Spec Coverage Check

- Strong backend layer: covered by Tasks 1-6.
- Two-step ingest: covered by Task 7.
- Query engine: covered by Task 8.
- Graph engine: covered by Task 9.
- Review and research loop: covered by Task 10.
- Source lifecycle management: covered by Task 11.
- Docs and verification closure: covered by Task 12.

