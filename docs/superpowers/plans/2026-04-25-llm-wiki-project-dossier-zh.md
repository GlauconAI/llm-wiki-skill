---
title: llm-wiki-maintainer 项目总档案
date: 2026-04-25
status: active
language: zh-CN
owner: codex
scope: project-record
---

# llm-wiki-maintainer 项目总档案

## 1. 文档目的

这份文档是 `llm-wiki-maintainer` 项目的中文主记录，用于集中保存以下信息：

- 项目的目标与定位
- 整体设计与架构边界
- 已完成的 Milestone 与实现清单
- 与竞品 `nashsu/llm_wiki` 的差距分析
- `SKILL.md` 的实际使用方式
- 已知遗留问题与风险
- 下一阶段规划
- 与路径、验证、工作区相关的操作约定

这份文档的目标不是替代代码、测试或 `SKILL.md`，而是给后续维护者、操作者、agent 和项目负责人提供一个单点可读的“项目全景视图”。

## 2. 项目定位

### 2.1 当前定位

`llm-wiki-maintainer` 当前已经不再只是一个“写给 agent 看的 skill 文档”，而是：

1. 一套面向 LLM Wiki 的操作规范
2. 一个可复用的 Python backend
3. 一组尽量薄的 CLI wrapper
4. 一个未来可继续长成完整 runtime 的基础仓库

### 2.2 它不是什么

当前它还不是：

- 完整桌面产品
- 全功能 query/research app
- 持久化任务调度系统
- 有完整 UI 的知识工作台
- `nashsu/llm_wiki` 的同级成品替代物

### 2.3 当前最准确的描述

当前最准确的描述是：

> 一个已经具备后端能力边界的 `LLM Wiki` 维护与运行基础设施仓库，重点在知识结构约束、source traceability、可测试的 backend 模块，以及向完整 runtime 演进的工程底座。

## 3. 项目目标

项目目标分两层：

### 3.1 近程目标

把“规则文档 + 脆弱脚本”升级成：

- 有明确包边界的 backend
- 可测试、可复用的模块
- 与 skill 规则一致的 CLI 行为
- 更稳健的 source / wiki / ingest / query / lifecycle 基础能力

### 3.2 远程目标

逐步缩小与 `nashsu/llm_wiki` 的差距，最终把本仓库推进成：

- 有 persisted runtime 的系统
- 有 review / research 执行层
- 有更完整 graph/query intelligence
- 可被 CLI 或未来 UI 共同驱动的核心引擎

## 4. 知识模型与设计原则

### 4.1 三层模型

仓库围绕三层结构组织：

1. `raw/`
- 原始资料层
- 保留接近 source 的原始内容

2. `wiki/`
- 编译知识层
- 面向回答、组织、聚合

3. `wiki/sources/`
- source card 层
- 只负责导航、映射、指向，不负责承载知识总结

### 4.2 核心原则

1. Source traceability
- 重要 claim 必须能回溯到 raw/source

2. No source laundering
- source card 不应变成“伪 summary 页面”

3. Compiled-first, raw-backstop
- 一般优先用 wiki 编译层回答
- 高风险或争议信息回 raw 核实

4. Skill rules should become code where practical
- 不能永远只靠操作者记住流程
- 应尽量把规则沉淀成 backend 与测试

5. CLI wrappers should stay thin
- 业务逻辑尽量放入 `llm_wiki_maintainer/`
- `scripts/*.py` 尽量只做参数处理和调用

## 5. 当前仓库架构

### 5.1 包结构

当前核心代码位于：

- `llm_wiki_maintainer/`

该包当前已经覆盖以下能力域：

- frontmatter
- models
- config
- wiki_io
- source_cards
- links
- references
- linting
- ingest
- query
- graph
- review
- research
- lifecycle

### 5.2 脚本层

当前脚本层位于：

- `scripts/`

它们主要是 backend 的入口包装，而不是逻辑主载体。

### 5.3 文档层

当前主要文档包括：

- `SKILL.md`
- `README.md`
- `references/templates.md`
- `docs/superpowers/plans/*.md`

### 5.4 测试层

当前测试主要位于：

- `tests/`

并包含：

- fixture wiki
- 单元测试
- wrapper/harness 回归测试

## 6. 已完成的 Milestone

以下内容已经在本仓库落地，并经过多轮修复与回归验证。

### Milestone 1: Package Scaffold

已完成：

- `llm_wiki_maintainer/__init__.py`
- `tests/conftest.py`
- 最小 fixture wiki
- 基础 harness

目的：

- 让后续功能有统一包边界与测试基线

### Milestone 2: Frontmatter Layer

已完成：

- `llm_wiki_maintainer/frontmatter.py`
- `llm_wiki_maintainer/models.py`
- `tests/test_frontmatter.py`

能力：

- 解析/序列化 frontmatter
- 处理 malformed YAML、边界分隔符、CRLF、round-trip fidelity

### Milestone 3: Config / IO Layer

已完成：

