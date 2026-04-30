---
title: llm-wiki-maintainer 架构说明
date: 2026-04-25
status: active
language: zh-CN
---

# llm-wiki-maintainer 架构说明

## 1. 架构目标

本仓库的架构目标是：

- 把 `LLM Wiki` 的规则沉淀成可复用 backend
- 把脚本变成薄 wrapper，而不是逻辑主载体
- 让 skill 文档、backend 和测试形成闭环

## 2. 分层

### 2.1 知识层

- `raw/`
- `wiki/`
- `wiki/sources/`

### 2.2 代码层

- `llm_wiki_maintainer/`
- `scripts/`
- `tests/`

### 2.3 文档层

- `README.md`
- `SKILL.md`
- `references/templates.md`
- `docs/superpowers/plans/*.md`

## 3. Backend 包结构

### Foundation

- `frontmatter.py`
- `models.py`
- `config.py`
- `wiki_io.py`

### Wiki Maintenance

- `source_cards.py`
- `references.py`
- `linting.py`
- `links.py`

### Ingest

- `ingest/cache.py`
- `ingest/planner.py`
- `ingest/analysis.py`
- `ingest/generation.py`

### Query

- `query/tokenize.py`
- `query/retrieve.py`

### Graph

- `graph/build.py`
- `graph/insights.py`

### Governance

- `review.py`
- `research.py`

### Lifecycle

- `lifecycle.py`

## 4. 脚本层原则

脚本层的原则是：

1. 参数解析在脚本里
2. 业务逻辑在 backend 里
3. root 解析尽量从 cwd 或显式参数得出
4. 避免硬编码 vault 名称

## 5. 当前边界

当前架构已经覆盖：

- 维护层
- ingest 规划层
- retrieval backend
- graph seed layer
- schema 层 review/research
- lifecycle analysis

当前还没有覆盖：

- persisted runtime
- queue engine
- UI / app shell

## 6. 设计原则

1. compiled-first, raw-backstop
2. source traceability
3. no source laundering
4. backend-first
5. tests before trust
