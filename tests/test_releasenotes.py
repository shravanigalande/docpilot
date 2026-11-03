from datetime import date

from docpilot.releasenotes import categorize, render


def test_categorize_skips_internal_and_flags_breaking():
    groups = categorize(["feat(cli): add ask", "fix: typo.", "chore: deps", "feat!: new format", "random message"])
    assert groups["feat"] == ["**cli**: Add ask"]
    assert groups["fix"] == ["Typo"]
    assert groups["breaking"] == ["New format"]
    assert groups["other"] == []


def test_render_contains_review_notice():
    text = render("1.0.0", categorize(["feat: x"]), date(2026, 1, 1))
    assert "# Release notes: 1.0.0" in text and "writer must review" in text
