---
title: llm-wiki-maintainer 最终版方案与里程碑
date: 2026-04-29
status: active
language: zh-CN
owner: codex
scope: final-baseline
supersedes:
  - docs/superpowers/plans/2026-04-25-llm-wiki-future-roadmap-zh.md
  - docs/superpowers/plans/2026-04-25-llm-wiki-stage2-runtime-plan.md
---

# llm-wiki-maintainer 最终版方案与里程碑

## 1. 文档目的

这份文档用于收口 `llm-wiki-maintainer` 的最终版方案。

它解决两个问题：

1. 明确这个仓库最终要成为什么
2. 明确接下来只按哪些 Milestone 往前推进

从这份文档开始，后续路线应以本文件为主基线，旧 roadmap 和阶段计划保留为历史背景与补充实现参考。

## 2. 最终定位

`llm-wiki-maintainer` 的最终定位是：

> 一个面向 `LLM Wiki` 的可测试 backend + persisted runtime core + operator CLI 仓库。

这意味着它：

1. 不是单纯的 skill 文档
2. 不是只靠若干一次性脚本维持的工具集合
3. 不是当前阶段就要完成的桌面 UI 产品

它的核心价值在于：

- 把 `raw / wiki / wiki/sources` 三层模型做成可执行系统
- 把 source traceability 和 no source laundering 做成代码与测试
- 把 ingest / review / research / query / lifecycle 的关键流程沉淀成 runtime

## 3. 项目边界

### 3.1 当前阶段明确要做的

1. 继续巩固 backend 作为唯一行为来源
2. 在 backend 之上补齐 persisted runtime
3. 为 operator 提供稳定 CLI 入口
4. 为未来 query / graph / 产品层保留扩展缝

### 3.2 当前阶段明确不做的

1. 不先做桌面 UI 或 application shell
2. 不先接具体 provider 绑定的 vector / search / research 执行器
3. 不做复杂并行调度或分布式系统
4. 不把 source card 扩成 summary 层
5. 不用产品壳去掩盖 runtime 尚未成型的问题

## 4. 最终架构方向

最终方案固定为三层：

### 4.1 Foundation Layer

职责：

- frontmatter / config / wiki_io
- source cards / references / linting / lifecycle
- ingest cache / planner / artifacts
- query lexical seed
- graph extraction seed
- review / research schema

判断：

这一层已经基本完成，并且测试基线已经成立。

### 4.2 Runtime Layer

职责：

- persisted state
- ingest jobs
- queue execution
- retry / cancel / resume
- review / research handoff
- operator-facing runtime CLI

判断：

这是当前主线，也是仓库从“强 backend”走到“可运行系统”的关键层。

### 4.3 Intelligence Layer

职责：

- query context assembly
- graph relevance / clustering / richer insights
- lifecycle remediation planning
- future vector seam
- future runtime API facade

判断：

这层重要，但必须排在 runtime 之后，不能喧宾夺主。

## 5. 关键设计原则

最终版方案继续坚持这些原则，不再摇摆：

1. compiled-first, raw-backstop
2. source traceability first
3. no source laundering
4. backend-first, wrapper-thin
5. governance before over-automation
6. runtime before product shell
7. tests before trust

其中需要特别强调两点：

### 5.1 Runtime before product shell

当前与 `nashsu/llm_wiki` 的主要差距在 runtime，不在界面。

如果先做 UI，只会把未完成的系统包装成“看起来像产品”的外壳，技术债会更重。

### 5.2 Governance before over-automation

`ReviewItem` 和 `ResearchTask` 的价值不是多两个模块，而是把不确定性、高风险 claim、以及需要人工判断的内容从自动化链路中切出来。

它们属于治理层，而不是装饰性功能层。

## 6. 最终 Milestone

最终里程碑固定为 6 个。

### Milestone 1: Backend Foundation Complete

状态：已完成

范围：

- package scaffold
- frontmatter / models
- config / wiki_io
- source_cards
- references / linting / links
- ingest cache / planner / artifacts
- query lexical retrieval seed
- graph extraction seed
- lifecycle analysis
- review / research schema
- tests / fixtures / harness

验收标准：

- backend 边界清晰
- CLI 主要调用 backend 而非重复逻辑
- 全量测试通过

