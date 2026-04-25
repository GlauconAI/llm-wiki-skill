from datetime import date
from pathlib import Path

import llm_wiki_maintainer.config as config_module
from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.wiki_io import write_text


def test_runtime_config_uses_dynamic_today(monkeypatch):
    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 24)

    monkeypatch.setattr(config_module, "date", FakeDate)

    cfg = RuntimeConfig.from_root("~/tmp/wiki")
    assert cfg.root == Path("~/tmp/wiki").expanduser()
    assert cfg.today == "2026-04-24"


def test_write_text_creates_parent_directories(tmp_path):
    target = tmp_path / "wiki" / "reports" / "report.md"
    write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
