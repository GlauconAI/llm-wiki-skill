from pathlib import Path

from llm_wiki_maintainer.lifecycle import analyze_source_removal


def test_analyze_source_removal_reports_dependent_pages(wiki_root: Path) -> None:
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    impact = analyze_source_removal(wiki_root, raw)

    source_card = wiki_root / "wiki" / "sources" / "example-source.md"
    overview = wiki_root / "wiki" / "overview.md"

    assert impact.source_cards_to_delete == [source_card.resolve()]
    assert isinstance(impact.pages_to_update, list)
    assert overview.resolve() in impact.pages_to_update
    assert any("overview.md" in link for link in impact.broken_links)
    assert not any(
        link.startswith("wiki/sources/example-source.md ->")
        for link in impact.broken_links
    )


def test_analyze_source_removal_reports_sources_frontmatter_dependencies(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    shared = wiki_root / "wiki" / "shared.md"
    shared.write_text(
        "---\n"
        "type: concept\n"
        "title: Shared Page\n"
        "sources: [SRC-1]\n"
        "---\n"
        "\n"
        "# Shared Page\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert shared.resolve() in impact.pages_to_update


def test_analyze_source_removal_does_not_resolve_bare_stem_used_by_links(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "ambiguous-raw.md"
    raw.write_text(
        "# Ambiguous Raw\n",
        encoding="utf-8",
    )
    source_card = wiki_root / "wiki" / "sources" / "ambiguous-source.md"
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-99\n"
        "title: Ambiguous Source\n"
        "---\n"
        "\n"
        "# Source: Ambiguous Source\n"
        "\n"
        "## Location\n"
        "[[raw/sources/ambiguous-raw|/raw/sources/ambiguous-raw.md]]\n"
        "\n"
        "## Type\n"
        "md\n"
        "\n"
        "## Coverage\n"
        "- Ambiguous coverage.\n"
        "\n"
        "## Used by\n"
        "- [[overview]]\n"
        "\n"
        "## Key Sections\n"
        "- Ambiguous section.\n"
        "\n"
        "## Notes\n"
        "- Ambiguous source card for testing.\n",
        encoding="utf-8",
    )
    ambiguous_overview = wiki_root / "overview.md"
    ambiguous_overview.write_text(
        "# Ambiguous Overview\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert impact.source_cards_to_delete == [source_card.resolve()]
    assert ambiguous_overview.resolve() not in impact.pages_to_update
    assert not any(link.startswith("overview.md") for link in impact.broken_links)
