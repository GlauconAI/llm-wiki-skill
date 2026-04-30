# llm-wiki-maintainer 全功能验收报告

## 范围与日期

- 验收日期：2026-04-30
- 验收范围：`llm_wiki_maintainer/` 后端模块、`runtime` 门面、`scripts/` CLI、工作流封装、注册表、source adapter、query/graph、governance、importer、lifecycle。
- 写入范围限制：本次验收仅新增本报告，未修改生产代码或测试代码。

## 测试环境

- 操作系统：macOS（Darwin）
- Python：`3.9.6`
- pytest：`8.4.2`
- 工作目录：`/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer`
- 说明：仓库工作树在验收开始时已存在其他未提交改动；本次未回滚或覆盖这些改动。

## 执行命令

### 1. 全量自动化验证

```bash
python3 -m pytest
```

结果：`169 passed in 9.95s`

### 2. 运行时与工作流 CLI 冒烟

在 `/tmp/llm-wiki-acceptance.DQJbSc/llm-wiki` 的 fixture 副本上执行：

```bash
python3 scripts/wiki_status.py /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/query_context.py example /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/save_query.py example /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki "Acceptance Saved Query"
python3 scripts/create_digest.py example /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki "Acceptance Digest"
python3 scripts/crystallize_note.py "Acceptance Insight" "A concise synthesis for acceptance testing." /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki SRC-1
python3 scripts/delete_source.py /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki/raw/sources/example-raw.md /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/source_adapters.py /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/create_source_card.py /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki/raw/sources/example-raw.md /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/suggest_target_pages.py /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki/raw/sources/example-raw.md /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/create_ingest_report.py "Acceptance Ingest Report" /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
python3 scripts/create_audit_report.py "Acceptance Audit Report" /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
```

### 3. 队列、导入、适配器、注册表、治理 CLI 冒烟

在 `/private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki` 的 fixture 副本上执行：

```bash
python3 scripts/lint_llm_wiki.py /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/update_used_by.py /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/run_ingest_queue.py enqueue /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki/raw/sources/example-raw.md /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/run_ingest_queue.py status /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/run_ingest_queue.py run /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/review_queue.py import /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki/.llm-wiki/generation/ingest-de3e96637b19.yaml /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/review_queue.py list /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/review_queue.py approve ingest-de3e96637b19-review-targets /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/review_queue.py show ingest-de3e96637b19-review-targets /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/run_research_queue.py run /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/import_folder.py /tmp/llm-wiki-acceptance2.Kb7wYo/import-src /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
python3 scripts/source_adapters.py /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki --with-research-provider
python3 scripts/wiki_registry.py add acceptance /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki /tmp/llm-wiki-acceptance2.Kb7wYo/registry.yaml
python3 scripts/wiki_registry.py activate acceptance /tmp/llm-wiki-acceptance2.Kb7wYo/registry.yaml
python3 scripts/wiki_registry.py list /tmp/llm-wiki-acceptance2.Kb7wYo/registry.yaml
python3 scripts/wiki_registry.py show-active /tmp/llm-wiki-acceptance2.Kb7wYo/registry.yaml
```

### 4. 运行时 API 与图谱/查询补充验证

```bash
python3 - <<'PY' /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki
from pathlib import Path
import sys
from llm_wiki_maintainer.runtime.api import LlmWikiRuntime
from llm_wiki_maintainer.query.vector import VectorMatch

class FakeVectorProvider:
    def search(self, query: str, root: Path, limit: int = 8):
        return [VectorMatch(path='wiki/overview', score=8.0, excerpt=f'vector:{query}')]

root = Path(sys.argv[1])
runtime = LlmWikiRuntime(root)
result = runtime.query('example', vector_provider=FakeVectorProvider())
graph = runtime.build_graph()
related = runtime.related_pages('wiki/overview', limit=5)
insights = runtime.graph_insights()
print('query_pages', len(result.package.pages))
print('graph_nodes', len(graph.nodes))
print('graph_edges', len(graph.edges))
print('related_count', len(related))
print('insight_keys', sorted(insights.keys()))
PY
```

## 功能检查清单

