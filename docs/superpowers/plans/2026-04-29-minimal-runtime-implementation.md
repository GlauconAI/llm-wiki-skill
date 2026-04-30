# Minimal Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first persisted ingest runtime for `llm-wiki-maintainer`, with serial jobs, restart-safe state, artifact recording, and a CLI runner.

**Architecture:** Add a small `runtime/` package on top of the existing backend. The runtime owns persisted state and orchestration, but delegates actual ingest planning to existing modules such as `SourceManifest`, `suggest_target_pages`, `AnalysisArtifact`, and `GenerationArtifact`. The first version stays deterministic and serial: no UI, no provider integrations, no parallel workers.

**Tech Stack:** Python 3.9+, `dataclasses`, `pathlib`, `yaml` via `PyYAML`, existing `pytest` harness, existing ingest/review/research models.

---

## File Structure

- Create: `llm_wiki_maintainer/runtime/__init__.py` — package marker for runtime modules.
- Create: `llm_wiki_maintainer/runtime/jobs.py` — runtime job dataclasses, status transitions, and serialization helpers.
- Create: `llm_wiki_maintainer/runtime/state.py` — persisted queue/state storage under `.llm-wiki/state/`.
- Create: `llm_wiki_maintainer/runtime/ingest_queue.py` — serial queue orchestration using existing ingest planner and manifest.
- Create: `scripts/run_ingest_queue.py` — CLI for `enqueue`, `run`, `status`, and `retry`.
- Create: `tests/test_runtime_state.py` — persistence and restart-safety tests.
- Create: `tests/test_ingest_queue.py` — queue behavior and CLI tests.

### Task 1: Runtime Jobs and State Storage

**Files:**
- Create: `llm_wiki_maintainer/runtime/__init__.py`
- Create: `llm_wiki_maintainer/runtime/jobs.py`
- Create: `llm_wiki_maintainer/runtime/state.py`
- Test: `tests/test_runtime_state.py`

- [ ] **Step 1: Write the failing persistence tests**

```python
from pathlib import Path

from llm_wiki_maintainer.runtime.jobs import IngestJob
from llm_wiki_maintainer.runtime.state import RuntimeStateStore


def test_state_store_round_trips_jobs_and_queue(tmp_path: Path):
    store = RuntimeStateStore(tmp_path)
    job = IngestJob.new(raw_path="raw/sources/a.md")
    store.save_jobs([job], queue=[job.id])

    reloaded = RuntimeStateStore(tmp_path)
    snapshot = reloaded.load()

    assert snapshot.queue == [job.id]
    assert snapshot.jobs[job.id].raw_path == "raw/sources/a.md"
    assert snapshot.jobs[job.id].status == "pending"


def test_state_store_creates_default_empty_snapshot(tmp_path: Path):
    snapshot = RuntimeStateStore(tmp_path).load()

    assert snapshot.queue == []
    assert snapshot.jobs == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_runtime_state.py -q`
Expected: FAIL with import errors because `llm_wiki_maintainer.runtime` does not exist yet.

- [ ] **Step 3: Write minimal runtime package marker**

```python
"""Persisted runtime layer for llm-wiki-maintainer."""
```

- [ ] **Step 4: Implement job model and state snapshot**

```python
from __future__ import annotations

from dataclasses import dataclass, field, replace
from uuid import uuid4


JOB_STATUSES = {"pending", "running", "completed", "failed", "cancelled", "skipped"}


@dataclass(frozen=True)
class IngestJob:
    id: str
    raw_path: str
    status: str = "pending"
    attempts: int = 0
    analysis_artifact: str = ""
    generation_artifact: str = ""
    review_items: tuple[str, ...] = field(default_factory=tuple)
    research_tasks: tuple[str, ...] = field(default_factory=tuple)
    last_error: str = ""

    @classmethod
    def new(cls, raw_path: str) -> "IngestJob":
        return cls(id=f"ingest-{uuid4().hex[:12]}", raw_path=raw_path)

    def with_status(self, status: str, **changes: object) -> "IngestJob":
        if status not in JOB_STATUSES:
            raise ValueError(f"invalid job status: {status}")
        return replace(self, status=status, **changes)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "raw_path": self.raw_path,
            "status": self.status,
            "attempts": self.attempts,
            "analysis_artifact": self.analysis_artifact,
            "generation_artifact": self.generation_artifact,
            "review_items": list(self.review_items),
            "research_tasks": list(self.research_tasks),
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "IngestJob":
        return cls(
            id=str(data["id"]),
            raw_path=str(data["raw_path"]),
            status=str(data.get("status", "pending")),
            attempts=int(data.get("attempts", 0)),
            analysis_artifact=str(data.get("analysis_artifact", "")),
            generation_artifact=str(data.get("generation_artifact", "")),
            review_items=tuple(str(item) for item in data.get("review_items", [])),
            research_tasks=tuple(str(item) for item in data.get("research_tasks", [])),
            last_error=str(data.get("last_error", "")),
        )
```

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from llm_wiki_maintainer.runtime.jobs import IngestJob


