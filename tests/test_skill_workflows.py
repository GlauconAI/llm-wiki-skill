from pathlib import Path

from llm_wiki_maintainer.runtime.api import LlmWikiRuntime


def test_runtime_status_summarizes_project_state(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)

    summary = runtime.status()

    assert summary.root == wiki_root.resolve()
    assert summary.page_count == 3
    assert summary.source_card_count == 1
    assert summary.raw_count == 1
    assert summary.ingest_jobs["pending"] == 0
    assert summary.review_items["pending"] == 0
    assert summary.research_tasks["pending"] == 0


def test_runtime_digest_persists_query_report(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)
    bridge = wiki_root / "wiki" / "bridge.md"
    bridge.write_text(
        """---
type: concept
title: Bridge
sources: [SRC-1]
---

See [[wiki/overview]] and [[wiki/scalar]].
""",
        encoding="utf-8",
    )

    digest = runtime.create_digest("example", title="Example Digest")

    assert digest.path == wiki_root / "wiki" / "digests" / "example-digest.md"
    assert digest.path.is_file()
    text = digest.path.read_text(encoding="utf-8")
    assert "type: digest" in text
    assert "title: Example Digest" in text
    assert "query: example" in text
    assert "# Example Digest" in text
    assert "## Context Package" in text
    assert "[[wiki/overview]]" in text
    assert "[[(\'" not in text
    assert "[[wiki/bridge]]" in text


def test_runtime_save_query_persists_bounded_context_without_digest_sections(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)

    note = runtime.save_query("example", title="Example Saved Query")

    assert note.path == wiki_root / "wiki" / "queries" / "example-saved-query.md"
    assert note.path.is_file()
    text = note.path.read_text(encoding="utf-8")
    assert "type: query" in text
    assert "title: Example Saved Query" in text
    assert "query: example" in text
    assert "# Example Saved Query" in text
    assert "## Retrieved Pages" in text
    assert "## Context Package" in text
    assert "## Graph Signals" not in text


def test_runtime_crystallize_persists_standalone_wiki_note(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)

    note = runtime.crystallize(
        title="Working Insight",
        summary="A compressed synthesis.",
        bullets=["Keep the synthesis durable.", "Link it back into the wiki."],
        sources=["SRC-1"],
    )

    assert note.path == wiki_root / "wiki" / "crystallized" / "working-insight.md"
    assert note.path.is_file()
    text = note.path.read_text(encoding="utf-8")
    assert "type: crystal" in text
    assert "title: Working Insight" in text
    assert "sources:" in text
    assert "# Working Insight" in text
    assert "A compressed synthesis." in text
    assert "- Keep the synthesis durable." in text


def test_query_and_crystal_titles_support_non_ascii_without_falling_back_to_note(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)

    query_note = runtime.save_query("example", title="中文 查询")
    crystal_note = runtime.crystallize(title="中文 结晶", summary="摘要")

    assert query_note.path.name != "note.md"
    assert crystal_note.path.name != "note.md"
    assert "中文" in query_note.path.stem
    assert "中文" in crystal_note.path.stem


def test_runtime_delete_source_defaults_to_impact_only(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"

    result = runtime.delete_source(raw)

    assert raw.is_file()
    assert source_card.is_file()
    assert result.applied is False
    assert result.impact.source_cards_to_delete == [source_card.resolve()]
    assert wiki_root / "wiki" / "overview.md" in result.impact.pages_to_update


def test_runtime_delete_source_apply_removes_raw_and_source_card(wiki_root: Path):
    runtime = LlmWikiRuntime(wiki_root)
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"

    result = runtime.delete_source(raw, apply=True)

    assert result.applied is True
    assert not raw.exists()
    assert not source_card.exists()
