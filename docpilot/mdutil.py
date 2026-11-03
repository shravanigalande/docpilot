"""Small Markdown helpers shared by every DocPilot tool (standard library only)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

FENCE = re.compile(r"^\s*(```|~~~)")
FENCE_INFO = re.compile(r"^\s*(?:```|~~~)\s*(\S*)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_TEXT = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Split simple YAML-style front matter (key: value, key: [a, b]) from the body."""
    match = FM_RE.match(text)
    if not match:
        return {}, text
    meta: dict = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            meta[key.strip()] = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key.strip()] = value.strip("'\"")
    return meta, text[match.end():]


def iter_md(root: str | Path) -> Iterator[Path]:
    path = Path(root)
    if path.is_file():
        yield path
        return
    yield from sorted(path.rglob("*.md"))


def classify(lines: list[str]) -> Iterator[tuple[int, str, bool, bool]]:
    """Yield (line_number, line, in_code, opens_fence). Fence lines count as code."""
    in_code = False
    for number, line in enumerate(lines, 1):
        if FENCE.match(line):
            yield number, line, True, not in_code
            in_code = not in_code
        else:
            yield number, line, in_code, False


def slugify(text: str) -> str:
    text = re.sub(r"[`*_]", "", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def headings(body: str) -> list[tuple[int, str, int]]:
    """Return (level, text, line_number) for headings outside code blocks."""
    found = []
    for number, line, in_code, _ in classify(body.splitlines()):
        if in_code:
            continue
        match = HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2), number))
    return found


def prose(line: str) -> str:
    """Strip links and inline code so style checks only see readable text."""
    return INLINE_CODE.sub("", LINK_TEXT.sub(r"\1", line))
