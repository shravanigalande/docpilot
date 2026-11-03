---
title: Style guide
type: reference
tags: [style, contributing]
last_reviewed: 2026-11-04
---
# Style guide

The linter enforces these rules. Run `docpilot lint docs` before every pull request.

## Topic types

Every topic declares `type` in its front matter as `concept`, `task` or `reference`. Task topics also record `tested_version`, the restic version you used when you ran every step.

## Task topics

- Start with a one-sentence goal.
- Add a `Before you begin` section for prerequisites.
- Put numbered actions under a `Steps` section.
- Write one action per step and start it with an imperative verb, such as `Run` or `Create`.
- State what the user should see after a key step.

## Writing rules

- Keep sentences under 30 words.
- Use active voice.
- Remove filler words such as `simply`, `just` and `please`.
- Give every code block a language tag.
- Write link text that describes the destination. Never use `here`.

## Terminology

The file `terminology.txt` lists words to avoid and the preferred term. The linter reports each match as an error. Examples: use `repository`, not `backup repo`, and use `use`, not `utilize`.
