from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.references import compute_used_by


def test_compute_used_by_supports_multiline_sources(wiki_root):
    page = wiki_root / "wiki" / "topic-a.md"
    page.write_text(
        "---\n"
        "type: topic\n"
        "sources:\n"
        "  - src-1\n"
        "---\n"
        "# Topic\n",
        encoding="utf-8",
    )

    mapping = compute_used_by(wiki_root)

    assert mapping["wiki/sources/example-source.md"] == {
        "wiki/overview",
        "wiki/topic-a",
    }


def test_update_used_by_script_skips_malformed_frontmatter_without_traceback(wiki_root):
    broken = wiki_root / "wiki" / "broken.md"
    broken.write_text("---\ntype: [oops\n---\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "update_used_by.py"

    result = subprocess.run(
        [sys.executable, str(script), str(wiki_root)],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "malformed frontmatter" in result.stdout
    assert "Traceback" not in result.stderr


def test_update_used_by_script_fails_when_source_card_id_is_missing(wiki_root):
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"
    source_card.write_text(
        source_card.read_text(encoding="utf-8").replace("id: SRC-1\n", ""),
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "update_used_by.py"

    result = subprocess.run(
        [sys.executable, str(script), str(wiki_root)],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "wiki/sources/example-source.md" in result.stdout
    assert "Traceback" not in result.stderr


def test_update_used_by_script_fails_when_source_card_ids_are_duplicated(wiki_root):
    duplicate = wiki_root / "wiki" / "sources" / "duplicate-source.md"
    duplicate.write_text(
        """---
type: source
id: SRC-1
title: Duplicate Source
---

# Source: Duplicate Source

## Location
[[raw/sources/example-raw]]

## Type
md

## Coverage
- Duplicate coverage.

## Used by
- [[wiki/overview]]

## Key Sections
- Duplicate section.

## Notes
- Duplicate source card for testing.
""",
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "update_used_by.py"

    result = subprocess.run(
        [sys.executable, str(script), str(wiki_root)],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "wiki/sources/duplicate-source.md" in result.stdout
    assert "Traceback" not in result.stderr
