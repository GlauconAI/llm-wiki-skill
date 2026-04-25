from llm_wiki_maintainer.config import RuntimeConfig
from llm_wiki_maintainer.wiki_io import write_text


def test_runtime_config_uses_dynamic_today():
    cfg = RuntimeConfig(root="/tmp/wiki", today="2026-04-24")
    assert cfg.today == "2026-04-24"


def test_write_text_creates_parent_directories(tmp_path):
    target = tmp_path / "wiki" / "reports" / "report.md"
    write_text(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
