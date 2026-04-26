# llm-wiki-maintainer

This repository contains the Python backend and command-line runtime for Aristotle's `llm-wiki` system.

The split is intentionally simple:

- `llm_wiki_maintainer/` is the reusable backend. It holds the parsing, planning, linting, tracing, and helper logic.
- `scripts/` is the runtime layer. Each script is a thin CLI wrapper around backend functions and should only handle argument parsing, root resolution, and human-readable output.

The code is designed around the `llm-wiki` vault layout:

- `raw/` is the source surface.
- `wiki/` is the compiled knowledge surface.
- `wiki/sources/` is the navigation-only source-card surface.

In this workspace, the vault path now lives under `Glaucon's Vault`, not `Glaucon Vault`.

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

## Runtime entrypoints

The shipped scripts are the supported CLI entrypoints:

- `python3 scripts/create_source_card.py <raw-file> [llm-wiki-root]`
- `python3 scripts/suggest_target_pages.py <raw-file> [llm-wiki-root]`
- `python3 scripts/lint_llm_wiki.py [llm-wiki-root]`
- `python3 scripts/update_used_by.py [llm-wiki-root]`
- `python3 scripts/create_ingest_report.py <title> [llm-wiki-root]`
- `python3 scripts/create_audit_report.py <title> [llm-wiki-root]`

When a root argument is omitted, the runtime prefers the current working directory if it already looks like an `llm-wiki` root. Otherwise, scripts either derive the root from the raw-file path where that is reliable or fail with a clear explicit-root error.

## Practical use

The backend is meant to stay importable from tests and other tooling. The runtime wrappers are intentionally thin so the same logic can be reused from Python code or from shell commands without duplicating behavior.