- `llm_wiki_maintainer/config.py`
- `llm_wiki_maintainer/wiki_io.py`

能力：

- runtime config
- 日期/路径规范化
- 安全文件 IO

### Milestone 4: Source Card Backend

已完成：

- `llm_wiki_maintainer/source_cards.py`
- `scripts/create_source_card.py`
- 对应测试

能力：

- source card 生成
- 位置重复检测
- 路径规范化
- 安全 frontmatter 写出

### Milestone 5: References / Linting

已完成：

- `llm_wiki_maintainer/links.py`
- `llm_wiki_maintainer/references.py`
- `llm_wiki_maintainer/linting.py`
- `scripts/lint_llm_wiki.py`
- `scripts/update_used_by.py`

能力：

- `sources:` 解析与校验
- `Used by` 同步
- source-card id 完整性检查
- malformed 输入容错

### Milestone 6: Ingest Cache / Planner

已完成：

- `llm_wiki_maintainer/ingest/cache.py`
- `llm_wiki_maintainer/ingest/planner.py`
- `scripts/suggest_target_pages.py`

能力：

- ingest manifest
- source hash 变化检测
- target page lexical planning

### Milestone 7: Ingest Artifacts

已完成：

- `llm_wiki_maintainer/ingest/analysis.py`
- `llm_wiki_maintainer/ingest/generation.py`

能力：

- `AnalysisArtifact`
- `GenerationArtifact`
- 输入校验
- artifact contract 文档化

### Milestone 8: Query Backend

已完成：

- `llm_wiki_maintainer/query/tokenize.py`
- `llm_wiki_maintainer/query/retrieve.py`

能力：

- 英文 tokenization
- 中文 bigram
- 一定程度东亚脚本支持
- lexical retrieval
- excerpt/context assembly

修复过的问题包括：

- 短 token 误召回
- hyphen/space 归一化
- frontmatter 噪音 excerpt
- title/body/source-only excerpt 对齐

### Milestone 9: Graph Layer

已完成：

- `llm_wiki_maintainer/graph/build.py`
- `llm_wiki_maintainer/graph/insights.py`

能力：

- page/source nodes
- wikilink edges
- shared-source edges
- isolated page heuristic

修复过的问题包括：

- source metadata 覆盖
- malformed frontmatter 容错
- graph scope 漂移
- 重复边/degree 膨胀
- scalar `sources:` 规范化

### Milestone 10: Review / Research Schema

已完成：

- `llm_wiki_maintainer/review.py`
- `llm_wiki_maintainer/research.py`
- `tests/test_review.py`

能力：

- `ReviewItem`
- `ResearchTask`
- review approval copy semantics
- queries 输入规范化与校验

### Milestone 11: Source Lifecycle Analysis

已完成：

- `llm_wiki_maintainer/lifecycle.py`
- `tests/test_lifecycle.py`

能力：

- `SourceRemovalImpact`
- `analyze_source_removal`
- source deletion impact analysis

已覆盖：

- source cards to delete
- shared pages via `sources:`
- `Used by`
- unique bare-stem resolution
- explicit-path behavior
- self-link handling
- out-of-root display fallback
- external links 忽略
- fenced code / literal examples 忽略
- 仅扫描 compiled wiki/index surface

### Milestone 12: End-to-End Documentation / Entrypoint Alignment

已完成：

- `README.md`
- `SKILL.md`
- `references/templates.md`
- 多个 `scripts/*.py`

能力：

- backend/runtime split 文档化
- skill/operator docs 与实现对齐
- CLI root 解析行为统一
- brittle absolute-path defaults 清理
- report scaffold 健壮化

## 7. 已实现模块总览

当前已实现的主要 backend 模块：

### Parsing / Model

- `frontmatter.py`
- `models.py`

### Runtime Basics

- `config.py`
- `wiki_io.py`

### Source Maintenance

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

## 8. 目前 skill 的实际用法

### 8.1 `SKILL.md` 的角色

`SKILL.md` 现在的角色是：

- 操作规范
- 模型约束
- operator playbook
- 对 backend 的行为说明

它不再是整个项目唯一的逻辑来源。

### 8.2 推荐使用方式

1. 先把 `SKILL.md` 当作行为规则
2. 再优先调用 backend/CLI，而不是手工重复逻辑
3. 高风险操作先查 lifecycle / review / references 结果
4. query 优先走 retrieval，而不是直接盲扫 raw

### 8.3 当前 skill 与 backend 的关系

应当理解为：

- `SKILL.md` 负责定义“怎么做”
- `llm_wiki_maintainer/` 负责把“怎么做”变成可测试代码

## 9. 与 `nashsu/llm_wiki` 的差距

对比目标：

- `https://github.com/nashsu/llm_wiki`

### 9.1 已经缩小的差距

当前已经不再只是文档和脚本，而是有明确 backend 的系统基础：

- 可测试 backend
- query seed capability
- graph seed capability
- lifecycle analysis
- review/research schema
- ingest artifacts/cache/planner

