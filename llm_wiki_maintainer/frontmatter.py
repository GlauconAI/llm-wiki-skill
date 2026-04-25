from typing import Any

from llm_wiki_maintainer.models import FrontmatterDocument


def load_frontmatter(text: str) -> FrontmatterDocument:
    if not text.startswith("---\n"):
        return FrontmatterDocument(data={}, body=text)

    lines = text.splitlines(keepends=True)
    if not lines or lines[0] != "---\n":
        return FrontmatterDocument(data={}, body=text)

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line in ("---\n", "---\r\n", "---"):
            closing_index = index
            break
    if closing_index is None:
        raise ValueError("frontmatter block is not closed")

    raw_block = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1 :])
    data = _parse_frontmatter_block(raw_block)
    return FrontmatterDocument(data=data, body=body)


def dump_frontmatter(data: dict[str, Any], body: str) -> str:
    normalized = dict(data)
    if isinstance(normalized.get("sources"), tuple):
        normalized["sources"] = list(normalized["sources"])

    rendered = [_render_frontmatter_value(key, normalized[key]) for key in normalized]
    return "---\n" + "\n".join(rendered) + "\n---\n" + body.lstrip("\n")


def _parse_frontmatter_block(raw_block: str) -> dict[str, Any]:
    lines = raw_block.splitlines()
    data: dict[str, Any] = {}
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        key, sep, remainder = line.partition(":")
        if not sep:
            raise ValueError("frontmatter must contain key-value pairs")

        key = key.strip()
        value = remainder.strip()
        if value:
            data[key] = _parse_inline_value(value)
            index += 1
            continue

        items: list[Any] = []
        index += 1
        while index < len(lines):
            next_line = lines[index]
            stripped = next_line.strip()
            if not stripped:
                index += 1
                continue
            if not next_line.startswith("  - "):
                break
            items.append(_parse_scalar(next_line[4:].strip()))
            index += 1
        data[key] = items

    return data


def _parse_inline_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    return _parse_scalar(value)


def _parse_scalar(value: str) -> Any:
    if value in {"null", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit():
        return int(value)
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _render_frontmatter_value(key: str, value: Any) -> str:
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        rendered_items = ", ".join(_render_scalar(item) for item in value)
        return f"{key}: [{rendered_items}]"
    return f"{key}: {_render_scalar(value)}"


def _render_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)
