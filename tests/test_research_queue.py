from pathlib import Path

import pytest

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.research_queue import ResearchQueueStore
from llm_wiki_maintainer.research_runtime import queue_research_from_review
from llm_wiki_maintainer.review import ReviewItem
from llm_wiki_maintainer.review_queue import ReviewQueueStore


def test_research_queue_round_trips_tasks(tmp_path: Path):
    store = ResearchQueueStore(tmp_path)
    task = ResearchTask(topic="market map", queries=["market map 2026"])

    store.save([task])
    loaded = store.load()

    assert len(loaded) == 1
    assert loaded[0].topic == "market map"
    assert loaded[0].status == "pending"


def test_queue_research_from_approved_review_persists_task(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    review_store = ReviewQueueStore(root)
    review_store.save(
        [ReviewItem(id="rv-1", title="Research market map", action="deep_research", status="approved")]
    )

    task = queue_research_from_review(
        root,
        review_id="rv-1",
        topic="market map",
        queries=["market map 2026"],
    )

    assert task.topic == "market map"
    assert ResearchQueueStore(root).load()[0].topic == "market map"


def test_queue_research_from_pending_review_requires_override(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    ReviewQueueStore(root).save(
        [ReviewItem(id="rv-1", title="Research market map", action="deep_research", status="pending")]
    )

    with pytest.raises(PermissionError, match="review item must be approved"):
        queue_research_from_review(
            root,
            review_id="rv-1",
            topic="market map",
            queries=["market map 2026"],
        )

    task = queue_research_from_review(
        root,
        review_id="rv-1",
        topic="market map",
        queries=["market map 2026"],
        override=True,
    )

    assert task.status == "pending"


def test_queue_research_requires_deep_research_action_without_override(tmp_path: Path):
    root = tmp_path / "llm-wiki"
    ReviewQueueStore(root).save(
        [ReviewItem(id="rv-1", title="Create page", action="create_page", status="approved")]
    )

    with pytest.raises(PermissionError, match="review item action must be deep_research"):
        queue_research_from_review(
            root,
            review_id="rv-1",
            topic="market map",
            queries=["market map 2026"],
        )

    task = queue_research_from_review(
        root,
        review_id="rv-1",
        topic="market map",
        queries=["market map 2026"],
        override=True,
    )

    assert task.topic == "market map"


def test_research_queue_mark_in_progress_and_completed(tmp_path: Path):
    store = ResearchQueueStore(tmp_path)
    store.save([ResearchTask(topic="market map", queries=["market map 2026"])])

    started = store.update_status("market map", "in_progress")
    finished = store.update_status("market map", "completed")

    assert started.status == "in_progress"
    assert finished.status == "completed"
