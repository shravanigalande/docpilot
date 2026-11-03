from docpilot.linter import lint_text

TERMS = [("utilize", "use"), ("folder", "directory")]

GOOD = """---
title: Do a thing
type: task
tags: [x]
last_reviewed: 2026-11-04
tested_version: 0.16.0
---
# Do a thing

Do the thing.

## Before you begin

- Install the tool.

## Steps

1. Run the command:

    ```bash
    echo hi
    ```
"""


def codes(text):
    return {i.code for i in lint_text(text, "t.md", TERMS)}


def test_clean_topic_has_no_issues():
    assert codes(GOOD) == set()


def test_missing_front_matter():
    assert "FM001" in codes("# Title\n\nText.\n")


def test_untested_task_warns():
    assert "TST001" in codes(GOOD.replace("0.16.0", "UNTESTED"))


def test_terminology_filler_and_step_rules():
    bad = GOOD.replace("Do the thing.", "You should utilize the folder. Just do it.").replace(
        "1. Run the command:", "1. You should run the command:")
    found = codes(bad)
    assert {"TERM001", "S001", "STEP001"} <= found


def test_heading_level_jump_and_missing_steps():
    bad = GOOD.replace("## Steps", "#### Steps")
    found = codes(bad)
    assert "H002" in found and "TSK001" in found


def test_code_block_without_language():
    assert "C001" in codes(GOOD.replace("```bash", "```"))


def test_code_blocks_are_not_checked_as_prose():
    assert "TERM001" not in codes(GOOD.replace("echo hi", "utilize folder"))
