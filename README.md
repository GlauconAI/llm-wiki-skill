# llm-wiki-maintainer

This repository contains the Python backend and command-line runtime for Aristotle's `llm-wiki` system.

## Project Baseline

This repository should now be read as a `backend + persisted runtime core + operator CLI` project, not as a loose collection of helper scripts.

The current execution baseline is:

- [docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md)

That document fixes:

- the final project position
- the current scope boundaries
- the official milestone order
- the rule that runtime work comes before UI or product shell work

If future development needs a single source of truth for "what are we building next?", use that file first.

The split is intentionally simple:

- `llm_wiki_maintainer/` is the reusable backend. It holds the parsing, planning, linting, tracing, and helper logic.
- `scripts/` is the runtime layer. Each script is a thin CLI wrapper around backend functions and should only handle argument parsing, root resolution, and human-readable output.

The code is designed around the `llm-wiki` vault layout:

- `raw/` is the source surface.
- `wiki/` is the compiled knowledge surface.
- `wiki/sources/` is the navigation-only source-card surface.

The runtime now also assumes a project-local state surface under:

- `.llm-wiki/state/` for persisted queue/state files
- `.llm-wiki/analysis/` for analysis artifacts
- `.llm-wiki/generation/` for generation artifacts

In this workspace, the vault path lives under `Glaucon's Vault`.

## Documentation Map

The repository has a few documents with different responsibilities. They should not be treated as interchangeable.

- [README.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/README.md) is the first-entry technical overview for maintainers. It explains repo structure, runtime entrypoints, and where to look next.
- [SKILL.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/SKILL.md) defines operator rules for working on an actual `llm-wiki` root. It is workflow guidance, not the project roadmap.
- [docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md) is the current roadmap baseline. Use it for final positioning, scope, and milestone order.
- [docs/superpowers/plans/2026-04-25-llm-wiki-project-dossier-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-project-dossier-zh.md) is the broadest project record. Use it for historical context, completed milestones, and gap analysis.
- [docs/superpowers/plans/2026-04-25-llm-wiki-future-roadmap-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-future-roadmap-zh.md) is now a summary roadmap. It should be read through the lens of the final plan above.
- [docs/superpowers/plans/2026-04-25-llm-wiki-stage2-runtime-plan.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-stage2-runtime-plan.md) and [docs/superpowers/plans/2026-04-24-llm-wiki-backend-roadmap.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-24-llm-wiki-backend-roadmap.md) are historical implementation plans. Keep using them as execution reference, but not as the top-level product decision source.
- [docs/superpowers/plans/INDEX.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/INDEX.md) is the navigation page for the planning docs directory.
- [references/templates.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/references/templates.md) holds the page templates and output format expectations used during wiki work.

## Recommended Reading Order

If someone needs to resume development later, this is the shortest reliable path:

1. Read [README.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/README.md).
2. Read [docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md).
3. Read [docs/superpowers/plans/2026-04-25-llm-wiki-project-dossier-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-project-dossier-zh.md).
4. Read [docs/superpowers/plans/2026-04-25-llm-wiki-architecture-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-architecture-zh.md) and [docs/superpowers/plans/2026-04-25-llm-wiki-capabilities-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-capabilities-zh.md).
5. Only then drop into older roadmap files if implementation detail is needed.

The original six milestone baseline is now complete in this repository. Later non-desktop alignment work extends it with:

- research execution that writes raw research notes and re-enters ingest
- recursive folder import with batch enqueue
- an optional vector search seam on top of the deterministic query runtime
- richer graph diagnostics such as cohesion scoring and knowledge-gap detection

The current continuation point after that baseline is skill productization: explicit workflow routing plus durable `status`, `digest`, `delete`, and `crystallize` operator flows.

## Implemented backend modules

The backend currently includes:

- `llm_wiki_maintainer.config` for runtime root/date configuration.
- `llm_wiki_maintainer.frontmatter` for loading and dumping markdown frontmatter.
- `llm_wiki_maintainer.wiki_io` for safe text reads and writes.
- `llm_wiki_maintainer.links` for wikilink parsing and target normalization.
- `llm_wiki_maintainer.source_cards` for source-card generation and duplicate detection.
- `llm_wiki_maintainer.references` for `Used by` synchronization and source reference checks.
- `llm_wiki_maintainer.linting` for structural validation of the vault.
- `llm_wiki_maintainer.lifecycle` for source-removal impact analysis.
- `llm_wiki_maintainer.ingest.planner` for affected-page suggestion during ingest.
- `llm_wiki_maintainer.ingest.analysis` and `llm_wiki_maintainer.ingest.generation` for ingest artifact models.
- `llm_wiki_maintainer.query.tokenize` and `llm_wiki_maintainer.query.retrieve` for lexical retrieval helpers.
- `llm_wiki_maintainer.graph.build` and `llm_wiki_maintainer.graph.insights` for graph extraction and analysis.
- `llm_wiki_maintainer.review` for review-item state handling.
- `llm_wiki_maintainer.research` for research-task modeling.
- `llm_wiki_maintainer.importer` for recursive folder import into the raw surface.
- `llm_wiki_maintainer.source_adapters` for source registry, adapter status classification, and unified import/research adapter wrappers.
- `llm_wiki_maintainer.registry` for multi-wiki root registration, active-root management, and shared root resolution.

## Runtime Surface

The project now has a shared runtime surface intended to be reused by both CLI entrypoints and any future UI or application shell.

