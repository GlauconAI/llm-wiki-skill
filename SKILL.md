---
name: llm-wiki-maintainer
description: Use when working on Aristotle's llm-wiki knowledge system: ingesting raw materials, creating or updating source cards, compiling or rewriting wiki pages, maintaining direct raw pointers, auditing traceability, fixing index structure, or linting the raw/wiki/wiki-sources three-layer model.
---

# LLM Wiki Maintainer

Maintain `/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki` as a strict three-layer system:

- `raw/` = only source of truth
- `wiki/` = directly usable compiled knowledge
- `wiki/sources/` = source-card navigation layer only

## Required reads

Before touching llm-wiki:
1. Read `/Users/glaucon/Obsidian/Glaucon Vault/README.md`
2. Read `/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki/AGENTS.md`
3. Read `/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki/index.md`

Read `references/templates.md` when creating or rewriting pages.
Run `python3 scripts/lint_llm_wiki.py` after structural edits or before claiming the wiki is healthy.

## Operating rules

- Never treat `wiki/sources/` as the final source.
- Every important conclusion in `wiki/` must point directly to `raw/`.
- Important claims should be supported twice when practical:
  1. locally, near the claim itself with an inline raw pointer; and
  2. globally, in `## Raw Source Pointers` for page-level traceability.
- Compress wording, not information.
- Do not drop steps, constraints, exceptions, numbers, dates, or definitions when they matter.
- Make wiki pages usable for normal questions without forcing the user back to raw every time.
- For high-stakes or uncertain claims, always trace back to raw.
- Use Obsidian-clickable wikilinks for internal vault paths; do not leave raw pointers as plain code-formatted text paths.
- Source cards are navigation-only. If a page starts teaching the topic instead of routing to evidence, it is in the wrong layer.
- Avoid source laundering: do not cite a source card as if it were evidence for a claim. Source cards route; raw proves.

## Answer-mode protocol

When an agent answers using llm-wiki:
1. Read `index.md` first to locate the right pages.
2. Read the relevant compiled pages in `wiki/`.
3. Answer from `wiki/` when the page is sufficient, specific enough, and not high-risk.
4. Return to `raw/` when any of the following is true:
   - the wiki page is thin, incomplete, or outdated
   - the question is high-risk or precision-sensitive
   - the page itself marks uncertainty or conflict
   - the user asks for verification, source checking, wording accuracy, or exact numbers
   - a key claim lacks direct raw support
5. If raw and wiki diverge, report the divergence explicitly and prefer raw for factual grounding.

## Task modes

### 1. Ingest mode
Use when new raw material arrives.

1. Inspect the raw file.
2. Create or update the matching source card in `wiki/sources/`.
3. Use `python3 scripts/suggest_target_pages.py <raw-file>` to identify likely affected compiled pages.
4. Update affected concept/entity/topic/overview pages in `wiki/`.
5. Add direct `Raw Source Pointers` to the compiled pages.
6. Add inline claim-level raw pointers near important claims whenever practical.
7. Record an ingest report with a `Not Absorbed` section listing what stayed out of the wiki and why.
8. Update `index.md` if navigation changed.
9. Append to `log.md` if the change is durable and notable.
10. Run `python3 scripts/update_used_by.py` and `python3 scripts/lint_llm_wiki.py`.

Use helpers when useful:
- `python3 scripts/create_source_card.py <raw-file>`
- `python3 scripts/create_ingest_report.py "<title>"`

### 2. Rewrite / compile mode
Use when a wiki page is too thin, too lossy, or not traceable.

1. Read the relevant raw files first.
2. Rewrite the compiled page using the template from `references/templates.md`.
3. Preserve decision-relevant details.
4. Add direct raw pointers at page bottom.
5. Add inline raw pointers near the strongest or riskiest claims.
6. Link related wiki pages.
7. Re-run lint.

### 3. Source-card mode
Use when touching `wiki/sources/`.

A source card may contain only:
- `Location`
- `Type`
- `Coverage`
- `Used by`
- `Key Sections`
- `Notes`

Do not turn source cards into summary pages.
Run `python3 scripts/update_used_by.py` after major rewrites if you want `Used by` to match actual `sources:` usage automatically.

### 4. Lint / audit mode
Use when checking system health.

Check for:
- missing raw pointers
- missing inline claim-level raw support for important claims
- thin wiki pages or template-only pages
- source cards that became summaries
- broken or non-clickable internal links
- index drift
- raw files not yet compiled
- `Used by` drift versus actual references
- compiled pages missing from `index.md`
- claims too strong for the evidence quality
- source laundering or summary-as-source behavior
- whether wiki pages are sufficient to answer common questions without unnecessary raw reopening

When useful, produce an audit report under `wiki/reports/`.
Use `python3 scripts/create_audit_report.py "<title>"` for a fast audit-report scaffold.
Run `python3 scripts/lint_llm_wiki.py` for a repeatable structural check.

## Success standard

A good llm-wiki change leaves the system in this state:
- normal use can start from `index.md` and `wiki/`
- key conclusions trace directly to `raw/`
- important claims are locally supportable, not only globally sourced at page bottom
- source cards help navigation but do not replace evidence
- the knowledge layer becomes more usable, not thinner
- ingest work explicitly records what was not absorbed and why
