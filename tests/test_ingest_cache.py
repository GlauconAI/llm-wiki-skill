import yaml
import pytest

from llm_wiki_maintainer.ingest.cache import MANIFEST_PATH, SourceManifest


def test_manifest_marks_missing_source_changed_without_raising(tmp_path):
    manifest = SourceManifest.empty(tmp_path)
    missing = tmp_path / "raw" / "sources" / "gone.md"

    assert manifest.has_changed(missing) is True


def test_manifest_normalizes_keys_relative_to_wiki_root(tmp_path):
    raw = tmp_path / "raw" / "sources" / "a.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("hello", encoding="utf-8")

    manifest = SourceManifest.empty(tmp_path)
    manifest.remember(raw.relative_to(tmp_path))
    manifest.save(tmp_path)

    saved = yaml.safe_load((tmp_path / MANIFEST_PATH).read_text(encoding="utf-8"))

    assert list(saved["hashes"]) == ["raw/sources/a.md"]

    loaded = SourceManifest.load(tmp_path)

    assert loaded.has_changed(raw) is False
    assert loaded.has_changed(raw.relative_to(tmp_path)) is False


def test_manifest_round_trips_no_root_save_then_load_with_root(tmp_path):
    raw = tmp_path / "raw" / "sources" / "a.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("hello", encoding="utf-8")

    manifest = SourceManifest.empty()
    manifest.remember(raw)
    manifest.save(tmp_path)

    saved = yaml.safe_load((tmp_path / MANIFEST_PATH).read_text(encoding="utf-8"))

    assert list(saved["hashes"]) == ["raw/sources/a.md"]

    loaded = SourceManifest.load(tmp_path)

    assert loaded.has_changed(raw) is False
    assert loaded.has_changed(raw.relative_to(tmp_path)) is False


def test_manifest_save_updates_instance_root_for_follow_up_calls(tmp_path):
    raw = tmp_path / "raw" / "sources" / "a.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("hello", encoding="utf-8")

    manifest = SourceManifest.empty()
    manifest.remember(raw)
    manifest.save(tmp_path)

    assert manifest.root == tmp_path.resolve()
    assert manifest.has_changed(raw.relative_to(tmp_path)) is False

    manifest.remember(raw.relative_to(tmp_path))

    assert manifest.has_changed(raw) is False


def test_manifest_load_rejects_non_mapping_yaml(tmp_path):
    manifest_path = tmp_path / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("- not a mapping\n- still not a mapping\n", encoding="utf-8")

    with pytest.raises(ValueError, match="ingest manifest must decode to a mapping"):
        SourceManifest.load(tmp_path)