| 区域 | 检查内容 | 状态 | 关键证据 |
| --- | --- | --- | --- |
| 后端模块基础 | frontmatter、IO、references、source cards、research/review/runtime state 等单测覆盖 | 通过 | `pytest` 全量通过，169/169 |
| Runtime facade | `ProjectLayout`、`LlmWikiRuntime`、ingest/query/review/research/graph/status/delete API | 通过 | 运行时 API 补充验证返回 `query_pages 1`、`graph_nodes 4`、`related_count 2` |
| Query / Graph | 词法检索、bounded context、vector seam、graph build、insights、related pages | 通过 | `query_context.py` 输出 Query/Pages/Context；`create_digest.py` 生成 Graph Signals；API 返回 7 个 insight keys |
| Workflows | `status`、`save-query`、`digest`、`crystallize`、`delete` | 通过 | 生成了 `wiki/queries/acceptance-saved-query.md`、`wiki/digests/acceptance-digest.md`、`wiki/crystallized/acceptance-insight.md`；`delete_source.py` 正确给出影响预览 |
| Ingest / Review / Research 队列 | 入队、执行、artifact 持久化、review handoff、research note 回流 ingest | 通过 | `.llm-wiki/generation/ingest-de3e96637b19.yaml` 含 review item；`review_queue.py approve` 成功；`run_research_queue.py` 生成 `raw/research/acceptance-research.md` 并在 `runtime-state.yaml` 中新建待处理 ingest job |
| Registry | add / activate / list / show-active，root 解析顺序 | 通过 | `wiki_registry.py` 成功注册并激活 `acceptance`；列表显示 `* acceptance ...` |
| Source adapters | local file、folder import、research task 状态标准化 | 通过 | 无 provider 时 `research_task env_unavailable`；带 `--with-research-provider` 时变为 `ready` |
| Importer | 目录导入到 `raw/imports/` 并入运行时 | 通过 | `import_folder.py` 输出 `folder_import: ready` 与 `imported 1 file(s)`，生成 `raw/imports/import-src/a.md` |
| Governance / Lifecycle | lint、used-by 同步、source deletion impact analysis | 通过（有保留） | `update_used_by.py` 正常执行；`delete_source.py` 输出依赖页面和 broken links；`lint_llm_wiki.py` 能稳定列出 24 个结构问题 |
| CLI 脚本层整体 | README 声明入口的可用性 | 有缺陷 | `create_source_card.py` 在 macOS `/tmp` 绝对路径场景下复现失败，见下文发现 1 |

## 关键证据与观察

### 1. 自动化验证基线稳定

- 全量测试一次通过：`169 passed in 9.95s`。
- 覆盖面已包含 query、graph、runtime facade、source adapters、review/research queue、registry、workflow scripts。

### 2. 运行时门面与持久化状态符合声明

- [llm_wiki_maintainer/runtime/api.py](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/llm_wiki_maintainer/runtime/api.py:50) 暴露的 facade 方法，均能在测试或冒烟中对应到可执行路径。
- `run_ingest_queue.py run` 后产生：
  - `.llm-wiki/analysis/ingest-de3e96637b19.yaml`
  - `.llm-wiki/generation/ingest-de3e96637b19.yaml`
  - `.llm-wiki/state/runtime-state.yaml`
- generation artifact 中包含 review handoff：
  - `id: ingest-de3e96637b19-review-targets`
  - `action: review_ingest_targets`

### 3. Query / Digest / Crystal 产物结构正确

- `save_query.py` 生成的查询笔记包含 frontmatter、`## Retrieved Pages`、`## Context Package`。
- `create_digest.py` 生成的 digest 包含 `## Graph Signals`，并列出 Bridge Pages、Dense Clusters、Knowledge Gaps、Orphaned Source Cards、Top Cohesion Clusters。
- `crystallize_note.py` 生成的结晶笔记包含 `sources` frontmatter 与 `## Source IDs`。

### 4. Research 与 importer 成功回流 ingest

- `run_research_queue.py run` 生成 [acceptance-research.md](/private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki/raw/research/acceptance-research.md:1)。
- `runtime-state.yaml` 中新增：
  - `raw/research/acceptance-research.md` 的待处理 ingest job
  - `raw/imports/import-src/a.md` 的待处理 ingest job
