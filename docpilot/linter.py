"""Docs linter: structure, style, terminology and front matter checks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .mdutil import (FENCE_INFO, HEADING, classify, headings, iter_md,
                     parse_front_matter, prose)

REQUIRED_FRONT_MATTER = ["title", "type", "last_reviewed"]
TOPIC_TYPES = {"concept", "task", "reference"}
FILLER = re.compile(r"\b(simply|just|easily|obviously|basically|please)\b", re.I)
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", re.I)
VAGUE_LINK = re.compile(r"\[(click here|here|this link|link)\]\(", re.I)
BAD_STEP_START = ("you ", "now ", "then ", "next ", "please ", "should ")
ORDERED_ITEM = re.compile(r"^\s*\d+\.\s+(.*)")
MAX_WORDS = 30


@dataclass
class Issue:
    path: str
    line: int
    code: str
    severity: str  # error | warning | info
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.severity.upper()} {self.code} {self.message}"


def load_terms(path: str | Path) -> list[tuple[str, str]]:
    """Read 'avoid | preferred' pairs, one per line. Lines starting with # are comments."""
    terms = []
    p = Path(path)
    if not p.exists():
        return terms
    for raw in p.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "|" not in raw:
            continue
        avoid, preferred = (part.strip() for part in raw.split("|", 1))
        terms.append((avoid, preferred))
    return terms


def lint_text(text: str, path: str, terms: list[tuple[str, str]]) -> list[Issue]:
    issues: list[Issue] = []

    def add(line: int, code: str, severity: str, message: str) -> None:
        issues.append(Issue(str(path), line, code, severity, message))

    meta, body = parse_front_matter(text)
    offset = text[: len(text) - len(body)].count("\n")

    # Front matter
    if not meta:
        add(1, "FM001", "error", "Missing front matter (title, type, last_reviewed).")
    else:
        for key in REQUIRED_FRONT_MATTER:
            if key not in meta:
                add(1, "FM002", "error", f"Front matter is missing '{key}'.")
        if meta.get("type") and meta["type"] not in TOPIC_TYPES:
            add(1, "FM003", "error", f"Unknown topic type '{meta['type']}'. Use concept, task or reference.")
        if meta.get("type") == "task":
            tested = str(meta.get("tested_version", ""))
            if not tested:
                add(1, "FM004", "error", "Task topics need 'tested_version' in front matter.")
            elif "UNTESTED" in tested.upper():
                add(1, "TST001", "warning", "Task is marked UNTESTED. Run every step, then record the version.")

    # Headings
    found = headings(body)
    h1s = [h for h in found if h[0] == 1]
    if len(h1s) != 1:
        add(offset + 1, "H001", "error", f"Expected exactly one H1, found {len(h1s)}.")
    previous = 0
    for level, title, number in found:
        if previous and level > previous + 1:
            add(offset + number, "H002", "error", f"Heading level jumps from H{previous} to H{level}: '{title}'.")
        previous = level
    if meta.get("type") == "task":
        h2s = {t.lower() for level, t, _ in found if level == 2}
        if "steps" not in h2s:
            add(offset + 1, "TSK001", "error", "Task topics need a '## Steps' section.")
        if "before you begin" not in h2s:
            add(offset + 1, "TSK002", "warning", "Task topics should have a '## Before you begin' section.")

    # Line by line
    term_patterns = [(re.compile(rf"(?<!\w){re.escape(a)}(?!\w)", re.I), a, p) for a, p in terms]
    for number, line, in_code, opens in classify(body.splitlines()):
        at = offset + number
        if opens and not FENCE_INFO.match(line).group(1):
            add(at, "C001", "warning", "Code block has no language tag.")
        if in_code or HEADING.match(line):
            continue
        if VAGUE_LINK.search(line):
            add(at, "L001", "warning", "Vague link text. Describe the destination instead.")
        text_only = prose(line)
        for pattern, avoid, preferred in term_patterns:
            if pattern.search(text_only):
                add(at, "TERM001", "error", f"Use '{preferred}' instead of '{avoid}'.")
        for match in FILLER.finditer(text_only):
            add(at, "S001", "warning", f"Remove filler word '{match.group(1)}'.")
        if PASSIVE.search(text_only):
            add(at, "S002", "info", "Possible passive voice. Prefer an active verb.")
        if not line.lstrip().startswith("|"):
            for sentence in re.split(r"(?<=[.!?])\s+", text_only):
                if len(sentence.split()) > MAX_WORDS:
                    add(at, "S003", "warning", f"Sentence has more than {MAX_WORDS} words.")
        if meta.get("type") == "task":
            item = ORDERED_ITEM.match(line)
            if item and item.group(1).lower().startswith(BAD_STEP_START):
                add(at, "STEP001", "warning", "Start the step with an imperative verb, such as 'Run' or 'Open'.")
    return issues


def lint_path(root: str | Path, terms_file: str | Path) -> list[Issue]:
    terms = load_terms(terms_file)
    issues: list[Issue] = []
    for md in iter_md(root):
        issues.extend(lint_text(md.read_text(encoding="utf-8"), str(md), terms))
    return issues
