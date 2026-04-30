#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
VENDOR_DIR = ROOT_DIR / ".vendor"
if VENDOR_DIR.exists() and str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue
from llm_wiki_maintainer.registry import resolve_wiki_root


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: python3 scripts/run_ingest_queue.py "
            "<enqueue|run|status|retry|cancel> <raw-file|job-id|llm-wiki-root> [llm-wiki-root]"
        )
        return 2

    command = sys.argv[1]

    if command in {"status", "run"}:
        root_arg = sys.argv[2] if len(sys.argv) > 2 else None
        try:
            root = resolve_wiki_root(root=root_arg)
        except ValueError:
            print(
                "Usage: python3 scripts/run_ingest_queue.py "
                "<enqueue|run|status|retry|cancel> <raw-file|job-id|llm-wiki-root> [llm-wiki-root]"
            )
            return 2
        queue = IngestQueue(root)
        if command == "status":
            for job_id in queue.snapshot.queue:
                job = queue.snapshot.jobs[job_id]
                print(f"{job.id} {job.status} {job.raw_path}")
            return 0

        result = queue.run_next()
        if result is None:
            print("no queued ingest jobs")
            return 0
        print(f"{result.status}: {result.id}")
        return 0

    if len(sys.argv) < 3:
        print(
            "Usage: python3 scripts/run_ingest_queue.py "
            "<enqueue|retry|cancel> <raw-file|job-id> [llm-wiki-root]"
        )
        return 2

    subject = sys.argv[2]
    root_arg = sys.argv[3] if len(sys.argv) > 3 else None
    try:
        root = resolve_wiki_root(root=root_arg)
    except ValueError:
        print(
            "Usage: python3 scripts/run_ingest_queue.py "
            "<enqueue|retry|cancel> <raw-file|job-id> [llm-wiki-root]"
        )
        return 2
    queue = IngestQueue(root)

    if command == "enqueue":
        job = queue.enqueue(subject)
        print(f"queued ingest job {job.id} for {job.raw_path}")
        return 0
    if command == "retry":
        job = queue.retry(subject)
        print(f"retried {job.id}")
        return 0
    if command == "cancel":
        job = queue.cancel(subject)
        print(f"cancelled {job.id}")
        return 0

    print(f"ERROR: unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
