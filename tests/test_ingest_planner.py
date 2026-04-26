from pathlib import Path
import subprocess
import sys

import pytest

from llm_wiki_maintainer.ingest.analysis import AnalysisArtifact
from llm_wiki_maintainer.ingest.generation import GenerationArtifact
from llm_wiki_maintainer.ingest.planner import suggest_target_pages


def test_suggest_target_pages_returns_ranked_candidates(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"

    ranked = suggest_target_pages(raw, wiki_root)

    assert isinstance(ranked, list)
    assert ranked
    assert ranked[0].path == "wiki/overview"
    assert ranked[0].title == "Overview"
    assert ranked[0].score == 5


def test_suggest_target_pages_script_reports_positive_candidates(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "suggest_target_pages.py"

    result = subprocess.run(
        [sys.executable, str(script), str(raw), str(wiki_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Suggested affected pages:" in result.stdout
    assert "No strong candidates found" not in result.stdout
    assert "[[wiki/overview|Overview]] (score: 5)" in result.stdout


def test_suggest_target_pages_script_uses_default_root_from_raw_layout(wiki_root):
    raw = wiki_root / "raw" / "sources" / "example-raw.md"
    script = Path(__file__).resolve().parents[1] / "scripts" / "suggest_target_pages.py"

    result = subprocess.run(
        [sys.executable, str(script), str(raw)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Suggested affected pages:" in result.stdout
    assert "ERROR: raw file not found" not in result.stdout
    assert "[[wiki/overview|Overview]] (score: 5)" in result.stdout


def test_suggest_target_pages_script_keeps_empty_message(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "example-raw.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("# raw\n", encoding="utf-8")
    (root / "wiki").mkdir(parents=True)
    script = Path(__file__).resolve().parents[1] / "scripts" / "suggest_target_pages.py"

    result = subprocess.run(
        [sys.executable, str(script), str(raw), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Suggested affected pages:" in result.stdout
    assert "No strong candidates found" in result.stdout


def test_suggest_target_pages_matches_short_acronyms(tmp_path):
    root = tmp_path / "llm-wiki"
    raw = root / "raw" / "sources" / "acronyms.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("AI UX DB OS API", encoding="utf-8")

    wiki = root / "wiki"
    wiki.mkdir(parents=True)
    for slug, title in [
        ("ai", "AI"),
        ("ux", "UX"),
        ("db", "DB"),
        ("os", "OS"),
        ("api", "API"),
    ]:
        (wiki / f"{slug}.md").write_text(
            f"---\ntype: concept\ntitle: {title}\n---\n\n# {title}\n{title}\n",
            encoding="utf-8",
        )

    ranked = suggest_target_pages(raw, root)

    assert {candidate.path for candidate in ranked} == {
        "wiki/ai",
        "wiki/ux",
        "wiki/db",
        "wiki/os",
        "wiki/api",
    }
    assert all(candidate.score > 0 for candidate in ranked)


def test_analysis_artifact_validates_required_fields_and_serializes():
    artifact = AnalysisArtifact(
        raw_path="raw/sources/example-raw.md",
        key_claims=["claim one"],
        target_pages=["wiki/overview"],
    )

    assert artifact.tensions == []
    assert artifact.to_dict() == {
        "raw_path": "raw/sources/example-raw.md",
        "key_claims": ["claim one"],
        "target_pages": ["wiki/overview"],
        "tensions": [],
    }


def test_analysis_artifact_rejects_non_string_raw_path():
    with pytest.raises(TypeError, match="raw_path must be a string"):
        AnalysisArtifact(
            raw_path=Path("raw/sources/example-raw.md"),
            key_claims=["claim one"],
            target_pages=["wiki/overview"],
        )


@pytest.mark.parametrize(
    ("factory", "kwargs"),
    [
        (AnalysisArtifact, {"key_claims": [], "target_pages": []}),
        (GenerationArtifact, {}),
    ],
)
def test_ingest_artifacts_reject_missing_required_fields(factory, kwargs):
    with pytest.raises(TypeError):
        factory(**kwargs)


def test_generation_artifact_validates_and_serializes():
    artifact = GenerationArtifact(
        outputs={"wiki/overview": "updated page body"},
        review_items=[{"page": "wiki/overview", "status": "review"}],
    )

    assert artifact.to_dict() == {
        "outputs": {"wiki/overview": "updated page body"},
        "review_items": [{"page": "wiki/overview", "status": "review"}],
    }


def test_generation_artifact_rejects_non_string_outputs():
    with pytest.raises(TypeError, match="outputs must be a mapping of strings to strings"):
        GenerationArtifact(outputs={"wiki/overview": 123})
