from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_queue import ResearchQueueStore
from llm_wiki_maintainer.research_runtime import SearchHit, execute_next_research
from llm_wiki_maintainer.review import ReviewItem
from llm_wiki_maintainer.review_queue import ReviewQueueStore
from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


class FakeSearchProvider:
    def search(self, query: str) -> list[SearchHit]:
        return [
            SearchHit(
                title=f"Result for {query}",
                url=f"https://example.com/{query.replace(' ', '-')}",
                snippet=f"Snippet for {query}",
            )
        ]


def test_execute_next_research_writes_raw_file_and_enqueues_ingest(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    ResearchQueueStore(root).save(
        [ResearchTask(topic="market map", queries=["market map 2026"])]
    )

    task, raw_path = execute_next_research(root, FakeSearchProvider())

    assert task.status == "completed"
    assert raw_path.is_file()
    assert "market-map" in raw_path.name
    queued = IngestQueue(root).snapshot.queue
    assert queued


def test_research_execution_can_be_seeded_from_approved_review(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    ReviewQueueStore(root).save(
        [ReviewItem(id="rv-1", title="Research market map", action="deep_research", status="approved")]
    )

    ResearchQueueStore(root).enqueue(ResearchTask(topic="market map", queries=["market map 2026"]))
    task, raw_path = execute_next_research(root, FakeSearchProvider())

    assert task.topic == "market map"
    assert raw_path.exists()


def test_run_research_queue_cli_executes_next_task(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    ResearchQueueStore(root).save(
        [ResearchTask(topic="market map", queries=["market map 2026"])]
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_research_queue.py"

    result = subprocess.run(
        [sys.executable, str(script), "run", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "completed research task: market map" in result.stdout
