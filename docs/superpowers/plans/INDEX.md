# llm-wiki-maintainer 文档导航

这个目录同时包含：

- 历史执行计划
- 当前项目总档案
- 中文说明文档
- 下一阶段路线图

如果你是第一次进入这个项目，建议按下面的顺序阅读。

## 1. 项目总入口

1. [中文总览](./2026-04-25-llm-wiki-overview-zh.md)
- 最短路径理解这个项目是什么、做到哪一步、还缺什么

2. [项目总档案](./2026-04-25-llm-wiki-project-dossier-zh.md)
- 最完整的中文主记录
- 包含定位、设计、Milestone、差距、遗留问题、未来规划

3. [最终版方案与里程碑](./2026-04-29-llm-wiki-final-plan-zh.md)
- 当前后续执行的正式基线
- 明确最终定位、边界与 6 个固定 Milestone

## 2. 分主题文档

1. [架构说明](./2026-04-25-llm-wiki-architecture-zh.md)
- 看代码与文档分层、backend 包结构、脚本层原则

2. [当前能力清单](./2026-04-25-llm-wiki-capabilities-zh.md)
- 看现在已经实现了什么

3. [未来路线图](./2026-04-25-llm-wiki-future-roadmap-zh.md)
- 看下一阶段应该往哪做

## 3. 执行计划

1. [Backend Roadmap](./2026-04-24-llm-wiki-backend-roadmap.md)
- 第一阶段实际执行路线图

2. [Stage 2 Runtime Alignment Plan](./2026-04-25-llm-wiki-stage2-runtime-plan.md)
- 对齐 `nashsu/llm_wiki` 的下一阶段计划

3. [最终版方案与里程碑](./2026-04-29-llm-wiki-final-plan-zh.md)
- 当前执行时应优先参照的收口版本

## 4. 仓库其他关键文档

这些文档不在本目录，但应当一起看：

1. [README.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/README.md)
- 项目说明、backend/runtime split

2. [SKILL.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/SKILL.md)
- operator 规则与 skill 使用规范

3. [references/templates.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/references/templates.md)
- 模板与输出格式说明

## 5. 建议阅读顺序

### 如果你是项目负责人

1. 中文总览
2. 项目总档案
3. 最终版方案与里程碑
4. 未来路线图

### 如果你是实现者

1. 架构说明
2. 当前能力清单
3. 最终版方案与里程碑
4. Backend Roadmap
5. Stage 2 Runtime Alignment Plan

### 如果你是操作者 / agent

1. README
2. SKILL.md
3. 中文总览
4. 最终版方案与里程碑
5. 当前能力清单

## 6. 维护约定

后续如果继续补文档，建议遵守：

1. 总体变化先更新：
- `README.md`
- `SKILL.md`
- 本目录下的中文总档案或路线图

2. 新阶段实施前：
- 先加新的 plan 文件

3. 新模块落地后：
- 同步更新“当前能力清单”

4. 方向变化后：
- 同步更新“未来路线图”
