from docpilot.accuracy import check_draft

DRAFT = """# T

Use restic 0.9.1 and expect 40% savings.

```bash
restic backup ~/docs --repo /tmp/r --exclude "*.tmp"
restic backup ~/docs --compress-level 9
restic archive --repo /tmp/r
restic forget --keep-last 3 \\
  --prune
```
"""


def by_text(claims):
    return {c.text: c for c in claims}


def test_valid_command_verified_and_invalid_flagged():
    claims = by_text(check_draft(DRAFT))
    assert claims['restic backup ~/docs --repo /tmp/r --exclude "*.tmp"'].status == "verified"
    assert claims["restic backup ~/docs --compress-level 9"].status == "fail"
    assert claims["restic archive --repo /tmp/r"].status == "fail"


def test_line_continuation_is_joined():
    claims = by_text(check_draft(DRAFT))
    assert claims["restic forget --keep-last 3 --prune"].status == "verified"


def test_numbers_and_versions_go_to_human_review():
    review = {c.text for c in check_draft(DRAFT) if c.status == "review"}
    assert {"0.9.1", "40%"} <= review
