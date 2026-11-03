---
title: Decision log
type: reference
tags: [process, ai]
last_reviewed: 2026-11-04
---
# Decision log

This log records decisions about how the docs are produced, including what went wrong when AI drafted content and how the review caught it.

## How to use this log

Add one entry each time an AI-assisted draft contains an error. Record the tool, the prompt, the error and the check that caught it. Write only what really happened.

## Entry template

| Field | Content |
|---|---|
| Date | The day you found the error. |
| Tool and prompt | The model and the instruction you gave it. |
| What was wrong | The incorrect claim, such as an invented flag or an outdated version. |
| How it was caught | The check that found it, such as `docpilot verify --live`. |
| Rule added | The new lint rule, checklist item or prompt change. |

## Data handling

Use only approved or local AI tools. Never paste confidential or customer data into an unapproved tool. The chatbot in this project refuses to send content to a non-local model unless you pass `--allow-remote`.