### Milestone 2: Operator CLI Stabilized

状态：已完成

范围：

- `scripts/create_source_card.py`
- `scripts/suggest_target_pages.py`
- `scripts/lint_llm_wiki.py`
- `scripts/update_used_by.py`
- report scaffolders
- root resolution / dynamic date / wrapper 回归测试

验收标准：

- CLI 不依赖机器绑定默认路径
- 关键入口行为稳定
- 常见回归点有测试保护

### Milestone 3: Minimal Runtime

状态：下一优先级

范围：

- `llm_wiki_maintainer/runtime/jobs.py`
- `llm_wiki_maintainer/runtime/state.py`
- `llm_wiki_maintainer/runtime/ingest_queue.py`
- `scripts/run_ingest_queue.py`

关键目标：

- enqueue raw
- 判断是否变更
- 生成和记录 ingest artifacts
- 产出 review / research handoff
- 记录 status 并支持恢复

验收标准：

- job 状态持久化
- 进程重启后可恢复
- unchanged raw 可跳过
- 串行执行稳定可复现
- failure state 可重试

### Milestone 4: Governance Runtime

状态：Milestone 3 后

范围：

- `llm_wiki_maintainer/review_queue.py`
- `llm_wiki_maintainer/research_queue.py`
- `llm_wiki_maintainer/research_runtime.py`
- `scripts/review_queue.py`

关键目标：

- persisted review queue
- persisted research queue
- approval-gated research flow
- human-in-the-loop 边界落地

验收标准：

- review item 可流转
- research task 可排队和恢复
- 未审批内容不能直接进入 research flow
- 治理规则由代码和测试强制执行

### Milestone 5: Query And Graph Runtime Expansion

状态：Milestone 4 后

范围：

- `llm_wiki_maintainer/query/models.py`
- `llm_wiki_maintainer/query/assemble.py`
- `llm_wiki_maintainer/query/runtime.py`
- `scripts/query_context.py`
- `llm_wiki_maintainer/graph/relevance.py`
- `llm_wiki_maintainer/graph/community.py`
- `llm_wiki_maintainer/graph/insights.py`

关键目标：

- bounded context assembly
- deterministic runtime query path
- explainable graph relevance and insight generation

验收标准：

- query runtime 输出可用 context package
- graph insights 结果可解释、可复现
- 不引入 provider lock-in

### Milestone 6: Productization Readiness

状态：最后阶段

范围：

- runtime API facade
- project config / state conventions
- operator docs consolidation
- future UI / app shell integration seam

关键目标：

- 让 CLI 与未来 UI 共享 runtime 核心
- 让产品接入不需要重写 backend 与 state layer

验收标准：

- runtime 接口边界稳定
- state 目录与扩展点清晰
- 产品层可接入，但不反向污染核心模块

## 7. 最终执行顺序

最终顺序固定为：

1. Backend Foundation Complete
2. Operator CLI Stabilized
3. Minimal Runtime
4. Governance Runtime
5. Query And Graph Runtime Expansion
6. Productization Readiness

其中真正尚待实现的主线，是 Milestone 3 到 Milestone 6。

## 8. 进入下一阶段的正式条件

满足以下条件后，应视为“路线收口完成”，后续进入按 Milestone 执行阶段：

1. 项目定位不再摇摆
2. 不再把 UI 当作当前主路线
3. runtime 成为明确第一优先级
4. review / research 被承认为治理层
5. query / graph 被放回 runtime 之后的增强层

当前这些条件已经满足。

## 9. 对后续实现的约束

后续若新增 plan、spec 或实现任务，应遵守：

1. 新工作必须能映射到 6 个最终 Milestone 之一
2. 若某项工作无法映射，应先质疑其必要性，而不是直接实现
3. 若某项工作抢在 Milestone 3 之前推动 UI 或产品壳，应默认视为偏航
4. 若某项工作把 review / research 变成无约束自动化，应默认视为违反治理边界

## 10. 结论

`llm-wiki-maintainer` 当前不缺更多分散功能点，缺的是路线收紧。

最终版方案已经明确：

- 仓库目标是 `backend + runtime core`
- 当前主线是 persisted runtime
- review / research 是治理层
- query / graph 是后续增强层
- 产品化排在最后

后续执行应以此为唯一基线。
