from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.ingest.planner import suggest_target_pages


def test_suggest_target_pages_returns_ranked_candidates(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"

    ranked = suggest_target_pages(raw, wiki_root)

    assert isinstance(ranked, list)
    assert ranked
    assert ranked[0].path == "wiki/overview"
    assert ranked[0].title == "Overview"
    assert ranked[0].score == 5


def test_suggest_target_pages_script_reports_positive_candidates(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "suggest_target_pages.py"

    result = subprocess.run(
        [sys.executable, str(script), str(raw), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Suggested affected pages:" in result.stdout
    assert "No strong candidates found" not in result.stdout
    assert "[[wiki/overview|Overview]] (score: 5)" in result.stdout


def test_suggest_target_pages_script_keeps_empty_message(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "example-raw.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# raw\n", encoding="utf-8")
    (root / "wiki").mkdir(parents=True)
    script = Path(__file__).resolve().parents[1] / "scripts" / "suggest_target_pages.py"

    result = subprocess.run(
        [sys.executable, str(script), str(raw), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Suggested affected pages:" in result.stdout
    assert "No strong candidates found" in result.stdout
