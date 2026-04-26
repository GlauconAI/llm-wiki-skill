import pytest

from llm_wiki_maintainer.research import ResearchTask
from llm_wiki_maintainer.review import ReviewItem


def test_review_item_approve_returns_approved_copy():
    item = ReviewItem(id="rv-1", title="Need page", action="create_page", status="pending")

    approved = item.approve()

    assert approved.status == "approved"
    assert approved is not item
    assert item.status == "pending"


def test_research_task_preserves_queries():
    queries = ["market map 2026"]

    task = ResearchTask(topic="market map", queries=queries)
    queries.append("adjacent market map")

    assert task.topic == "market map"
    assert task.status == "pending"
    assert isinstance(task.queries, list)
    assert task.queries == ["market map 2026"]


def test_research_task_accepts_tuple_queries():
    task = ResearchTask(topic="market map", queries=("market map 2026", "adjacent market map"))

    assert isinstance(task.queries, list)
    assert task.queries == ["market map 2026", "adjacent market map"]


def test_research_task_rejects_non_string_topic():
    with pytest.raises(TypeError, match="topic must be a string"):
        ResearchTask(topic=123, queries=["market map 2026"])


def test_research_task_rejects_non_string_query_entries():
    with pytest.raises(TypeError, match="queries must be an iterable of strings"):
        ResearchTask(topic="market map", queries=("market map 2026", 123))
