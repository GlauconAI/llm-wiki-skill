from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_queue import ResearchQueueStore


def test_source_adapters_script_reports_registry_and_statuses(wiki_root: Path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "source_adapters.py"

    result = subprocess.run(
        [sys.executable, str(script), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "local_file mode=file raw=raw/sources" in result.stdout
    assert "status research_task env_unavailable" in result.stdout


def test_import_folder_script_uses_adapter_status_output(tmp_path: Path):
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
    assert "folder_import: ready" in result.stdout
    assert "imported 1 file(s)" in result.stdout


def test_run_research_queue_script_still_executes_via_adapter_layer(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    ResearchQueueStore(root).save([ResearchTask(topic="market map", queries=["market map 2026"])])
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_research_queue.py"

    result = subprocess.run(
        [sys.executable, str(script), "run", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "completed research task: market map" in result.stdout