- `llm_wiki_maintainer.project.ProjectLayout` defines the canonical runtime directories for a project root.
- `llm_wiki_maintainer.runtime.api.LlmWikiRuntime` is the top-level runtime facade.
- `llm_wiki_maintainer.runtime.ingest_queue.IngestQueue` owns persisted ingest jobs and queue execution.
- `llm_wiki_maintainer.review_queue.ReviewQueueStore` owns persisted review items.
- `llm_wiki_maintainer.research_queue.ResearchQueueStore` owns persisted research tasks.
- `llm_wiki_maintainer.query.runtime.query_runtime` exposes deterministic retrieval + bounded context assembly.
- `llm_wiki_maintainer.graph.relevance` and `llm_wiki_maintainer.graph.insights` expose explainable graph-derived helpers.
- `llm_wiki_maintainer.research_runtime` now supports executable research tasks that emit raw research notes and feed them back into ingest.
- `llm_wiki_maintainer.importer` now supports recursive folder import into `raw/imports/`.
- `llm_wiki_maintainer.source_adapters` now exposes the current adapter registry and normalized status codes for local files, folder imports, and research tasks.

If a future product layer needs to call into this repository, it should prefer `LlmWikiRuntime` and `ProjectLayout` instead of reaching directly into individual CLI scripts.

## Runtime entrypoints

The shipped scripts are the supported CLI entrypoints:

- `python3 scripts/create_source_card.py <raw-file> [llm-wiki-root]`
- `python3 scripts/suggest_target_pages.py <raw-file> [llm-wiki-root]`
- `python3 scripts/lint_llm_wiki.py [llm-wiki-root]`
- `python3 scripts/update_used_by.py [llm-wiki-root]`
- `python3 scripts/create_ingest_report.py <title> [llm-wiki-root]`
- `python3 scripts/create_audit_report.py <title> [llm-wiki-root]`
- `python3 scripts/run_ingest_queue.py <enqueue|run|status|retry|cancel> ...`
- `python3 scripts/review_queue.py <import|list|show|approve|reject> ...`
- `python3 scripts/query_context.py <query> <llm-wiki-root>`
- `python3 scripts/save_query.py <query> <llm-wiki-root> [title]`
- `python3 scripts/run_research_queue.py <run> <llm-wiki-root>`
- `python3 scripts/import_folder.py <source-folder> <llm-wiki-root>`
- `python3 scripts/source_adapters.py <llm-wiki-root> [--with-research-provider]`
- `python3 scripts/wiki_registry.py <add|activate|list|show-active> ...`
- `python3 scripts/wiki_status.py <llm-wiki-root>`
- `python3 scripts/create_digest.py <query> <llm-wiki-root> [title]`
- `python3 scripts/delete_source.py <raw-file> <llm-wiki-root> [--apply]`
- `python3 scripts/crystallize_note.py <title> <summary> <llm-wiki-root> [source-id ...]`

When a root argument is omitted, the shared resolver now uses this order:

1. explicit root argument
2. current working directory if it already looks like an `llm-wiki` root
3. the active root from the multi-wiki registry

## Productized workflows

The runtime is no longer just a set of helper commands. At the skill layer, the intended top-level workflows are:

- `ingest` and `batch-ingest` for new source intake
- `query` for transient bounded context retrieval
- `save-query` for persisting a bounded query context under `wiki/queries/`
- `digest` for persisted query-driven synthesis under `wiki/digests/`
- `status` for project, queue, and governance summary
- `delete` for source-removal analysis and explicit apply
- `crystallize` for turning temporary synthesis into durable wiki pages
- `lint` for structural health checks

## Source adapter layer

The current source adapter layer does not try to scrape the web yet. It normalizes the source types that already exist in this repository:

- `local_file` for direct files under `raw/sources/`
- `folder_import` for recursive local imports into `raw/imports/`
- `research_task` for queued research that materializes into `raw/research/`

Adapter health is normalized into a small shared set of status codes:

- `ready`
- `not_installed`
- `env_unavailable`
- `runtime_failed`
- `unsupported`
- `empty_result`

That gives future URL or provider-backed adapters a place to plug in without changing the surrounding runtime contracts.

## Query persistence

The repository now has three distinct query-adjacent outputs:

- `query` is transient. It retrieves pages and assembles bounded context for the current turn only.
- `save-query` persists that bounded context into `wiki/queries/` without adding graph synthesis or broader interpretation.
- `digest` is the heavier persisted artifact. It includes the query context plus graph-derived synthesis and should be used for more durable knowledge work.

## Multi-wiki registry

The repository now supports a lightweight multi-wiki registry so future work does not depend on one hard-coded vault path.

- The registry stores named wiki roots plus one active root.
- Runtime entrypoints can resolve a root from `cwd` or the active registry entry when no explicit root is passed.
- The default registry path is `~/.codex/memories/llm-wiki-roots.yaml`, and it can be overridden with `LLM_WIKI_REGISTRY_PATH`.

## Test fixtures

The repository now ships two distinct fixture vaults under `tests/fixtures/`:

- `wiki_minimal/` is intentionally imperfect and is used to exercise lint, graph, and edge-case behavior.
- `wiki_healthy/` is the official lint-clean sample root and can be used as a known-good acceptance baseline.

## Practical use

The backend is meant to stay importable from tests and other tooling. The runtime wrappers are intentionally thin so the same logic can be reused from Python code or from shell commands without duplicating behavior.
