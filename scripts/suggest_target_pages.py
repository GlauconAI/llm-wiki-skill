#!/usr/bin/env python3
from __future__ import annotations
from collections import Counter
from pathlib import Path
import re
import sys

ROOT_DEFAULT = Path('/Users/glaucon/Obsidian/Glaucon Vault/aristotle-lyceum/llm-wiki')
WORD_RE = re.compile(r'[A-Za-z][A-Za-z0-9\-]{2,}|[\u4e00-\u9fff]{2,}')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n?', re.S)
TYPE_RE = re.compile(r'^type:\s*(.+)$', re.M)
TITLE_RE = re.compile(r'^title:\s*(.+)$', re.M)
STOPWORDS = {
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'your', 'what', 'when', 'where', 'which',
    'openclaw', 'wiki', 'page', 'pages', 'topic', 'topics', 'concept', 'concepts', 'entity', 'entities',
    'agent', 'agents', 'system', 'systems', 'note', 'notes', 'raw', 'source', 'sources', 'overview',
    '当前', '可以', '什么', '如何', '以及', '不是', '一个', '这类', '页面', '系统', '主题', '知识'
}


def frontmatter_block(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return m.group(1) if m else ''


def body_without_frontmatter(text: str) -> str:
    m = FRONTMATTER_RE.match(text)
    return text[m.end():] if m else text


def parse_type(text: str):
    m = TYPE_RE.search(frontmatter_block(text))
    return m.group(1).strip() if m else None


def parse_title(text: str, fallback: str):
    m = TITLE_RE.search(frontmatter_block(text))
    return m.group(1).strip() if m else fallback


def tokenize(text: str):
    toks = []
    for t in WORD_RE.findall(text.lower()):
        if len(t) >= 2 and t not in STOPWORDS:
            toks.append(t)
    return toks


def weighted_tokens(raw_text: str, raw_file: Path):
    body = body_without_frontmatter(raw_text)
    title = parse_title(raw_text, raw_file.stem)
    tokens = []
    tokens.extend(tokenize(raw_file.stem) * 4)
    tokens.extend(tokenize(title) * 5)
    tokens.extend(tokenize(body[:4000]))
    return Counter(tokens)


def page_score(raw_counter: Counter, title: str, rel_path: str, text: str):
    title_tokens = tokenize(title)
    path_tokens = tokenize(rel_path.replace('/', ' '))
    body_tokens = tokenize(body_without_frontmatter(text)[:2500])
    score = 0
    for tok in title_tokens:
        score += raw_counter[tok] * 5
    for tok in path_tokens:
        score += raw_counter[tok] * 3
    for tok in set(body_tokens):
        score += min(raw_counter[tok], 2)
    return score


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/suggest_target_pages.py <raw-file> [llm-wiki-root]')
        return 2
    raw_file = Path(sys.argv[1]).expanduser()
    root = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else ROOT_DEFAULT
    if not raw_file.exists():
        print(f'ERROR: raw file not found: {raw_file}')
        return 2
    raw_text = raw_file.read_text(encoding='utf-8', errors='replace')
    raw_counter = weighted_tokens(raw_text, raw_file)
    candidates = []
    for path in sorted((root / 'wiki').rglob('*.md')):
        rp = path.relative_to(root).as_posix()
        if '/sources/' in rp or '/reports/' in rp:
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        page_type = parse_type(text)
        if page_type not in {'overview', 'concept', 'entity', 'topic'}:
            continue
        title = parse_title(text, path.stem)
        s = page_score(raw_counter, title, rp[:-3], text)
        if s >= 6:
            candidates.append((s, rp[:-3], title))
    candidates.sort(reverse=True)
    print('Suggested affected pages:')
    if not candidates:
        print('- No strong candidates found. Consider creating a new topic or concept page.')
        return 0
    for s, rp, title in candidates[:12]:
        print(f'- [[{rp}|{title}]] (score: {s})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
