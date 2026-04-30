from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.importer import import_folder
from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


def test_import_folder_copies_nested_files_and_enqueues_jobs(tmp_path: Path):
    source = tmp_path / "source"
    (source / "nested").mkdir(parents=True)
    (source / "a.md").write_text("# A\n", encoding="utf-8")
    (source / "nested" / "b.txt").write_text("B\n", encoding="utf-8")

    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)

    imported = import_folder(source, root)

    assert len(imported) == 2
    assert (root / "raw" / "imports" / "source" / "a.md").is_file()
    assert (root / "raw" / "imports" / "source" / "nested" / "b.txt").is_file()
    assert len(IngestQueue(root).snapshot.queue) == 2


def test_import_folder_cli_reports_imported_count(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.md").write_text("# A\n", encoding="utf-8")
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    script = Path(__file__).resolve().parents[1] / "scripts" / "import_folder.py"

    result = subprocess.run(
        [sys.executable, str(script), str(source), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "imported 1 file(s)" in result.stdout