### 9.2 仍然显著落后的地方

1. Persistent ingest runtime
- 没有 durable queue
- 没有 crash recovery
- 没有 retry/cancel/progress persistence

2. Review engine
- 现在只有 schema，没有真正 queue/workflow

3. Research engine
- 现在只有 schema，没有执行、调度、搜索闭环

4. Query runtime
- 只有 retrieval backend，没有完整 answer runtime

5. Graph intelligence
- 没有 relevance/community/surprising connections/gap discovery

6. Runtime state layer
- 没有统一 project state / runtime state store

7. Product layer
- 没有桌面 app / UI shell / activity panel / settings UX

### 9.3 当前准确结论

如果把 `nashsu/llm_wiki` 看作完整产品，那么本仓库现在的位置是：

- 已有较强 backend 基础
- 尚未进入完整 runtime / product 形态

差距已经不是“有没有基本能力”，而是“有没有持久化 runtime 和产品层”。

## 10. 现有验证结论

本轮演进过程中，已经多次做过：

- targeted pytest
- full pytest
- script wrapper smoke
- `py_compile`

最新一次全量回报结果为：

- `python3 -m pytest`
- `94 passed`

这意味着：

- 当前代码基线是可用的
- 大量边界行为已经有回归测试

## 11. 当前已知遗留问题

以下属于“已知但非阻塞”的遗留项。

### 11.1 Review / Research 仍是 schema，不是 runtime

当前：

- `ReviewItem`
- `ResearchTask`

只提供数据结构与基础行为，还没有：

- persisted queue
- status engine
- operator commands
- execution loop

### 11.2 Graph insights 仍然偏浅

当前只实现了 first-pass heuristic：

- isolated pages

没有：

- bridge nodes
- cluster/community
- graph-derived insight ranking

### 11.3 Query 仍是 backend，不是 full runtime

当前已有 retrieval，但缺少：

- answer assembly runtime
- query session persistence
- vector retrieval seam 的完整接入

### 11.4 Lifecycle 还没有 remediation planner

当前能分析 impact，但不能自动输出完整 fix plan：

- rename/move plan
- apply-ready patch suggestion

### 11.5 Runtime orchestration 缺失

这是当前最大的系统缺口：

- 没有 ingest queue
- 没有 project state
- 没有 durable runtime loop

## 12. 未来规划

### 12.1 已写入文件的下一阶段计划

下一阶段已经单独写入：

- [2026-04-25-llm-wiki-stage2-runtime-plan.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-stage2-runtime-plan.md)
- [2026-04-29-llm-wiki-final-plan-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md)

### 12.2 推荐执行顺序

1. Minimal Runtime
- ingest queue
- state persistence
- orchestration CLI

2. Review / Research Execution
- persisted queue
- review actions
- research task flow

3. Query Runtime Expansion
- answer-context assembler
- query runtime

4. Graph Intelligence
- relevance scoring
- communities
- richer insights

5. Lifecycle Engine Upgrade
- remediation planning
- rename/move/delete patch planning

6. Productization Readiness
- project config
- settings/state
- runtime API facade

## 13. 当前工作区与路径说明

### 13.1 当前正确工作区

当前实际工作区路径为：

`/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer`

### 13.2 路径迁移说明

历史上存在旧路径：

- `Glaucon Vault`

当前统一以：

- `Glaucon's Vault`

为准。

### 13.3 已处理的路径遗留

已经做过的清理包括：

- 更新 README 中残留的旧路径文案
- 清理旧路径 checkout 下的 `.pytest_cache`

仍需注意：

- 如果其他旧 checkout 目录仍存在，不应再把它们当作当前 source of truth

## 14. 文档清单建议

当前建议把以下文件当成项目文档入口：

1. 本文档
- `docs/superpowers/plans/2026-04-25-llm-wiki-project-dossier-zh.md`

2. 原始 backend 计划
- `docs/superpowers/plans/2026-04-24-llm-wiki-backend-roadmap.md`

3. 下一阶段 runtime 计划
- `docs/superpowers/plans/2026-04-25-llm-wiki-stage2-runtime-plan.md`

4. Operator skill
- `SKILL.md`

5. 项目说明
- `README.md`

6. 模板说明
- `references/templates.md`

## 15. 建议的后续维护规则

1. 新能力优先下沉到 `llm_wiki_maintainer/` 包
2. 脚本尽量只做 wrapper
3. 新规则优先写测试，再写实现
4. 重要 workflow 改动同时更新：
- `README.md`
- `SKILL.md`
- `references/templates.md`
- 本文档或阶段计划文档
5. 与路径相关的假设一律避免硬编码 vault 名称

## 16. 一句话总结

这个项目现在已经从一个“技能文档 + 辅助脚本”演进成了一个有明确后端边界、测试覆盖和持续演进路线的 `LLM Wiki` 基础设施仓库；下一阶段的主要任务，不再是补零散功能，而是把现有 backend 长成真正的 runtime。
