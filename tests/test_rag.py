import pytest

from docpilot.rag import Index, answer, ensure_local, evaluate, load_chunks


@pytest.fixture()
def index(tmp_path):
    (tmp_path / "install.md").write_text(
        "---\ntitle: Install the tool\ntype: task\n---\n# Install the tool\n\nInstall it.\n\n## Steps\n\n1. Run brew install.\n")
    (tmp_path / "prune.md").write_text(
        "---\ntitle: Remove old snapshots\ntype: task\n---\n# Remove old snapshots\n\n## Steps\n\n1. Run forget with prune to delete snapshots.\n")
    return Index(load_chunks(tmp_path))


def test_retrieves_right_topic(index):
    assert index.search("how do I delete snapshots", 1)[0][1].path == "prune.md"


def test_abstains_on_unknown_topic(index):
    result = answer("How do I configure Kubernetes autoscaling?", index)
    assert not result["answered"] and result["sources"] == []


def test_evaluate_counts_hits_and_rejections(index):
    qs = [{"question": "how do I install", "expected": ["install.md"]},
          {"question": "configure Kubernetes autoscaling", "expected": []}]
    result = evaluate(index, qs)
    assert result["hit_at_1"] == 1.0 and result["correct_rejections"] == 1.0


def test_remote_hosts_are_refused():
    ensure_local("http://localhost:11434")
    with pytest.raises(ValueError):
        ensure_local("https://api.example.com")
