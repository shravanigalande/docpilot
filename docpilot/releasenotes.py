"""Release-note assembler: turns Conventional Commit subjects into a draft note."""
from __future__ import annotations

import re
import subprocess
from datetime import date

CONVENTIONAL = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<desc>.+)$")

SECTIONS = [
    ("breaking", "Breaking changes"),
    ("feat", "New features"),
    ("fix", "Fixes"),
    ("perf", "Improvements"),
    ("docs", "Documentation"),
    ("other", "Other changes"),
]
# Internal work that customers do not need to read about.
SKIP_TYPES = {"chore", "ci", "test", "build", "style"}


def categorize(subjects: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {key: [] for key, _ in SECTIONS}
    for subject in subjects:
        match = CONVENTIONAL.match(subject.strip())
        if not match:
            continue  # Non-conventional commits need a human decision.
        kind = match.group("type").lower()
        if kind in SKIP_TYPES:
            continue
        desc = match.group("desc").strip().rstrip(".")
        desc = desc[0].upper() + desc[1:]
        if match.group("scope"):
            desc = f"**{match.group('scope')}**: {desc}"
        if match.group("bang"):
            groups["breaking"].append(desc)
        elif kind in {"feat", "fix", "perf", "docs"}:
            groups[kind].append(desc)
        else:
            groups["other"].append(desc)
    return groups


def render(version: str, groups: dict[str, list[str]], when: date | None = None) -> str:
    when = when or date.today()
    lines = [f"# Release notes: {version}", "", f"Release date: {when.isoformat()}", ""]
    for key, title in SECTIONS:
        if groups.get(key):
            lines += [f"## {title}", ""] + [f"- {item}" for item in groups[key]] + [""]
    lines.append("*Draft generated from commit messages. A writer must review it before publishing.*")
    return "\n".join(lines) + "\n"


def git_subjects(since: str | None = None, cwd: str = ".") -> list[str]:
    rev = f"{since}..HEAD" if since else "HEAD"
    result = subprocess.run(
        ["git", "log", rev, "--pretty=format:%s"], cwd=cwd, capture_output=True, text=True, check=True
    )
    return [line for line in result.stdout.splitlines() if line.strip()]
