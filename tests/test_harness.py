from datetime import date
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest

def test_wiki_root_copies_minimal_fixture_vault(wiki_root: Path) -> None:
    assert wiki_root.exists()
    assert (wiki_root / "index.md").is_file()
    assert (wiki_root / "wiki" / "overview.md").is_file()
    assert (wiki_root / "wiki" / "sources" / "example-source.md").is_file()
    assert (wiki_root / "raw" / "sources" / "example-raw.md").is_file()


def _load_script_module(script_name: str):
    script_path = Path(__file__).resolve().parents[1] / "scripts" / script_name
    spec = spec_from_file_location(script_name.removesuffix(".py"), script_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("script_name", "suffix"),
    [
        ("create_audit_report.py", ".md"),
        ("create_ingest_report.py", "-ingest.md"),
    ],
)
def test_report_scaffolders_create_reports_dir_and_slugify_titles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    script_name: str,
    suffix: str,
) -> None:
    root = tmp_path / "llm-wiki"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)

    module = _load_script_module(script_name)

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 24)

    monkeypatch.setattr(module, "date", FakeDate)
    monkeypatch.setattr(
        sys,
        "argv",
        [script_name, "Audit / Closure", str(root)],
    )

    assert module.main() == 0
    report_path = root / "wiki" / "reports" / f"2026-04-24-audit-closure{suffix}"
    assert report_path.is_file()
    assert report_path.parent == root / "wiki" / "reports"
