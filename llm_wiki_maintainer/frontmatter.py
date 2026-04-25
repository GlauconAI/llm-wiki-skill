from typing import Any

import yaml

from llm_wiki_maintainer.models import FrontmatterDocument


def load_frontmatter(text: str) -> FrontmatterDocument:
    if not text.startswith("---\n"):
        return FrontmatterDocument(data={}, body=text)

    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError("frontmatter block is not closed")
    _, raw_block, body = parts
    data = yaml.safe_load(raw_block) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must decode to a mapping")
    return FrontmatterDocument(data=data, body=body)


def dump_frontmatter(data: dict[str, Any], body: str) -> str:
    normalized = dict(data)
    if isinstance(normalized.get("sources"), tuple):
        normalized["sources"] = list(normalized["sources"])
    return (
        "---\n"
        + yaml.safe_dump(normalized, sort_keys=False).strip()
        + "\n---\n"
        + body
    )
