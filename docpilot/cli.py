"""Command-line entry point: docpilot <command>."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .accuracy import check_draft, render_report
from .linkcheck import check_links
from .linter import lint_path
from .rag import (DEFAULT_THRESHOLD, Index, answer, evaluate, gap_report,
                  load_chunks)
from .releasenotes import categorize, git_subjects, render

QUERY_LOG = Path(".docpilot/queries.jsonl")


def _report(issues, strict: bool) -> int:
    for issue in issues:
        print(issue)
    errors = sum(i.severity == "error" for i in issues)
    warnings = sum(i.severity == "warning" for i in issues)
    infos = sum(i.severity == "info" for i in issues)
    print(f"\n{errors} error(s), {warnings} warning(s), {infos} info")
    return 1 if errors or (strict and warnings) else 0


def cmd_lint(args) -> int:
    issues = lint_path(args.path, args.terms)
    if args.quiet:
        issues = [i for i in issues if i.severity != "info"]
    return _report(issues, args.strict)


def cmd_links(args) -> int:
    return _report(check_links(args.path, external=args.external), strict=False)


def cmd_release_notes(args) -> int:
    notes = render(args.version, categorize(git_subjects(args.since)))
    if args.out:
        Path(args.out).write_text(notes, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(notes)
    return 0


def cmd_ask(args) -> int:
    index = Index(load_chunks(args.docs))
    llm = {"model": args.model, "url": args.ollama_url, "allow_remote": args.allow_remote} if args.llm else None
    result = answer(args.question, index, args.threshold, llm)
    print(result["text"])
    if result["sources"]:
        print("\nSources:", ", ".join(result["sources"]))
    print(f"\n(confidence {result['score']:.2f})")
    if not result["answered"]:
        QUERY_LOG.parent.mkdir(exist_ok=True)
        with QUERY_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"question": args.question, "score": result["score"]}) + "\n")
    return 0


def cmd_eval(args) -> int:
    index = Index(load_chunks(args.docs))
    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    result = evaluate(index, questions, args.threshold)
    logged = []
    if QUERY_LOG.exists():
        logged = sorted({json.loads(l)["question"] for l in QUERY_LOG.read_text().splitlines() if l.strip()})
    report = gap_report(result, logged)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")
    print(report)
    ok = result["hit_at_3"] >= args.min_hit
    if not ok:
        print(f"FAIL: top-3 hit rate {result['hit_at_3']:.0%} is below the minimum {args.min_hit:.0%}", file=sys.stderr)
    return 0 if ok else 1


def cmd_verify(args) -> int:
    text = Path(args.draft).read_text(encoding="utf-8")
    claims = check_draft(text, live=args.live)
    report = render_report(claims, args.draft)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    print(report)
    return 1 if any(c.status == "fail" for c in claims) else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="docpilot", description="Docs-as-code and GenAI toolkit.")
    p.add_argument("--version", action="version", version=f"docpilot {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("lint", help="Check structure, style and terminology.")
    s.add_argument("path", nargs="?", default="docs")
    s.add_argument("--terms", default="terminology.txt")
    s.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    s.add_argument("--quiet", action="store_true", help="Hide info-level findings.")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("links", help="Check relative links, anchors and optionally external URLs.")
    s.add_argument("path", nargs="?", default="docs")
    s.add_argument("--external", action="store_true")
    s.set_defaults(func=cmd_links)

    s = sub.add_parser("release-notes", help="Draft release notes from Conventional Commits.")
    s.add_argument("--since", help="Git tag or commit to start from.")
    s.add_argument("--version", default="Unreleased")
    s.add_argument("--out")
    s.set_defaults(func=cmd_release_notes)

    s = sub.add_parser("ask", help="Ask the docs a question.")
    s.add_argument("question")
    s.add_argument("--docs", default="docs")
    s.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    s.add_argument("--llm", action="store_true", help="Phrase the answer with a local Ollama model.")
    s.add_argument("--model", default="llama3.2")
    s.add_argument("--ollama-url", default="http://localhost:11434")
    s.add_argument("--allow-remote", action="store_true")
    s.set_defaults(func=cmd_ask)

    s = sub.add_parser("eval", help="Score retrieval and write a content gap report.")
    s.add_argument("--docs", default="docs")
    s.add_argument("--questions", default="eval/questions.json")
    s.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    s.add_argument("--min-hit", type=float, default=0.8)
    s.add_argument("--out", default="reports/gap-report.md")
    s.set_defaults(func=cmd_eval)

    s = sub.add_parser("verify", help="Accuracy gate for an AI-assisted draft.")
    s.add_argument("draft")
    s.add_argument("--live", action="store_true", help="Check flags against the installed restic binary.")
    s.add_argument("--out")
    s.set_defaults(func=cmd_verify)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
