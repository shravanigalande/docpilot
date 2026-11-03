"""Link checker: relative links, anchors and (optionally) external URLs."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

from .linter import Issue
from .mdutil import classify, headings, iter_md, parse_front_matter, slugify

LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def _anchors(path: Path) -> set[str]:
    _, body = parse_front_matter(path.read_text(encoding="utf-8"))
    return {slugify(title) for _, title, _ in headings(body)}


def check_external(url: str, timeout: int = 10) -> str | None:
    """Return an error message, or None if the URL responds with a non-error status."""
    error = "no response"
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "docpilot-linkcheck"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status < 400:
                    return None
        except Exception as exc:  # noqa: BLE001 - report any network failure
            error = str(exc)
    return error


def check_links(root: str | Path, external: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    for md in iter_md(root):
        text = md.read_text(encoding="utf-8")
        _, body = parse_front_matter(text)
        offset = text[: len(text) - len(body)].count("\n")
        for number, line, in_code, _ in classify(body.splitlines()):
            if in_code:
                continue
            for target in LINK.findall(line):
                at = offset + number
                if target.startswith("mailto:"):
                    continue
                if target.startswith(("http://", "https://")):
                    if external:
                        error = check_external(target)
                        if error:
                            issues.append(Issue(str(md), at, "LINK003", "error", f"External link failed: {target} ({error})"))
                    continue
                path_part, _, anchor = target.partition("#")
                destination = md if not path_part else (md.parent / path_part).resolve()
                if not destination.exists():
                    issues.append(Issue(str(md), at, "LINK001", "error", f"Broken link: {target}"))
                elif anchor and destination.suffix == ".md" and slugify(anchor) not in _anchors(destination):
                    issues.append(Issue(str(md), at, "LINK002", "error", f"Missing anchor '#{anchor}' in {destination.name}"))
    return issues
