import re
from typing import Any

import yaml

from llm_wiki_maintainer.models import FrontmatterDocument

FRONTMATTER_RE = re.compile(r"\A---(?:\r?\n)(.*?)(?:\r?\n)---(?:\r?\n|$)", re.S)


def load_frontmatter(text: str) -> FrontmatterDocument:
    if re.match(r"\A---(?:\r?\n)", text) is None:
        return FrontmatterDocument(data={}, body=text)

    match = FRONTMATTER_RE.match(text)
    if match is None:
        raise ValueError("frontmatter block is not closed")
    raw_block = match.group(1)
    body = text[match.end() :]
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
