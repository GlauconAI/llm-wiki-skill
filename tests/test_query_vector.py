from dataclasses import dataclass
from pathlib import Path

from llm_wiki_maintainer.query.runtime import query_runtime
from llm_wiki_maintainer.query.vector import VectorMatch


@dataclass
class FakeVectorProvider:
    match_path: str

    def search(self, query: str, root: Path, limit: int = 8) -> list[VectorMatch]:
        return [
            VectorMatch(
                path=self.match_path,
                score=9.0,
                excerpt=f"Vector result for {query}",
            )
        ]


def test_query_runtime_merges_vector_matches_with_lexical_results(wiki_root):
    page = wiki_root / "wiki" / "vector-only.md"
    page.write_text(
        """---
type: concept
title: Vector Only
---

Body without the direct query term.
""",
        encoding="utf-8",
    )

    result = query_runtime(
        "semantic bridge",
        wiki_root,
        limit=5,
        max_chars=160,
        vector_provider=FakeVectorProvider("wiki/vector-only"),
    )

    assert result.package.pages
    assert result.package.pages[0].title == "Vector Only"
    assert "Vector result for semantic bridge" in result.package.context
