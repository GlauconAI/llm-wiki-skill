from pathlib import Path
import shutil

import pytest


@pytest.fixture
def wiki_root(tmp_path: Path) -> Path:
    src = Path(__file__).parent / "fixtures" / "wiki_minimal"
    dst = tmp_path / "llm-wiki"
    shutil.copytree(src, dst)
    return dst


@pytest.fixture
def healthy_wiki_root(tmp_path: Path) -> Path:
    src = Path(__file__).parent / "fixtures" / "wiki_healthy"
    dst = tmp_path / "llm-wiki"
    shutil.copytree(src, dst)
    return dst
