---
title: llm-wiki Stage 2 Runtime Alignment Plan
date: 2026-04-25
status: proposed
owner: codex
source_of_truth: docs/superpowers/plans/2026-04-24-llm-wiki-backend-roadmap.md
comparison_target: https://github.com/nashsu/llm_wiki
---

# Stage 2 Runtime Alignment Plan

## Purpose

This plan defines the next execution phase after the backend foundation is in place.
The goal is to close the remaining gap between this repository and `nashsu/llm_wiki`
on runtime behavior, orchestration depth, and operator workflow, without jumping
straight into a full desktop product rewrite.

Current repo state:
- backend modules exist for parsing, source maintenance, ingest planning, query retrieval, graph extraction, review/research schemas, and lifecycle analysis
- CLI wrappers and operator docs are aligned with the backend
- tests are in place and the suite is currently green

Remaining gap versus `nashsu/llm_wiki` is concentrated in:
- runtime orchestration
- persistent queueing and recovery
- review/research execution loops
- deeper graph and retrieval intelligence
- product-facing state and UX

## Gap Summary Against `nashsu/llm_wiki`

### Already comparable

- Three-layer wiki model
- Source-traceable ingest discipline
- Lint / maintenance workflows
- Query backend seed capability
- First-pass graph extraction
- Source lifecycle analysis

### Still missing or significantly weaker

1. Persistent ingest runtime
- No durable ingest queue
- No retry/cancel/progress state model
- No crash recovery

2. Review system
- Schema exists, but no persisted queue, actions, filtering, or approval flow

3. Research system
- Schema exists, but no queued execution, no search orchestration, no ingest feedback loop

4. Query runtime
- Lexical retrieval exists, but no full answer assembly, no vector mode, no session persistence

5. Graph intelligence
- Graph extraction exists, but no relevance scoring model, no community detection, no graph-derived insight generation

6. Runtime state layer
- No project-level persisted queue/state store for ingest, review, research, and graph jobs

7. Product layer
- No application shell, panel state, settings UX, or activity UI

## Strategy

Do not try to catch up by building UI first.
Close the gap in this order:

1. Build minimal runtime orchestration on top of the current backend
2. Add persistent queue/state and human-in-the-loop execution models
3. Expand graph/query intelligence
4. Only then consider desktop/product packaging

This keeps the current repo useful as:
- an operator-facing skill
- a reusable backend library
- a future runtime core

## Phase A: Minimal Runtime

### Goal

Turn the current backend modules into a runnable system with explicit jobs,
persisted task state, and resumable ingest execution.

### Deliverables

1. Ingest job model
- file: `llm_wiki_maintainer/runtime/jobs.py`
- define `IngestJob`, `JobStatus`, `JobResult`

2. Project state storage
- file: `llm_wiki_maintainer/runtime/state.py`
- persist queue/job state under `.llm-wiki/state/`

3. Ingest queue
- file: `llm_wiki_maintainer/runtime/ingest_queue.py`
- enqueue, dequeue, retry, cancel, resume

4. Orchestration CLI
- file: `scripts/run_ingest_queue.py`
- minimal commands:
  - `enqueue`
  - `run`
  - `status`
  - `retry`

5. Tests
- files:
  - `tests/test_runtime_state.py`
  - `tests/test_ingest_queue.py`

### Acceptance

- jobs survive process restart
- failed jobs can be retried
- unchanged raw files are skipped using existing manifest/cache
- queue processes serially

### Verification

```bash
python3 -m pytest tests/test_runtime_state.py tests/test_ingest_queue.py -q
```

## Phase B: Review And Research Execution

### Goal

Turn `ReviewItem` and `ResearchTask` from schemas into executable, persisted workflows.

### Deliverables

1. Review queue persistence
- file: `llm_wiki_maintainer/review_queue.py`
- load/save/filter/update review items

2. Review actions
- file: `scripts/review_queue.py`
- commands:
  - `list`
  - `approve`
  - `reject`
  - `show`

3. Research queue persistence
- file: `llm_wiki_maintainer/research_queue.py`
- store research tasks and lifecycle state

4. Research handoff rules
- file: `llm_wiki_maintainer/research_runtime.py`
- only allow queueing after review approval or explicit override

5. Tests
- files:
  - `tests/test_review_queue.py`
  - `tests/test_research_queue.py`

### Acceptance

- review items can move through explicit status transitions
- research tasks can be queued and resumed
- queue invariants enforce the documented governance rules

### Verification

```bash
python3 -m pytest tests/test_review_queue.py tests/test_research_queue.py -q
```

