---
title: llm-wiki-maintainer 未来路线图
date: 2026-04-25
status: active
language: zh-CN
source_plan: docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md
---

# llm-wiki-maintainer 未来路线图

## 1. 背景

这份路线图现在作为摘要文档使用。

最终基线请以：

- `docs/superpowers/plans/2026-04-29-llm-wiki-final-plan-zh.md`

为准。

当前仓库的 backend 基础已经基本成型，后续重点不再是“有没有模块”，而是“有没有 runtime”。

## 2. 总体方向

下一阶段的核心目标是：

1. 把 backend 长成最小 runtime
2. 把 schema 长成 persisted workflow
3. 把 retrieval / graph 提升成更强 intelligence
4. 为未来产品化做准备

## 3. 分阶段路线

### Phase A: Minimal Runtime

目标：

- ingest queue
- state persistence
- job recovery
- orchestration CLI

### Phase B: Review / Research Execution

目标：

- persisted review queue
- persisted research queue
- approval-gated research flow

### Phase C: Query Runtime Expansion

目标：

- query models
- answer-context assembly
- query runtime entrypoint
- future vector seam

### Phase D: Graph Intelligence

目标：

- relevance scoring
- community / clustering seam
- richer graph insights

### Phase E: Productization Readiness

目标：

- project config
- settings/state
- runtime API facade
- 更完整 operator docs

## 4. 执行优先级

推荐顺序：

1. Minimal Runtime
2. Review / Research Execution
3. Query Runtime Expansion
4. Graph Intelligence
5. Productization Readiness

## 5. 为什么不是先做 UI

因为当前与 `nashsu/llm_wiki` 的主要差距在 runtime，不在界面。

如果先做 UI，会把没有稳定运行时的能力包装成表面完整产品，维护成本会上升，技术债会更重。

## 6. 对标 `nashsu/llm_wiki` 的剩余差距

### 仍待补齐

- persisted ingest queue
- crash recovery
- review queue
- research queue
- deeper query runtime
- graph intelligence
- runtime state layer
- application shell

### 已经具备的基础

- backend 包边界
- traceability discipline
- retrieval seed
- graph seed
- lifecycle seed
- operator docs

## 7. 进入下一阶段的条件

当以下条件都满足，可以认为当前阶段结束：

- backend / docs / wrappers 已对齐
- 全量测试通过
- operator 能稳定使用当前能力
- 未解决问题主要集中在 runtime/product 层

当前这几个条件已经基本满足。
