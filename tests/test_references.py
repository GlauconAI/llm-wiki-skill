from llm_wiki_maintainer.references import compute_used_by


def test_compute_used_by_supports_multiline_sources(wiki_root):
    page = wiki_root / "wiki" / "topic-a.md"
    page.write_text(
        "---\n"
        "type: topic\n"
        "sources:\n"
        "  - SRC-1\n"
        "---\n"
        "# Topic\n",
        encoding="utf-8",
    )

    mapping = compute_used_by(wiki_root)

    assert mapping["wiki/sources/example-source.md"] == {
        "wiki/overview",
        "wiki/topic-a",
    }
