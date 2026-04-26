from pathlib import Path

import llm_wiki_maintainer.lifecycle as lifecycle
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
    assert "wiki/sources/example-source.md -> [[raw/sources/example-raw]]" in (
        impact.broken_links
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


def test_analyze_source_removal_reports_self_referential_source_link(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-1\n"
        "title: Example Source\n"
        "---\n"
        "\n"
        "# Source: Example Source\n"
        "\n"
        "## Location\n"
        "[[raw/sources/example-raw|/raw/sources/example-raw.md]]\n"
        "\n"
        "## Type\n"
        "md\n"
        "\n"
        "## Coverage\n"
        "- Minimal fixture coverage.\n"
        "\n"
        "## Used by\n"
        "- [[wiki/sources/example-source]]\n"
        "\n"
        "## Key Sections\n"
        "- Minimal fixture section.\n"
        "\n"
        "## Notes\n"
        "- Minimal source card for lint and harness coverage.\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert (
        "wiki/sources/example-source.md -> [[wiki/sources/example-source]]"
        in impact.broken_links
    )
    assert source_card.resolve() not in impact.pages_to_update
    assert not set(impact.source_cards_to_delete) & set(impact.pages_to_update)


def test_analyze_source_removal_resolves_unique_bare_stem_used_by_links(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "bare-stem-raw.md"
    raw.write_text(
        "# Bare Stem Raw\n",
        encoding="utf-8",
    )
    source_card = wiki_root / "wiki" / "sources" / "bare-stem-source.md"
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-100\n"
        "title: Bare Stem Source\n"
        "---\n"
        "\n"
        "# Source: Bare Stem Source\n"
        "\n"
        "## Location\n"
        "[[raw/sources/bare-stem-raw|/raw/sources/bare-stem-raw.md]]\n"
        "\n"
        "## Type\n"
        "md\n"
        "\n"
        "## Coverage\n"
        "- Bare stem coverage.\n"
        "\n"
        "## Used by\n"
        "- [[overview]]\n"
        "\n"
        "## Key Sections\n"
        "- Bare stem section.\n"
        "\n"
        "## Notes\n"
        "- Bare stem source card for testing.\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert wiki_root.joinpath("wiki", "overview.md").resolve() in impact.pages_to_update
    assert not any("wiki/overview.md -> [[overview]]" in link for link in impact.broken_links)


def test_analyze_source_removal_does_not_resolve_ambiguous_bare_stem_used_by_links(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "ambiguous-bare-stem-raw.md"
    raw.write_text(
        "# Ambiguous Bare Stem Raw\n",
        encoding="utf-8",
    )
    source_card = wiki_root / "wiki" / "sources" / "ambiguous-bare-stem-source.md"
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-102\n"
        "title: Ambiguous Bare Stem Source\n"
        "---\n"
        "\n"
        "# Source: Ambiguous Bare Stem Source\n"
        "\n"
        "## Location\n"
        "[[raw/sources/ambiguous-bare-stem-raw|/raw/sources/ambiguous-bare-stem-raw.md]]\n"
        "\n"
        "## Type\n"
        "md\n"
        "\n"
        "## Coverage\n"
        "- Ambiguous bare stem coverage.\n"
        "\n"
        "## Used by\n"
        "- [[consumer]]\n"
        "\n"
        "## Key Sections\n"
        "- Ambiguous bare stem section.\n"
        "\n"
        "## Notes\n"
        "- Ambiguous bare stem source card for testing.\n",
        encoding="utf-8",
    )
    same_directory_consumer = wiki_root / "wiki" / "sources" / "consumer.md"
    same_directory_consumer.write_text(
        "# Same Directory Consumer\n",
        encoding="utf-8",
    )
    elsewhere_consumer = wiki_root / "wiki" / "consumer.md"
    elsewhere_consumer.write_text(
        "# Elsewhere Consumer\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert source_card.resolve() in impact.source_cards_to_delete
    assert same_directory_consumer.resolve() not in impact.pages_to_update
    assert elsewhere_consumer.resolve() not in impact.pages_to_update
    assert not any("wiki/sources/consumer.md -> [[consumer]]" in link for link in impact.broken_links)
    assert not any("wiki/consumer.md -> [[consumer]]" in link for link in impact.broken_links)


def test_analyze_source_removal_does_not_fall_back_from_explicit_path_links(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "docs-raw.md"
    raw.write_text(
        "# Docs Raw\n",
        encoding="utf-8",
    )
    source_card = wiki_root / "wiki" / "sources" / "docs-source.md"
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-101\n"
        "title: Docs Source\n"
        "---\n"
        "\n"
        "# Source: Docs Source\n"
        "\n"
        "## Location\n"
        "[[raw/sources/docs-raw|/raw/sources/docs-raw.md]]\n"
        "\n"
        "## Type\n"
        "md\n"
        "\n"
        "## Coverage\n"
        "- Docs coverage.\n"
        "\n"
        "## Used by\n"
        "- [[docs/example]]\n"
        "\n"
        "## Key Sections\n"
        "- Docs section.\n"
        "\n"
        "## Notes\n"
        "- Docs source card for testing.\n",
        encoding="utf-8",
    )
    unrelated = wiki_root / "wiki" / "notes" / "example.md"
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    unrelated.write_text(
        "# Example\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert source_card.resolve() in impact.source_cards_to_delete
    assert unrelated.resolve() not in impact.pages_to_update
    assert not any("docs/example" in link for link in impact.broken_links)


def test_analyze_source_removal_uses_safe_display_for_source_outside_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    raw = tmp_path / "outside" / "raw" / "example-raw.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# Outside Raw\n", encoding="utf-8")
    source_card = tmp_path / "outside" / "wiki" / "sources" / "example-source.md"
    source_card.parent.mkdir(parents=True)
    source_target = source_card.resolve().with_suffix("").as_posix().lstrip("/")
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-500\n"
        "title: Outside Source\n"
        "---\n"
        "\n"
        "## Used by\n"
        f"- [[{source_target}]]\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        lifecycle,
        "_source_cards_for_raw",
        lambda root_path, raw_target: [source_card.resolve()],
    )

    impact = analyze_source_removal(root, raw)

    assert impact.source_cards_to_delete == [source_card.resolve()]
    assert any(
        link.startswith(f"{source_card.resolve().as_posix()} -> [[{source_target}]]")
        for link in impact.broken_links
    )


def test_analyze_source_removal_ignores_external_markdown_links(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "external-links-raw.md"
    raw.write_text(
        "# External Links Raw\n",
        encoding="utf-8",
    )
    source_card = wiki_root / "wiki" / "sources" / "external-links-source.md"
    source_card.write_text(
        "---\n"
        "type: source\n"
        "id: SRC-501\n"
        "title: External Links Source\n"
        "---\n"
        "\n"
        "## Location\n"
        "[[raw/sources/external-links-raw|/raw/sources/external-links-raw.md]]\n"
        "\n"
        "## Used by\n"
        "- [openai](https://openai.com)\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert impact.source_cards_to_delete == [source_card.resolve()]
    assert not any("openai" in link for link in impact.broken_links)


def test_analyze_source_removal_ignores_markdown_outside_wiki_surface(
    wiki_root: Path,
) -> None:
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    docs_page = wiki_root / "docs" / "plan.md"
    docs_page.parent.mkdir(parents=True, exist_ok=True)
    docs_page.write_text(
        "---\n"
        "type: note\n"
        "title: External Plan\n"
        "sources: [SRC-1]\n"
        "---\n"
        "\n"
        "# External Plan\n"
        "\n"
        "## Notes\n"
        "- [[raw/sources/example-raw|/raw/sources/example-raw.md]]\n",
        encoding="utf-8",
    )

    impact = analyze_source_removal(wiki_root, raw)

    assert docs_page.resolve() not in impact.pages_to_update
    assert not any("docs/plan.md" in link for link in impact.broken_links)


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