- 这说明 research 与 folder import 都能通过共享 runtime state 重新进入 ingest 生命周期。

## 发现与问题

### 发现 1：`create_source_card.py` 对 macOS `/tmp` 绝对路径不稳，CLI 可复现失败

状态：已复现，属于真实缺陷。

复现命令：

```bash
python3 scripts/create_source_card.py \
  /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki/raw/sources/example-raw.md \
  /tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
```

实际结果：

```text
ERROR: raw file must live under llm-wiki root: /private/tmp/llm-wiki-acceptance.DQJbSc/llm-wiki
```

原因判断：

- [scripts/create_source_card.py](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/scripts/create_source_card.py:33) 对绝对 `raw_file` 只做 `expanduser()`，未统一 `resolve()`。
- [scripts/create_source_card.py](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/scripts/create_source_card.py:42) 对 root 参数做了 `resolve()`。
- [scripts/create_source_card.py](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/scripts/create_source_card.py:61) 使用 `raw_file.relative_to(cfg.root)` 比较时，`/tmp/...` 与 `/private/tmp/...` 不等价，导致误判“raw file 不在 root 下”。

影响：

- README 声明的官方 CLI 用法 `python3 scripts/create_source_card.py <raw-file> [llm-wiki-root]` 在 macOS 常见临时目录符号链接路径下并不稳健。
- 该缺陷不影响 backend 的 `create_source_card(...)` 函数本身，也不影响相对路径或已 canonicalize 的绝对路径。

### 发现 2：仓库自带最小 fixture 不是 lint-clean 样例

状态：非阻塞，属于验收时的环境观察，不视为生产代码故障。

证据：

- `python3 scripts/lint_llm_wiki.py /private/tmp/llm-wiki-acceptance2.Kb7wYo/llm-wiki` 返回 24 个问题。
- 主要来源是 fixture 页面过于简化：
  - [dup.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/tests/fixtures/wiki_minimal/wiki/dup.md:1) 只有 metadata 和重复链接。
  - [scalar.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/tests/fixtures/wiki_minimal/wiki/scalar.md:1) 缺少 compiled-page 必需章节。
  - [index.md](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/tests/fixtures/wiki_minimal/index.md:1) 未收录 `dup`、`scalar`。

影响：

- lint 功能本身工作正常，且输出可读、无 traceback。
- 但仓库当前没有一个我在手工验收中可直接运行出 `LLM Wiki lint: PASS` 的官方示例根目录。

## 残余风险 / 非阻塞问题

- `create_source_card.py` 的路径规范化缺陷会影响部分 macOS 操作员场景，尤其是从 `/tmp/...` 传入绝对路径时。
- 本次 research 冒烟使用的是脚本内置假 provider，验证的是队列执行和状态流转，不是外部搜索集成质量。
- 本次 query / graph 冒烟基于极小 fixture，证明了机制通路，但不能代表真实知识库规模下的检索质量与图谱信号质量。
- 仓库自带 fixture 更偏“测试夹具”而非“健康样例库”；对新维护者来说，容易误解 lint 失败是系统整体不可用。

## 后续修复更新

在本报告出具后，主线程已经完成两项收尾修复：

- 修复了 [create_source_card.py](/Users/glaucon/.openclaw/workspace/aristotle/skills-dev/llm-wiki-maintainer/scripts/create_source_card.py:33) 对 macOS `/tmp` 绝对路径的规范化问题，现已通过回归测试覆盖。
- 新增 `tests/fixtures/wiki_healthy/` 作为官方 lint-clean 健康样例，并增加 `lint_root()` 对该样例必须返回空问题集的回归测试。

后续验证结果：

- `python3 -m pytest -q` -> `171 passed`

## 最终验收结论

结论：**接受（accepted）**

更新后的判断依据：

- 主体功能面完整，且修复后全量自动化验证 `171/171` 通过。
- runtime facade、队列、query/graph、adapter、registry、importer、治理删除预览等核心能力都已完成可执行验证。
- 原验收中的两个保留项都已被关闭，因此不再保留 `accepted with caveats` 状态。
