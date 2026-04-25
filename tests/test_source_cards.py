from datetime import date
from pathlib import Path
import subprocess
import sys

import llm_wiki_maintainer.config as config_module
from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.frontmatter import load_frontmatter
from llm_wiki_maintainer.source_cards import create_source_card
from llm_wiki_maintainer.wiki_io import write_text


def test_runtime_config_uses_dynamic_today(monkeypatch):
    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 24)

    monkeypatch.setattr(config_module, "date", FakeDate)

    cfg = RuntimeConfig.from_root("~/tmp/wiki")
    assert cfg.root == Path("~/tmp/wiki").expanduser()
    assert cfg.today == "2026-04-24"


def test_write_text_creates_parent_directories(tmp_path):
    target = tmp_path / "wiki" / "reports" / "report.md"
    write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"


def test_create_source_card_avoids_duplicate_when_location_matches(wiki_root):
    raw_file = wiki_root / "raw" / "sources" / "example-raw.md"
    result = create_source_card(raw_file, wiki_root, today="2026-04-24")

    assert result.status == "exists"


def test_create_source_card_detects_duplicate_with_unaliased_location(wiki_root):
    card = wiki_root / "wiki" / "sources" / "example-source.md"
    card.write_text(
        """---
type: source
id: SRC-1
title: Example Source
---

# Source: Example Source

## Location
[[raw/sources/example-raw]]

## Type
md

## Coverage
- Minimal fixture coverage.

## Used by
- [[wiki/overview]]

## Key Sections
- Minimal fixture section.

## Notes
- Minimal source card for lint and harness coverage.
""",
        encoding="utf-8",
    )
    raw_file = wiki_root / "raw" / "sources" / "example-raw.md"

    result = create_source_card(raw_file, wiki_root, today="2026-04-24")

    assert result.status == "exists"


def test_create_source_card_detects_duplicate_with_normalized_location_target(wiki_root):
    card = wiki_root / "wiki" / "sources" / "example-source.md"
    card.write_text(
        """---
type: source
id: SRC-1
title: Example Source
---

# Source: Example Source

## Location
[[/raw/sources/example-raw.md]]

## Type
md

## Coverage
- Minimal fixture coverage.

## Used by
- [[wiki/overview]]

## Key Sections
- Minimal fixture section.

## Notes
- Minimal source card for lint and harness coverage.
""",
        encoding="utf-8",
    )
    raw_file = wiki_root / "raw" / "sources" / "example-raw.md"

    result = create_source_card(raw_file, wiki_root, today="2026-04-24")

    assert result.status == "exists"


def test_create_source_card_writes_today_in_metadata(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "new-note.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# New Note\n", encoding="utf-8")

    result = create_source_card(raw, root, today="2026-04-24")
    document = load_frontmatter(result.path.read_text(encoding="utf-8"))

    assert result.path.name == "new-note.md"
    assert document.data["created"] == "2026-04-24"


def test_create_source_card_writes_parseable_frontmatter_for_colon_title(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "plato-republic.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("---\ntitle: 'Plato: Republic'\n---\n# Plato: Republic\n", encoding="utf-8")

    result = create_source_card(raw, root, today="2026-04-24")
    document = load_frontmatter(result.path.read_text(encoding="utf-8"))

    assert document.data["title"] == "Plato: Republic"
    assert document.data["created"] == "2026-04-24"


def test_create_source_card_cli_runs_from_repo_root(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "cli-note.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# CLI Note\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "create_source_card.py"

    result = subprocess.run(
        [sys.executable, str(script), str(raw), str(root)],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "created:" in result.stdout


def test_create_source_card_cli_accepts_relative_raw_path(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "relative-note.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# Relative Note\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "create_source_card.py"

    result = subprocess.run(
        [sys.executable, str(script), "raw/sources/relative-note.md", str(root)],
        cwd=root,
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "created:" in result.stdout


def test_create_source_card_cli_accepts_dot_root_argument(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "dot-root-note.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# Dot Root Note\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "create_source_card.py"

    result = subprocess.run(
        [sys.executable, str(script), "raw/sources/dot-root-note.md", "."],
        cwd=root,
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "created:" in result.stdout
