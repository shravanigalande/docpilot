"""Accuracy gate: extract checkable claims from a draft and verify what can be verified.

Commands in code blocks and inline code are checked against the real tool (--live) or an
offline list. Numbers and versions cannot be machine-verified, so they are always routed
to a human reviewer. Nothing here replaces testing each step against the product.
"""
from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .mdutil import classify, parse_front_matter

KNOWN = json.loads((Path(__file__).parent / "known_commands.json").read_text(encoding="utf-8"))
TOOL = "restic"
INLINE_CMD = re.compile(r"`(restic [^`]+)`")
NUMBER_CLAIM = re.compile(r"\b\d+(?:\.\d+)?\s?(?:%|(?:GB|MB|KB|TB|seconds|minutes|hours|days)\b)", re.I)
VERSION_CLAIM = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b")
FLAG_IN_HELP = re.compile(r"(?<![\w-])(--?[A-Za-z][\w-]*)")


@dataclass
class Claim:
    line: int
    kind: str      # command | number | version
    text: str
    status: str    # verified | unverified | fail | review
    detail: str


def is_package_install(tokens: list[str]) -> bool:
    return (
        tokens == ["brew", "install", "restic"]
        or tokens == ["sudo", "apt", "install", "restic"]
        or tokens == ["sudo", "apt-get", "install", "restic"]
    )


def extract_commands(body: str) -> list[tuple[int, str]]:
    lines = body.splitlines()
    commands: list[tuple[int, str]] = []
    i = 0
    states = list(classify(lines))

    while i < len(states):
        number, line, code, _ = states[i]

        if code and not re.match(r"^\s*(```|~~~)", line):
            stripped = line.strip().lstrip("$").strip()

            while stripped.endswith("\\") and i + 1 < len(states):
                i += 1
                stripped = stripped[:-1].rstrip() + " " + states[i][1].strip()

            try:
                tokens = shlex.split(stripped)
            except ValueError:
                tokens = []

            if is_package_install(tokens):
                commands.append((number, stripped))
            else:
                match = re.search(rf"(?:^|\s){TOOL}(?:\s|$)", stripped)
                if match and not stripped.startswith("#"):
                    commands.append((number, stripped[match.start():].strip()))

        elif not code:
            for found in INLINE_CMD.findall(line):
                commands.append((number, found))

        i += 1

    return commands


_help_cache: dict[str, set[str]] = {}


def live_flags(subcommand: str) -> set[str] | None:
    if not shutil.which(TOOL):
        return None
    if subcommand not in _help_cache:
        out = subprocess.run([TOOL, subcommand, "--help"], capture_output=True, text=True)
        _help_cache[subcommand] = set(FLAG_IN_HELP.findall(out.stdout + out.stderr))
    return _help_cache[subcommand]


def verify_command(line: int, command: str, live: bool) -> Claim:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return Claim(line, "command", command, "fail",
                     f"Could not parse command: {exc}")

    if is_package_install(tokens):
        return Claim(line, "command", command, "verified",
                     "Recognized Restic package installation command.")

    sub = next(
        (t for t in tokens[1:] if t in KNOWN["subcommands"]),
        None
    )

    if sub is None:
        return Claim(line, "command", command, "fail",
                     "No known restic subcommand found.")

    allowed = set(KNOWN["global_flags"]) | set(KNOWN["subcommands"][sub])
    source = "offline list"

    if live:
        flags = live_flags(sub)
        if flags is None:
            return Claim(line, "command", command, "unverified",
                         "restic is not installed, so --live could not run.")
        allowed, source = flags, "restic --help"

    unknown = []

    for token in tokens[1:]:
        if not token.startswith("-") or token.startswith("<") or "$" in token:
            continue

        name = token.split("=", 1)[0]

        if name in allowed:
            continue

        if not name.startswith("--") and len(name) > 2:
            if all(f"-{ch}" in allowed for ch in name[1:]):
                continue

        unknown.append(name)

    if unknown:
        return Claim(line, "command", command, "fail",
                     f"Flag not found in {source}: {', '.join(unknown)}")

    return Claim(line, "command", command, "verified",
                 f"Subcommand and flags match {source}. Still run it once.")


def check_draft(text: str, live: bool = False) -> list[Claim]:
    _, body = parse_front_matter(text)
    claims = [verify_command(n, c, live) for n, c in extract_commands(body)]
    for number, line, in_code, _ in classify(body.splitlines()):
        if in_code:
            continue
        for m in NUMBER_CLAIM.finditer(line):
            claims.append(Claim(number, "number", m.group(0), "review", "Check this figure against the product or source."))
        for m in VERSION_CLAIM.finditer(line):
            claims.append(Claim(number, "version", m.group(0), "review", "Check this version is current. AI drafts often use stale versions."))
    return sorted(claims, key=lambda c: c.line)


def render_report(claims: list[Claim], source: str) -> str:
    counts = {s: sum(c.status == s for c in claims) for s in ("verified", "fail", "review", "unverified")}
    lines = [
        f"# Accuracy report: {source}", "",
        f"- Verified commands: {counts['verified']}",
        f"- Failed commands: {counts['fail']}",
        f"- Claims needing human review: {counts['review']}",
        f"- Unverified: {counts['unverified']}", "",
        "| Line | Type | Claim | Status | Detail |", "|---|---|---|---|---|",
    ]
    for c in claims:
        text = c.text.replace("|", "\\|")
        lines.append(f"| {c.line} | {c.kind} | `{text}` | {c.status.upper()} | {c.detail} |")
    lines += ["", "**A senior writer must still review this draft before it is published.**"]
    return "\n".join(lines) + "\n"
