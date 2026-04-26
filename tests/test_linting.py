from pathlib import Path
import subprocess
import sys

from llm_wiki_maintainer.linting import LintProblem, lint_root


def test_lint_root_returns_problem_objects(wiki_root):
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"
    source_card.write_text(
        source_card.read_text(encoding="utf-8").replace(
            "- [[wiki/overview]]\n",
            "- [[wiki/missing-page]]\n",
        ),
        encoding="utf-8",
    )

    problems = lint_root(wiki_root)

    assert isinstance(problems, list)
    assert problems
    assert all(isinstance(problem, LintProblem) for problem in problems)
    assert any(
        problem.path == "wiki/sources/example-source.md"
        and "Used by" in problem.message
        for problem in problems
    )


def test_lint_script_reports_malformed_frontmatter_without_traceback(wiki_root):
    broken = wiki_root / "wiki" / "broken.md"
    broken.write_text("---\ntype: [oops\n---\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts" / "lint_llm_wiki.py"

    result = subprocess.run(
        [sys.executable, str(script), str(wiki_root)],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "malformed frontmatter" in result.stdout
    assert "Traceback" not in result.stderr


def test_lint_root_reports_missing_source_card_id(wiki_root):
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"
    source_card.write_text(
        source_card.read_text(encoding="utf-8").replace("id: SRC-1\n", ""),
        encoding="utf-8",
    )

    problems = lint_root(wiki_root)

    assert any(
        problem.path == "wiki/sources/example-source.md"
        and "missing valid id/source_id" in problem.message
        for problem in problems
    )
    assert not any(
        problem.path == "wiki/sources/example-source.md"
        and "Used by lists non-actual references" in problem.message
        for problem in problems
    )


def test_lint_root_treats_equivalent_used_by_link_targets_as_matching(wiki_root):
    source_card = wiki_root / "wiki" / "sources" / "example-source.md"
    source_card.write_text(
        source_card.read_text(encoding="utf-8").replace("[[wiki/overview]]", "[[/wiki/overview.md]]"),
        encoding="utf-8",
    )

    problems = lint_root(wiki_root)

    assert not any("Used by" in problem.message for problem in problems)
