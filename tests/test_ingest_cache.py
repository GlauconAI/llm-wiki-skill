from llm_wiki_maintainer.ingest.cache import MANIFEST_PATH, SourceManifest


def test_manifest_marks_source_changed_on_first_seen(tmp_path):
    raw = tmp_path / "a.md"
    raw.write_text("hello", encoding="utf-8")

    manifest = SourceManifest.empty()

    assert manifest.has_changed(raw) is True


def test_manifest_round_trips_yaml_and_detects_unchanged_file(tmp_path):
    raw = tmp_path / "a.md"
    raw.write_text("hello", encoding="utf-8")

    manifest = SourceManifest.empty()
    manifest.remember(raw)
    manifest.save(tmp_path)

    loaded = SourceManifest.load(tmp_path)

    assert MANIFEST_PATH == ".llm-wiki/ingest-manifest.yaml"
    assert loaded.has_changed(raw) is False

    raw.write_text("hello again", encoding="utf-8")

    assert loaded.has_changed(raw) is True
