from __future__ import annotations

from pathlib import Path

import yaml

from llm_wiki_maintainer.ingest.analysis import AnalysisArtifact
from llm_wiki_maintainer.ingest.cache import SourceManifest
from llm_wiki_maintainer.ingest.generation import GenerationArtifact
from llm_wiki_maintainer.ingest.planner import suggest_target_pages
from llm_wiki_maintainer.runtime.jobs import IngestJob
from llm_wiki_maintainer.runtime.state import RuntimeStateStore


class IngestQueue:
    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.store = RuntimeStateStore(self.root)
        self.snapshot = self.store.load()

    def enqueue(self, raw_path: Path | str) -> IngestJob:
        job = IngestJob.new(raw_path=self._raw_relative(raw_path))
        jobs = dict(self.snapshot.jobs)
        queue = list(self.snapshot.queue)
        jobs[job.id] = job
        queue.append(job.id)
        self._save(jobs, queue)
        return job

    def retry(self, job_id: str) -> IngestJob:
        if job_id not in self.snapshot.jobs:
            raise KeyError(job_id)
        jobs = dict(self.snapshot.jobs)
        queue = list(self.snapshot.queue)
        job = jobs[job_id].with_status("pending", last_error="")
        jobs[job_id] = job
        if job_id not in queue:
            queue.append(job_id)
        self._save(jobs, queue)
        return job

    def cancel(self, job_id: str) -> IngestJob:
        if job_id not in self.snapshot.jobs:
            raise KeyError(job_id)
        jobs = dict(self.snapshot.jobs)
        queue = [queued_id for queued_id in self.snapshot.queue if queued_id != job_id]
        job = jobs[job_id].with_status("cancelled", last_error="")
        jobs[job_id] = job
        self._save(jobs, queue)
        return job

    def run_next(self) -> IngestJob | None:
        if not self.snapshot.queue:
            return None

        job_id = self.snapshot.queue[0]
        pending_queue = list(self.snapshot.queue)
        jobs = dict(self.snapshot.jobs)
        running = jobs[job_id].with_status("running", attempts=jobs[job_id].attempts + 1)
        jobs[job_id] = running
        self._save(jobs, pending_queue)

        finished: IngestJob
        try:
            finished = self._execute(running)
        except Exception as exc:
            finished = running.with_status("failed", last_error=str(exc))

        jobs = dict(self.snapshot.jobs)
        jobs[job_id] = finished
        remaining_queue = [queued_id for queued_id in self.snapshot.queue if queued_id != job_id]
        self._save(jobs, remaining_queue)
        return finished

    def _execute(self, job: IngestJob) -> IngestJob:
        raw = self.root / job.raw_path
        manifest = SourceManifest.load(self.root)
        if not manifest.has_changed(raw):
            return job.with_status("skipped", last_error="")

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

    def _raw_relative(self, raw_path: Path | str) -> str:
        raw = Path(raw_path).expanduser()
        if not raw.is_absolute():
            return raw.as_posix()
        return raw.resolve().relative_to(self.root).as_posix()

    def _save(self, jobs: dict[str, IngestJob], queue: list[str]) -> None:
        self.store.save_jobs(list(jobs.values()), queue)
        self.snapshot = self.store.load()
