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


def test_update_used_by_script_skips_malformed_frontmatter_without_traceback(wiki_root):
    broken = wiki_root / "wiki" / "broken.md"
    broken.write_text("---\ntype: topic\nsources: [SRC-1]\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "update_used_by.py"

    result = subprocess.run(
        [sys.executable, str(script), str(wiki_root)],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Traceback" not in result.stderr
