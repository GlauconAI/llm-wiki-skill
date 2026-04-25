# LLM Wiki Templates

## Source card template

```md
---
type: source
id: SRC-XXXX
title: <source title>
agent: aristotle
subagent: source-ingest
cover:
status: active
claim_type: fact
confidence: medium
source_kind: <article / internal-note / note>
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [source, ...]
sources: [SRC-XXXX]
---
# Source: <title>

## Location
[[raw/sources/<file-stem>|/raw/sources/<file-name>.md]]

## Type
<md / pdf / transcript / web / note>

## Coverage
- topic A
- topic B

## Used by
- [[wiki/topics/example-page]]

## Key Sections
- section or page range
- section or page range

## Notes
- Navigation-only notes. No detailed summary here.
```

## Compiled wiki page template

```md
# <page title>

## TL;DR
一句话结论

## Core Knowledge
- 核心知识 [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)
- 第二条核心知识 [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)

## Decision-Relevant Details
- 影响判断的关键细节 [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)

## Procedures / Steps
1. 如适用，写步骤

## Constraints / Exceptions
- 限制、边界、例外 [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)

## Numbers / Facts
- 重要数字、日期、参数、定义 [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)

## Uncertainty / Conflicts
- 不确定性或冲突 [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)

## Related Pages
- [[wiki/...]]

## Raw Source Pointers
- [[raw/sources/<file-stem>|/raw/sources/<file-name>.md]] (section: ...)
```

## Claim-level raw pointer rule

For important claims, do not rely only on the page-bottom `## Raw Source Pointers` list.
Add inline raw pointers near the claim itself when practical, especially in:

- `## Core Knowledge`
- `## Decision-Relevant Details`
- `## Constraints / Exceptions`
- `## Numbers / Facts`
- `## Uncertainty / Conflicts`

Good:

```md
- FCN 常带 autocall / knock-out 机制 [[raw/sources/SRC-0021-dbs-eln-fcn-structured-notes|/raw/sources/SRC-0021-dbs-eln-fcn-structured-notes.md]] (section: FCN 的经济实质)
```

Weak:

```md
- FCN 常带 autocall / knock-out 机制

## Raw Source Pointers
- [[raw/sources/SRC-0021-dbs-eln-fcn-structured-notes|/raw/sources/SRC-0021-dbs-eln-fcn-structured-notes.md]]
```

## Ingest report template

```md
---
type: report
id: ING-YYYYMMDD-<slug>
title: YYYY-MM-DD <ingest title>
agent: aristotle
subagent: curator
cover:
status: active
claim_type: synthesis
confidence: medium
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [report, ingest, llm-wiki]
sources: [SRC-XXXX]
---

# YYYY-MM-DD <ingest title>

## Raw Reviewed
- [[raw/sources/SRC-XXXX-...|/raw/sources/SRC-XXXX-....md]]

## Pages Added or Updated
- [[wiki/...]]

## Claims Absorbed
- claim A -> [[wiki/...]]
- claim B -> [[wiki/...]]

## Not Absorbed
- item not absorbed
- why it was excluded: low confidence / off-scope / duplicate / too weakly evidenced / waiting for more raw

## Follow-up
- additional raw needed
- page still thin
- unresolved conflicts
```

## Audit report template

```md
---
type: report
id: RPT-YYYYMMDD-<slug>
title: YYYY-MM-DD <audit title>
agent: aristotle
subagent: librarian
cover:
status: active
claim_type: synthesis
confidence: medium
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [report, audit, llm-wiki]
sources: []
---

# YYYY-MM-DD <audit title>

## Scope
- what was audited

## Structural Health
- broken links
- missing sections
- thin pages

## Knowledge Fidelity
- can common questions be answered from wiki alone?
- do raw pointers actually support page conclusions?
- any source laundering?
- any summary-as-source behavior?

## Raw Pointer Coverage
- what now points directly to raw
- what still lacks direct raw support

## Remaining Gaps
- uncompiled raw
- weak evidence areas
- unresolved conflicts

## Verdict
- does the system meet “日常使用看 wiki，必要时回 raw”?
```

## Answer-mode protocol

When using llm-wiki to answer:

1. Read `index.md` first.
2. Read the most relevant compiled page(s) in `wiki/`.
3. Answer from `wiki/` if the page is sufficient and low-risk.
4. Return to `raw/` if the wiki is thin, uncertain, high-risk, contradictory, or the user asks for checking.
5. If wiki and raw differ, say so explicitly and ground factual claims in raw.

## Lint checklist

- `wiki/sources/` 是否只做导航？
- source card 是否过长、过实、过像 summary？
- `wiki/` 页面是否过薄或只剩模板标题？
- 关键结论是否直指 `raw/`？
- 关键 claim 是否有就地 raw pointer？
- raw pointer 是否是可点击的 wikilink？
- `index.md` 是否能回答“读什么、什么时候回 raw、哪里还空白”？
- audit 是否检查 knowledge fidelity，而不仅是结构？
- ingest 报告是否写出 `Not Absorbed`？

## Scripted lint

Run:

```bash
python3 scripts/lint_llm_wiki.py
```

Optional custom root:

```bash
python3 scripts/lint_llm_wiki.py /path/to/llm-wiki
```

## Source-card helper

Create a source-card skeleton from a raw file:

```bash
python3 scripts/create_source_card.py /path/to/llm-wiki/raw/sources/SRC-XXXX-something.md
```

Optional custom llm-wiki root:

```bash
python3 scripts/create_source_card.py /path/to/raw-file /path/to/llm-wiki
```

## Used-by sync helper

Sync source-card `Used by` sections from actual compiled-page `sources:` frontmatter:

```bash
python3 scripts/update_used_by.py
```

## Audit-report scaffold

Create a new audit report scaffold:

```bash
python3 scripts/create_audit_report.py "LLM Wiki Spot Audit"
```

## Ingest-report scaffold

Create a new ingest report scaffold:

```bash
python3 scripts/create_ingest_report.py "DBS ELN FCN Ingest"
```

## Candidate-page helper

Suggest likely compiled pages affected by a raw file:

```bash
python3 scripts/suggest_target_pages.py /path/to/raw-file
```