STATE_PATH = ".llm-wiki/state/runtime-state.yaml"


@dataclass(frozen=True)
class RuntimeSnapshot:
    jobs: dict[str, IngestJob]
    queue: list[str]


class RuntimeStateStore:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.path = self.root / STATE_PATH

    def load(self) -> RuntimeSnapshot:
        if not self.path.exists():
            return RuntimeSnapshot(jobs={}, queue=[])
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        jobs = {
            job_id: IngestJob.from_dict(job_data)
            for job_id, job_data in dict(data.get("jobs", {})).items()
        }
        queue = [str(job_id) for job_id in data.get("queue", [])]
        return RuntimeSnapshot(jobs=jobs, queue=queue)

    def save_jobs(self, jobs: list[IngestJob], queue: list[str]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "jobs": {job.id: job.to_dict() for job in jobs},
            "queue": queue,
        }
        self.path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return self.path
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_runtime_state.py -q`
Expected: PASS

### Task 2: Queue Orchestration

**Files:**
- Create: `llm_wiki_maintainer/runtime/ingest_queue.py`
- Modify: `llm_wiki_maintainer/runtime/state.py`
- Test: `tests/test_ingest_queue.py`

- [ ] **Step 1: Write the failing queue tests**

```python
from pathlib import Path

from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


