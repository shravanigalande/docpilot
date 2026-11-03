# DocPilot

A docs-as-code and GenAI toolkit for technical documentation. It documents [restic](https://restic.net), an open-source backup program, and ships the tooling that keeps those docs accurate:

- A **docs site** of concept, task and reference topics built with MkDocs.
- A **linter** for structure, style and terminology.
- A **link checker** for relative links, anchors and external URLs.
- A **release-note assembler** that drafts notes from Conventional Commits.
- A **docs chatbot** that answers from the docs, refuses when it cannot, and writes a **content gap report**.
- An **accuracy gate** that checks commands in AI-assisted drafts and routes everything else to a human.
- A **CI pipeline** that runs all of the above on every pull request.

The tools use only the Python standard library, so there is nothing to install to run them.

## Quick start

```bash
git clone <your-repo-url> && cd docpilot
pip install -e .            # optional: gives you the `docpilot` command
python -m docpilot lint docs
python -m docpilot links docs
python -m docpilot ask "How do I delete old snapshots?"
python -m docpilot eval
python -m docpilot verify examples/flawed-draft.md
python -m pytest -q
```

To preview the site, run `pip install -r requirements.txt` and then `mkdocs serve`.

## Commands

| Command | What it does |
|---|---|
| `docpilot lint [path]` | Checks front matter, headings, task structure, terminology, filler words, sentence length and code block tags. Use `--strict` to fail on warnings. |
| `docpilot links [path]` | Finds broken links and anchors. Add `--external` to check URLs. |
| `docpilot release-notes --since v1.0 --version 1.1` | Drafts release notes from commit messages. Skips internal commit types. |
| `docpilot ask "question"` | Answers from the docs with a source link. Logs low-confidence questions as gaps. |
| `docpilot eval` | Scores retrieval against `eval/questions.json` and writes `reports/gap-report.md`. |
| `docpilot verify draft.md [--live]` | Checks commands in a draft. With `--live`, flags are checked against the installed `restic --help`. |

## How the accuracy gate works

AI drafts fail in predictable ways: invented flags, nonexistent commands and stale versions. `docpilot verify` extracts every command from code blocks and inline code and checks the subcommand and flags. It reports numbers and version strings as **needs human review**, because a script cannot confirm them.

A passing result means "the command exists", not "the procedure works". Every task topic carries a `tested_version` field. The linter warns until a person has run all the steps and recorded the version.

## Data-handling policy

- Use approved or local AI tools only.
- Never paste confidential or customer data into an unapproved tool.
- `docpilot ask --llm` talks only to a local Ollama server. It refuses any other host unless you pass `--allow-remote`.
- Generated drafts are reviewed by a person before publishing. See the [decision log](docs/decisions.md).

## Design decisions and known limits

- **Retrieval is TF-IDF, not embeddings.** It is transparent and needs no dependencies, which suits a small corpus. Replace `Index` in `docpilot/rag.py` with a sentence-embedding index if the docs grow.
- **Confidence is IDF-weighted term coverage.** Plain cosine similarity scored unanswerable questions as confidently as answerable ones, because words like "repository" appear everywhere. Coverage fixed most cases. It still lets through questions whose words all appear in the docs without the answer, such as "How do I change the repository password?". The eval reports that miss instead of hiding it.
- **`known_commands.json` is an offline fallback** and can lag behind new restic releases. Prefer `--live`.
- **The release-note assembler ignores non-conventional commits.** A writer decides what to do with them.

## Project layout

```text
docs/            Topics, style guide and decision log
docpilot/        The tools
eval/            Questions for the chatbot evaluation
examples/        A deliberately flawed draft for the accuracy gate
tests/           Unit tests
terminology.txt  Words to avoid and their preferred terms
.github/         CI workflow
```
