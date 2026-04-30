---
title: llm-wiki-maintainer 中文总览
date: 2026-04-25
status: active
language: zh-CN
---

# llm-wiki-maintainer 中文总览

## 项目是什么

`llm-wiki-maintainer` 是一个面向 `LLM Wiki` 工作流的维护与运行基础设施仓库。

它当前同时承担三种角色：

1. 一套操作规范
2. 一个可复用的 Python backend
3. 一组尽量薄的 CLI 工具入口

它已经不再只是一个“skill 文档”，但也还不是一个完整桌面产品。

## 项目解决什么问题

它主要解决这些问题：

- 如何维护 `raw / wiki / wiki/sources` 三层知识结构
- 如何让 source traceability 变成可执行规则，而不是只靠人记住
- 如何把 source-card、lint、ingest、query、graph、lifecycle 等能力沉淀成 backend
- 如何为未来完整 runtime 和产品化打底

## 当前已经做到什么程度

当前已经完成的核心能力包括：

- frontmatter 解析与序列化
- wiki IO / config 基础层
- source-card 创建与重复检测
- references / lint / used-by 同步
- ingest manifest / cache / planner
- 两阶段 ingest artifacts
- query tokenization / lexical retrieval / context assembly
- graph extraction 与基础 insight
- review / research schema
- source deletion impact analysis
- `README` / `SKILL` / 模板 / CLI 的最终对齐

当前项目已经有较强 backend 基础，并且测试覆盖已成型。

## 当前还没做到什么

还没有的部分主要集中在 runtime 和 product 层：

- 持久化 ingest queue
- 真正的 review queue / research queue
- 完整 query runtime
- 更深的 graph intelligence
- lifecycle remediation planner
- 桌面 UI / 产品壳

## 和 `nashsu/llm_wiki` 的关系

和 `nashsu/llm_wiki` 相比，这个项目现在的优势与差距非常清楚：

### 已具备的优势

- 规则层更明确
- source hygiene 更严格
- traceability 约束更清晰
- backend 模块边界更适合继续演进

### 仍然存在的差距

- 没有完整 runtime
- 没有 persisted queue/state
- 没有完整 review/research 执行层
- 没有完整 product/UI 层

一句话说：

> 这个项目已经接近“强 backend + operator workflow”，但还没到“完整 llm-wiki 产品”。

## 当前状态结论

如果只看 backend 和工程基础，这个项目已经从早期草创状态进入了“可持续迭代”的阶段。

如果目标是继续逼近 `nashsu/llm_wiki`，接下来的重点不该再是补零散脚本，而是：

1. 做最小 runtime
2. 做 review/research queue
3. 做 query runtime
4. 做 graph intelligence

## 建议阅读顺序

如果你第一次接手这个项目，建议按这个顺序读：

1. [README.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/README.md)
2. [SKILL.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/SKILL.md)
3. [2026-04-25-llm-wiki-project-dossier-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-project-dossier-zh.md)
4. [2026-04-25-llm-wiki-architecture-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-architecture-zh.md)
5. [2026-04-25-llm-wiki-capabilities-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-capabilities-zh.md)
6. [2026-04-25-llm-wiki-future-roadmap-zh.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/docs/superpowers/plans/2026-04-25-llm-wiki-future-roadmap-zh.md)
