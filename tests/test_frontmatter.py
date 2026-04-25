from llm_wiki_maintainer.frontmatter import dump_frontmatter, load_frontmatter


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


def test_dump_frontmatter_normalizes_sources_tuple_to_list():
    dumped = dump_frontmatter({"type": "concept", "sources": ("SRC-1", "SRC-2")}, "body\n")

    doc = load_frontmatter(dumped)
    assert doc.data["sources"] == ["SRC-1", "SRC-2"]
    assert doc.body == "body\n"


def test_dump_frontmatter_preserves_leading_blank_lines_in_body():
    body = "\n\nbody\n"

    dumped = dump_frontmatter({"type": "concept", "sources": ("SRC-1",)}, body)

    doc = load_frontmatter(dumped)
    assert doc.body == body


def test_load_frontmatter_rejects_unclosed_block():
    text = "---\ntype: concept\nsources: [SRC-1]\n"

    try:
        load_frontmatter(text)
    except ValueError as exc:
        assert "not closed" in str(exc)
    else:
        raise AssertionError("expected ValueError")
