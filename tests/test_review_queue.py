from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.review import ReviewItem
from llm_wiki_maintainer.review_queue import ReviewQueueStore


def test_review_queue_round_trips_items(tmp_path: Path):
    store = ReviewQueueStore(tmp_path)
    item = ReviewItem(id="rv-1", title="Need page", action="create_page", status="pending")

    store.save([item])
    loaded = store.load()

    assert len(loaded) == 1
    assert loaded[0].id == "rv-1"
    assert loaded[0].status == "pending"


def test_review_queue_imports_generation_artifact_review_items(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    artifact = root / ".llm-wiki" / "generation" / "ingest-1.yaml"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        """outputs: {}
review_items:
  - id: rv-1
    title: Need review
    action: deep_research
    status: pending
""",
        encoding="utf-8",
    )

    imported = ReviewQueueStore(root).import_generation_artifact(artifact)

    assert [item.id for item in imported] == ["rv-1"]
    assert ReviewQueueStore(root).load()[0].action == "deep_research"


def test_review_queue_approve_and_reject_update_item_status(tmp_path: Path):
    store = ReviewQueueStore(tmp_path)
    store.save([ReviewItem(id="rv-1", title="Need page", action="create_page", status="pending")])

    approved = store.approve("rv-1")
    rejected = store.reject("rv-1")

    assert approved.status == "approved"
    assert rejected.status == "rejected"


def test_review_queue_cli_lists_and_updates_items(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    (root / ".llm-wiki" / "state").mkdir(parents=True)
    ReviewQueueStore(root).save(
        [ReviewItem(id="rv-1", title="Need page", action="create_page", status="pending")]
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "review_queue.py"

    listing = subprocess.run(
        [sys.executable, str(script), "list", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    approved = subprocess.run(
        [sys.executable, str(script), "approve", "rv-1", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    shown = subprocess.run(
        [sys.executable, str(script), "show", "rv-1", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert listing.returncode == 0
    assert "rv-1 pending create_page Need page" in listing.stdout
    assert approved.returncode == 0
    assert "approved rv-1" in approved.stdout
    assert shown.returncode == 0
    assert "rv-1 approved create_page Need page" in shown.stdout


def test_review_queue_cli_imports_generation_artifact(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    artifact = root / ".llm-wiki" / "generation" / "ingest-1.yaml"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        """outputs: {}
review_items:
  - id: rv-1
    title: Need review
    action: deep_research
    status: pending
""",
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "review_queue.py"

    imported = subprocess.run(
        [sys.executable, str(script), "import", str(artifact), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    shown = subprocess.run(
        [sys.executable, str(script), "show", "rv-1", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert imported.returncode == 0
    assert "imported 1 review item(s)" in imported.stdout
    assert shown.returncode == 0
    assert "rv-1 pending deep_research Need review" in shown.stdout


def test_review_queue_cli_list_can_resolve_root_from_cwd(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    (root / ".llm-wiki" / "state").mkdir(parents=True)
    ReviewQueueStore(root).save(
        [ReviewItem(id="rv-1", title="Need page", action="create_page", status="pending")]
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "review_queue.py"

    listing = subprocess.run(
        [sys.executable, str(script), "list"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert listing.returncode == 0
    assert "rv-1 pending create_page Need page" in listing.stdout