def test_queue_enqueues_and_persists_pending_job(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"

    queue = IngestQueue(wiki_root)
    job = queue.enqueue(raw)
    reloaded = IngestQueue(wiki_root)

    assert job.status == "pending"
    assert reloaded.snapshot.queue == [job.id]


def test_queue_run_skips_unchanged_source_after_first_run(wiki_root: Path):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    queue = IngestQueue(wiki_root)
    first = queue.enqueue(raw)
    queue.run_next()

    second = queue.enqueue(raw)
    result = queue.run_next()

    assert first.id != second.id
    assert result.status == "skipped"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_ingest_queue.py -q`
Expected: FAIL with import errors because `IngestQueue` does not exist yet.

- [ ] **Step 3: Implement queue orchestration around existing ingest helpers**

```python
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from llm_wiki_maintainer.ingest.analysis import AnalysisArtifact
from llm_wiki_maintainer.ingest.cache import SourceManifest
from llm_wiki_maintainer.ingest.generation import GenerationArtifact
from llm_wiki_maintainer.ingest.planner import suggest_target_pages
from llm_wiki_maintainer.runtime.jobs import IngestJob
from llm_wiki_maintainer.runtime.state import RuntimeSnapshot, RuntimeStateStore


class IngestQueue:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.store = RuntimeStateStore(self.root)
        self.snapshot = self.store.load()

    def enqueue(self, raw_path: Path | str) -> IngestJob:
        raw_file = Path(raw_path)
        rel = raw_file.resolve().relative_to(self.root).as_posix() if Path(raw_path).is_absolute() else Path(raw_path).as_posix()
        job = IngestJob.new(raw_path=rel)
        jobs = dict(self.snapshot.jobs)
        queue = list(self.snapshot.queue)
        jobs[job.id] = job
        queue.append(job.id)
        self._save(jobs, queue)
        return job

    def retry(self, job_id: str) -> IngestJob:
        job = self.snapshot.jobs[job_id]
        retried = job.with_status("pending", last_error="")
        jobs = dict(self.snapshot.jobs)
        queue = list(self.snapshot.queue)
        jobs[job_id] = retried
        if job_id not in queue:
            queue.append(job_id)
        self._save(jobs, queue)
        return retried

    def run_next(self) -> IngestJob | None:
        if not self.snapshot.queue:
            return None

        job_id = self.snapshot.queue[0]
        job = self.snapshot.jobs[job_id]
        jobs = dict(self.snapshot.jobs)
        queue = list(self.snapshot.queue[1:])
        running = job.with_status("running", attempts=job.attempts + 1)
        jobs[job_id] = running
        self._save(jobs, [job_id, *queue])

        try:
            finished = self._execute(running)
        except Exception as exc:
            failed = running.with_status("failed", last_error=str(exc))
            jobs[job_id] = failed
            self._save(jobs, queue)
            return failed

        jobs[job_id] = finished
        self._save(jobs, queue)
        return finished

    def _execute(self, job: IngestJob) -> IngestJob:
        raw = self.root / job.raw_path
        manifest = SourceManifest.load(self.root)
        if not manifest.has_changed(raw):
            return job.with_status("skipped")

        ranked = suggest_target_pages(raw, self.root)
        analysis = AnalysisArtifact(
            raw_path=job.raw_path,
            key_claims=[],
            target_pages=[candidate.path for candidate in ranked[:8]],
            tensions=[],
        )
        review_items = [
            {
                "id": f"{job.id}-review-targets",
                "title": f"Review ingest targets for {job.raw_path}",
                "action": "review_ingest_targets",
                "status": "pending",
            }
        ]
        generation = GenerationArtifact(outputs={}, review_items=review_items)

        analysis_path = self._write_yaml(".llm-wiki/analysis", job.id, analysis.to_dict())
        generation_path = self._write_yaml(".llm-wiki/generation", job.id, generation.to_dict())
        manifest.remember(raw)
        manifest.save(self.root)

        return job.with_status(
            "completed",
            analysis_artifact=analysis_path,
            generation_artifact=generation_path,
            review_items=tuple(item["id"] for item in review_items),
            research_tasks=tuple(),
            last_error="",
        )

    def _write_yaml(self, folder: str, job_id: str, payload: dict[str, object]) -> str:
        path = self.root / folder / f"{job_id}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def _save(self, jobs: dict[str, IngestJob], queue: list[str]) -> None:
        self.store.save_jobs(list(jobs.values()), queue)
        self.snapshot = self.store.load()
```

- [ ] **Step 4: Expand the tests to assert artifact recording**

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest tests/test_ingest_queue.py -q`
Expected: PASS

### Task 3: Runtime CLI

**Files:**
- Create: `scripts/run_ingest_queue.py`
- Test: `tests/test_ingest_queue.py`

- [ ] **Step 1: Write the failing CLI tests**

```python
import subprocess
import sys
from pathlib import Path


def test_run_ingest_queue_cli_enqueue_and_status(wiki_root):
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_ingest_queue.py::test_run_ingest_queue_cli_enqueue_and_status -q`
Expected: FAIL because `scripts/run_ingest_queue.py` does not exist.

- [ ] **Step 3: Implement the minimal CLI**

```python
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/run_ingest_queue.py <enqueue|run|status|retry> <arg> [llm-wiki-root]")
        return 2

    command = sys.argv[1]
    subject = sys.argv[2]
    root = Path(sys.argv[3]).expanduser().resolve() if len(sys.argv) > 3 else Path.cwd().resolve()
    queue = IngestQueue(root)

    if command == "enqueue":
        job = queue.enqueue(subject)
        print(f"queued ingest job {job.id} for {job.raw_path}")
        return 0
    if command == "run":
        result = queue.run_next()
        if result is None:
            print("no queued ingest jobs")
            return 0
        print(f"{result.status}: {result.id}")
        return 0
    if command == "status":
        for job_id in queue.snapshot.queue:
            job = queue.snapshot.jobs[job_id]
            print(f"{job.id} {job.status} {job.raw_path}")
        return 0
    if command == "retry":
        job = queue.retry(subject)
        print(f"retried {job.id}")
        return 0

    print(f"ERROR: unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run CLI-focused tests**

Run: `python3 -m pytest tests/test_ingest_queue.py -q`
Expected: PASS

### Task 4: Full Verification

**Files:**
- Verify: `tests/test_runtime_state.py`
- Verify: `tests/test_ingest_queue.py`
- Verify: `tests/test_ingest_cache.py`
- Verify: `tests/test_ingest_planner.py`

- [ ] **Step 1: Run runtime-only verification**

Run: `python3 -m pytest tests/test_runtime_state.py tests/test_ingest_queue.py -q`
Expected: PASS

- [ ] **Step 2: Run ingest regression verification**

Run: `python3 -m pytest tests/test_ingest_cache.py tests/test_ingest_planner.py tests/test_runtime_state.py tests/test_ingest_queue.py -q`
Expected: PASS

- [ ] **Step 3: Run full suite sanity check**

Run: `python3 -m pytest -q`
Expected: PASS