## Phase C: Query Runtime Expansion

### Goal

Upgrade retrieval into a real query runtime that can assemble answer context
and support future vector retrieval.

### Deliverables

1. Query result model
- file: `llm_wiki_maintainer/query/models.py`

2. Answer-context assembler
- file: `llm_wiki_maintainer/query/assemble.py`
- ranked pages -> bounded context package

3. Query session runner
- file: `llm_wiki_maintainer/query/runtime.py`
- one entry point for retrieval + assembly

4. CLI
- file: `scripts/query_context.py`

5. Optional vector abstraction seam
- file: `llm_wiki_maintainer/query/vector.py`
- do not implement provider lock-in yet

6. Tests
- files:
  - `tests/test_query_assemble.py`
  - `tests/test_query_runtime.py`

### Acceptance

- query runtime returns ranked pages plus bounded context
- lexical path remains default and deterministic
- future vector mode can be attached without rewriting query callers

### Verification

```bash
python3 -m pytest tests/test_query_retrieve.py tests/test_query_assemble.py tests/test_query_runtime.py -q
```

## Phase D: Graph Intelligence

### Goal

Move from graph extraction to graph-derived reasoning.

### Deliverables

1. Relevance scoring
- file: `llm_wiki_maintainer/graph/relevance.py`
- initial signals:
  - direct wikilinks
  - shared sources
  - local structural proximity
  - type affinity

2. Community detection seam
- file: `llm_wiki_maintainer/graph/community.py`
- start with a minimal dependency-light implementation or placeholder adapter

3. Insights expansion
- file: `llm_wiki_maintainer/graph/insights.py`
- add:
  - bridge pages
  - dense clusters
  - orphaned source cards
  - suspicious isolates

4. Tests
- files:
  - `tests/test_graph_relevance.py`
  - `tests/test_graph_insights.py`

### Acceptance

- graph heuristics produce deterministic outputs on fixtures
- insights remain explainable, not opaque scores only

### Verification

```bash
python3 -m pytest tests/test_graph_build.py tests/test_graph_relevance.py tests/test_graph_insights.py -q
```

## Phase E: Lifecycle Engine Upgrade

### Goal

Move from impact analysis to guided remediation.

### Deliverables

1. Patch suggestion model
- file: `llm_wiki_maintainer/lifecycle_actions.py`

2. Delete/move/rename action planner
- file: `llm_wiki_maintainer/lifecycle_runtime.py`

3. CLI
- file: `scripts/analyze_source_removal.py`
- file: `scripts/plan_source_cleanup.py`

4. Tests
- files:
  - `tests/test_lifecycle_runtime.py`

### Acceptance

- source removal can emit proposed edits, not just impact lists
- rename/move paths are analyzed separately from deletion

### Verification

```bash
python3 -m pytest tests/test_lifecycle.py tests/test_lifecycle_runtime.py -q
```

## Phase F: Productization Readiness

### Goal

Prepare the backend to become the core of a desktop or service application.

### Deliverables

1. Project config model
- file: `llm_wiki_maintainer/project.py`

2. Settings/state schema
- file: `llm_wiki_maintainer/settings.py`

3. Runtime API facade
- file: `llm_wiki_maintainer/runtime/api.py`

4. Documentation
- `README.md`
- `SKILL.md`
- `references/templates.md`
- new `docs/architecture.md`

### Acceptance

- operator docs clearly separate:
  - backend library
  - CLI wrappers
  - future runtime/application layer

## Suggested Execution Order

1. Phase A: Minimal Runtime
2. Phase B: Review And Research Execution
3. Phase C: Query Runtime Expansion
4. Phase D: Graph Intelligence
5. Phase E: Lifecycle Engine Upgrade
6. Phase F: Productization Readiness

## Recommended First Milestone

If only one follow-up sprint is funded, do:

1. Phase A
2. Phase B
3. first half of Phase C

That would close the biggest remaining gap versus `nashsu/llm_wiki`:
the absence of a real runtime.

## Out Of Scope For This Stage

- Full desktop UI
- Web clipper
- Browser extension
- Production vector database integration
- Multi-project app shell
- Cloud sync

These are product-layer tasks and should sit on top of the runtime, not replace it.

## Final Success Criteria

This repo will be considered Stage 2 complete when:

- ingest, review, research, query, graph, and lifecycle all have persisted runtime entry points
- operator docs match actual execution paths
- the backend can be driven by CLI or future UI without duplicating logic
- the remaining gap to `nashsu/llm_wiki` is mostly UI/product depth, not runtime capability
