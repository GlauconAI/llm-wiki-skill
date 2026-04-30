from pathlib import Path
import subprocess
import sys

import pytest

from llm_wiki_maintainer.registry import WikiRegistry, resolve_wiki_root


def test_registry_can_register_list_and_activate_roots(tmp_path: Path):
    registry_path = tmp_path / "registry.yaml"
    root_a = tmp_path / "wiki-a"
    root_b = tmp_path / "wiki-b"
    (root_a / "raw").mkdir(parents=True)
    (root_a / "wiki").mkdir(parents=True)
    (root_b / "raw").mkdir(parents=True)
    (root_b / "wiki").mkdir(parents=True)

    registry = WikiRegistry(registry_path)
    registry.register("alpha", root_a)
    registry.register("beta", root_b)
    active = registry.activate("beta")

    entries = registry.list()

    assert active.name == "beta"
    assert [entry.name for entry in entries] == ["alpha", "beta"]
    assert registry.active().path == root_b.resolve()


def test_registry_reregister_preserves_active_flag_for_same_name(tmp_path: Path):
    registry_path = tmp_path / "registry.yaml"
    root_a = tmp_path / "wiki-a"
    root_b = tmp_path / "wiki-b"
    (root_a / "raw").mkdir(parents=True)
    (root_a / "wiki").mkdir(parents=True)
    (root_b / "raw").mkdir(parents=True)
    (root_b / "wiki").mkdir(parents=True)

    registry = WikiRegistry(registry_path)
    registry.register("alpha", root_a)
    registry.activate("alpha")
    registry.register("alpha", root_b)

    active = registry.active()

    assert active.name == "alpha"
    assert active.path == root_b.resolve()


def test_resolve_wiki_root_prefers_explicit_then_cwd_then_active_registry(tmp_path: Path):
    registry_path = tmp_path / "registry.yaml"
    root_a = tmp_path / "wiki-a"
    root_b = tmp_path / "wiki-b"
    cwd_root = tmp_path / "cwd-wiki"
    for root in [root_a, root_b, cwd_root]:
        (root / "raw").mkdir(parents=True)
        (root / "wiki").mkdir(parents=True)

    registry = WikiRegistry(registry_path)
    registry.register("alpha", root_a)
    registry.register("beta", root_b)
    registry.activate("beta")

    assert resolve_wiki_root(root=root_a, cwd=tmp_path, registry=registry) == root_a.resolve()
    assert resolve_wiki_root(root=None, cwd=cwd_root, registry=registry) == cwd_root.resolve()
    assert resolve_wiki_root(root=None, cwd=tmp_path, registry=registry) == root_b.resolve()


def test_resolve_wiki_root_raises_when_no_explicit_cwd_or_active_registry(tmp_path: Path):
    registry = WikiRegistry(tmp_path / "registry.yaml")

    with pytest.raises(ValueError):
        resolve_wiki_root(root=None, cwd=tmp_path, registry=registry)


def test_wiki_registry_script_manages_entries(tmp_path: Path):
    registry_path = tmp_path / "registry.yaml"
    root = tmp_path / "wiki-a"
    (root / "raw").mkdir(parents=True)
    (root / "wiki").mkdir(parents=True)
    script = Path(__file__).resolve().parents[1] / "scripts" / "wiki_registry.py"

    add = subprocess.run(
        [sys.executable, str(script), "add", "alpha", str(root), str(registry_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    activate = subprocess.run(
        [sys.executable, str(script), "activate", "alpha", str(registry_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    listed = subprocess.run(
        [sys.executable, str(script), "list", str(registry_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert add.returncode == 0
    assert "registered alpha" in add.stdout
    assert activate.returncode == 0
    assert "active alpha" in activate.stdout
    assert listed.returncode == 0
    assert "* alpha" in listed.stdout


def test_wiki_status_script_can_resolve_root_from_cwd(wiki_root: Path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "wiki_status.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=wiki_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert f"root: {wiki_root.resolve()}" in result.stdout


def test_query_context_script_can_resolve_root_from_cwd(wiki_root: Path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "query_context.py"

    result = subprocess.run(
        [sys.executable, str(script), "example"],
        cwd=wiki_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Query: example" in result.stdout


def test_create_digest_script_can_resolve_root_from_cwd(wiki_root: Path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "create_digest.py"

    result = subprocess.run(
        [sys.executable, str(script), "example", "Example Digest"],
        cwd=wiki_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "created digest" in result.stdout
