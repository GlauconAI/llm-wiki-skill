---
title: llm-wiki-maintainer 当前能力清单
date: 2026-04-25
status: active
language: zh-CN
---

# llm-wiki-maintainer 当前能力清单

## 1. 解析与基础设施

- frontmatter 解析与安全写出
- runtime config
- safe file IO
- fixture wiki / harness / regression tests

## 2. Source 维护

- source-card 创建
- source-card 重复检测
- source-card path normalization
- source-card id 相关校验

## 3. References / Lint

- `sources:` 依赖解析
- `Used by` 同步
- malformed 输入容错
- lint 规则校验

## 4. Ingest 基础能力

- source hash manifest
- changed / unchanged 判断
- target page planning
- analysis artifact
- generation artifact

## 5. Query 基础能力

- 英文 tokenization
- 中文 bigram
- 一定程度东亚脚本支持
- lexical retrieval
- context assembly
- title/body/source-only excerpt 处理

## 6. Graph 基础能力

- graph build
- page/source node
- wikilink edge
- shared-source edge
- isolated page heuristic

## 7. Review / Research 基础能力

- `ReviewItem`
- `ResearchTask`
- 审批/队列规则文档化

## 8. Lifecycle 基础能力

- source removal impact analysis
- 共享页 `sources:` 依赖检测
- unique bare-stem 解析
- explicit-path 解析
- self-link / external link / code-fence / out-of-root 容错

## 9. Docs / Entrypoint 对齐

- `README.md`
- `SKILL.md`
- `references/templates.md`
- CLI root resolution 更新
- report scaffold 健壮化

## 10. 当前能力边界

这个仓库当前已经能做：

- 一个可靠的 llm-wiki backend 基础层
- 一组面向 operator 的维护型工具
- 一部分 runtime 前置能力

这个仓库当前还不能做：

- 完整 ingest runtime
- 持久化 review/research queue
- 完整 query runtime
- product 级桌面应用
