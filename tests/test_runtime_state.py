from pathlib import Path
import yaml

from llm_wiki_maintainer.runtime.jobs import IngestJob
from llm_wiki_maintainer.runtime.state import RuntimeStateStore


def test_state_store_round_trips_jobs_and_queue(tmp_path: Path):
    store = RuntimeStateStore(tmp_path)
    job = IngestJob.new(raw_path="raw/sources/a.md")

    store.save_jobs([job], queue=[job.id])

    snapshot = RuntimeStateStore(tmp_path).load()

    assert snapshot.queue == [job.id]
    assert snapshot.jobs[job.id].raw_path == "raw/sources/a.md"
    assert snapshot.jobs[job.id].status == "pending"


def test_state_store_creates_default_empty_snapshot(tmp_path: Path):
    snapshot = RuntimeStateStore(tmp_path).load()

    assert snapshot.queue == []
    assert snapshot.jobs == {}


def test_state_store_recovers_running_jobs_to_pending_on_load(tmp_path: Path):
    job = IngestJob.new(raw_path="raw/sources/a.md").with_status("running", attempts=1)
    path = RuntimeStateStore(tmp_path).save_jobs([job], queue=[job.id])

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["jobs"][job.id]["status"] == "running"

    snapshot = RuntimeStateStore(tmp_path).load()

    assert snapshot.jobs[job.id].status == "pending"
    assert snapshot.jobs[job.id].attempts == 1
