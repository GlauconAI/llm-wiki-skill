from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


def test_queue_enqueues_and_persists_pending_job(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"

    queue = IngestQueue(wiki_root)
    job = queue.enqueue(raw)
    reloaded = IngestQueue(wiki_root)

    assert job.status == "pending"
    assert reloaded.snapshot.queue == [job.id]


def test_queue_run_records_artifacts_and_review_handoff(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    queue = IngestQueue(wiki_root)
    job = queue.enqueue(raw)

    result = queue.run_next()

    assert result is not None
    assert result.status == "completed"
    assert result.analysis_artifact.startswith(".llm-wiki/analysis/")
    assert result.generation_artifact.startswith(".llm-wiki/generation/")
    assert result.review_items == (f"{job.id}-review-targets",)


def test_queue_run_skips_unchanged_source_after_first_run(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    queue = IngestQueue(wiki_root)
    queue.enqueue(raw)
    queue.run_next()

    second = queue.enqueue(raw)
    result = queue.run_next()

    assert result is not None
    assert result.id == second.id
    assert result.status == "skipped"


def test_run_ingest_queue_cli_enqueue_and_status(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_ingest_queue.py"

    enqueue = subprocess.run(
        [sys.executable, str(script), "enqueue", str(raw), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    status = subprocess.run(
        [sys.executable, str(script), "status", str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert enqueue.returncode == 0
    assert "queued ingest job" in enqueue.stdout
    assert status.returncode == 0
    assert "pending" in status.stdout


def test_queue_retry_requeues_failed_job_and_completes_after_fix(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw" / "sources").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    missing = root / "raw" / "sources" / "missing.md"

    queue = IngestQueue(root)
    job = queue.enqueue(missing)
    failed = queue.run_next()

    assert failed is not None
    assert failed.status == "failed"
    assert failed.last_error

    missing.write_text("# Missing\n", encoding="utf-8")
    retried = queue.retry(job.id)
    completed = queue.run_next()

    assert retried.status == "pending"
    assert completed is not None
    assert completed.id == job.id
    assert completed.status == "completed"


def test_run_ingest_queue_cli_retry_requeues_failed_job(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw" / "sources").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    raw = root / "raw" / "sources" / "missing.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_ingest_queue.py"

    enqueue = subprocess.run(
        [sys.executable, str(script), "enqueue", str(raw), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    job_id = enqueue.stdout.split()[3]
    run = subprocess.run(
        [sys.executable, str(script), "run", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert run.returncode == 0
    assert "failed:" in run.stdout

    retried = subprocess.run(
        [sys.executable, str(script), "retry", job_id, str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    status = subprocess.run(
        [sys.executable, str(script), "status", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert retried.returncode == 0
    assert f"retried {job_id}" in retried.stdout
    assert "pending" in status.stdout


def test_queue_cancel_marks_job_cancelled_and_removes_it_from_queue(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    queue = IngestQueue(wiki_root)
    job = queue.enqueue(raw)

    cancelled = queue.cancel(job.id)

    assert cancelled.status == "cancelled"
    assert queue.snapshot.queue == []
    assert queue.snapshot.jobs[job.id].status == "cancelled"


def test_run_ingest_queue_cli_cancel_updates_job_status(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_ingest_queue.py"

    enqueue = subprocess.run(
        [sys.executable, str(script), "enqueue", str(raw), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    job_id = enqueue.stdout.split()[3]

    cancelled = subprocess.run(
        [sys.executable, str(script), "cancel", job_id, str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    status = subprocess.run(
        [sys.executable, str(script), "status", str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert cancelled.returncode == 0
    assert f"cancelled {job_id}" in cancelled.stdout
    assert job_id not in status.stdout


def test_run_ingest_queue_cli_status_can_resolve_root_from_cwd(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_ingest_queue.py"

    subprocess.run(
        [sys.executable, str(script), "enqueue", str(raw)],
        cwd=wiki_root,
        capture_output=True,
        text=True,
        check=False,
    )
    status = subprocess.run(
        [sys.executable, str(script), "status"],
        cwd=wiki_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert status.returncode == 0
    assert "pending" in status.stdout
