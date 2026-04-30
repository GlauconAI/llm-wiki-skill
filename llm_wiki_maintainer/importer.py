from __future__ import annotations

from pathlib import Path
import shutil

from llm_wiki_maintainer.runtime.ingest_queue import IngestQueue


def import_folder(source_dir: Path | str, root: Path | str) -> list[Path]:
    source = Path(source_dir).resolve()
    root_path = Path(root).resolve()
    target_root = root_path / "raw" / "imports" / source.name
    imported: list[Path] = []
    queue = IngestQueue(root_path)

    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        imported.append(target)
        queue.enqueue(target)

    return imported
