from pathlib import Path
import subprocess
import sys


def test_status_and_digest_scripts_run_successfully(wiki_root: Path):
    status_script = Path(__file__).resolve().parents[1] / "scripts" / "wiki_status.py"
    digest_script = Path(__file__).resolve().parents[1] / "scripts" / "create_digest.py"

    status = subprocess.run(
        [sys.executable, str(status_script), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    digest = subprocess.run(
        [sys.executable, str(digest_script), "example", str(wiki_root), "Example Digest"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert status.returncode == 0
    assert "pages: 3" in status.stdout
    assert digest.returncode == 0
    assert "created digest" in digest.stdout
    assert (wiki_root / "wiki" / "digests" / "example-digest.md").is_file()


def test_save_query_script_persists_query_note(wiki_root: Path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "save_query.py"

    result = subprocess.run(
        [sys.executable, str(script), "example", str(wiki_root), "Example Saved Query"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "saved query" in result.stdout
    assert (wiki_root / "wiki" / "queries" / "example-saved-query.md").is_file()


def test_delete_and_crystallize_scripts_run_successfully(wiki_root: Path):
    delete_script = Path(__file__).resolve().parents[1] / "scripts" / "delete_source.py"
    crystal_script = Path(__file__).resolve().parents[1] / "scripts" / "crystallize_note.py"
    raw = wiki_root / "raw" / "sources" / "example-raw.md"

    delete_preview = subprocess.run(
        [sys.executable, str(delete_script), str(raw), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    crystal = subprocess.run(
        [
            sys.executable,
            str(crystal_script),
            "Working Insight",
            "A compressed synthesis.",
            str(wiki_root),
            "SRC-1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert delete_preview.returncode == 0
    assert "applied: False" in delete_preview.stdout
    assert crystal.returncode == 0
    assert "created crystal" in crystal.stdout
    assert (wiki_root / "wiki" / "crystallized" / "working-insight.md").is_file()
