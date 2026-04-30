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
    def __init__(self, root: Path | str):
        self.root = Path(root).resolve()
        self.path = self.root / STATE_PATH

    def load(self) -> RuntimeSnapshot:
        if not self.path.exists():
            return RuntimeSnapshot(jobs={}, queue=[])

        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError("runtime state must decode to a mapping")

        raw_jobs = data.get("jobs", {})
        raw_queue = data.get("queue", [])
        if not isinstance(raw_jobs, dict):
            raise ValueError("runtime state jobs must be a mapping")
        if not isinstance(raw_queue, list):
            raise ValueError("runtime state queue must be a list")

        jobs = {
            str(job_id): IngestJob.from_dict(dict(job_data))
            for job_id, job_data in raw_jobs.items()
        }
        jobs = {
            job_id: (
                job.with_status("pending")
                if job.status == "running"
                else job
            )
            for job_id, job in jobs.items()
        }
        queue = [str(job_id) for job_id in raw_queue]
        return RuntimeSnapshot(jobs=jobs, queue=queue)

    def save_jobs(self, jobs: list[IngestJob], queue: list[str]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "jobs": {job.id: job.to_dict() for job in jobs},
            "queue": queue,
        }
        self.path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return self.path
