from llm_wiki_maintainer.frontmatter import load_frontmatter


def test_load_frontmatter_supports_inline_sources():
    text = "---\ntype: concept\nsources: [SRC-1, SRC-2]\n---\nbody\n"
    doc = load_frontmatter(text)
    assert doc.data["sources"] == ["SRC-1", "SRC-2"]


def test_load_frontmatter_supports_multiline_yaml_list():
    text = "---\ntype: concept\nsources:\n  - SRC-1\n  - SRC-2\n---\nbody\n"
    doc = load_frontmatter(text)
    assert doc.data["sources"] == ["SRC-1", "SRC-2"]


def test_load_frontmatter_rejects_non_mapping():
    text = "---\n- SRC-1\n- SRC-2\n---\nbody\n"

    try:
        load_frontmatter(text)
    except ValueError as exc:
        assert "mapping" in str(exc)
    else:
        raise AssertionError("expected ValueError")
