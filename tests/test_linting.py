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
