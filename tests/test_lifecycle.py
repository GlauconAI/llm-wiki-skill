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
