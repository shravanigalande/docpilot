from docpilot.linkcheck import check_links


def write(tmp_path, name, text):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_broken_link_and_anchor(tmp_path):
    write(tmp_path, "a.md", "---\ntitle: A\n---\n# A\n\n[ok](b.md#target) [bad](missing.md) [anchor](b.md#nope)\n")
    write(tmp_path, "b.md", "---\ntitle: B\n---\n# B\n\n## Target\n")
    codes = sorted(i.code for i in check_links(tmp_path))
    assert codes == ["LINK001", "LINK002"]


def test_links_in_code_blocks_are_ignored(tmp_path):
    write(tmp_path, "a.md", "# A\n\n```md\n[x](nowhere.md)\n```\n")
    assert check_links(tmp_path) == []
