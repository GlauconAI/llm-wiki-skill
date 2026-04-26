from __future__ import annotations

import re


ASCII_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
_CJK_RANGES = (
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0x31F0, 0x31FF),  # Katakana Phonetic Extensions
    (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xAC00, 0xD7AF),  # Hangul Syllables
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
)


def _is_cjk(char: str) -> bool:
    code_point = ord(char)
    return any(start <= code_point <= end for start, end in _CJK_RANGES)


def _normalize_ascii_token(token: str) -> list[str]:
    normalized = [token]
    if "-" in token:
        spaced = token.replace("-", " ")
        if spaced != token:
            normalized.append(spaced)
    return normalized


def _dedupe_preserving_order(tokens: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


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
    ascii_tokens = [
        normalized
        for token in ASCII_WORD_RE.findall(lowered)
        if len(token) >= 2
        for normalized in _normalize_ascii_token(token)
    ]
    return _dedupe_preserving_order(ascii_tokens + _cjk_bigrams(text))
