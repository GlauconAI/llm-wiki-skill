from __future__ import annotations

import re


ASCII_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*")


def _is_cjk(char: str) -> bool:
    return "\u4e00" <= char <= "\u9fff"


def _cjk_bigrams(text: str) -> list[str]:
    tokens: list[str] = []
    span: list[str] = []

    def flush_span() -> None:
        if not span:
            return
        if len(span) == 1:
            tokens.append(span[0])
        else:
            tokens.extend("".join(span[i : i + 2]) for i in range(len(span) - 1))
        span.clear()

    for char in text:
        if _is_cjk(char):
            span.append(char)
        else:
            flush_span()
    flush_span()
    return tokens


def tokenize_query(text: str) -> list[str]:
    lowered = text.lower()
    ascii_tokens = [token for token in ASCII_WORD_RE.findall(lowered) if len(token) >= 2]
    return ascii_tokens + _cjk_bigrams(text)
