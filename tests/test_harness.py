from pathlib import Path


def test_wiki_root_copies_minimal_fixture_vault(wiki_root: Path) -> None:
    assert wiki_root.exists()
    assert (wiki_root / "index.md").is_file()
    assert (wiki_root / "wiki" / "overview.md").is_file()
    assert (wiki_root / "wiki" / "sources" / "example-source.md").is_file()
    assert (wiki_root / "raw" / "sources" / "example-raw.md").is_file()
