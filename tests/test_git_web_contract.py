"""Guard the Git web boundary for the Linux MAK publisher."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_ci_targets_linux_and_canonical_branches_only():
    text = _workflow("ci.yml")

    assert "windows-latest" not in text
    assert "os: [ubuntu-latest]" in text
    assert "branches: [main]" in text
    assert "mejoras" not in text


def test_git_topology_guard_requires_one_trunk_and_archive_tag():
    text = _workflow("git-topology.yml")

    assert "branches: [main]" in text
    assert "archive/house-history" in text
    assert "Unexpected permanent remote branch refs" in text
    assert "contents: write" not in text
    assert "git push" not in text


def test_automated_gates_cannot_publish_repo_changes():
    for name in ("airdrop_gate.yml", "claude.yml"):
        text = _workflow(name)
        assert "git push" not in text
        assert "gh pr create" not in text
        assert "contents: write" not in text
        assert "pull-requests: write" not in text


def test_claude_workflow_is_disabled_and_manual_only():
    text = _workflow("claude.yml")

    assert "workflow_dispatch: {}" in text
    assert "if: ${{ false }}" in text


def test_pages_publication_requires_explicit_dispatch():
    text = _workflow("publicar_iskvw.yml")

    assert "workflow_dispatch: {}" in text
    assert "\n  push:" not in text


def test_workflows_do_not_treat_win_as_runtime():
    for path in WORKFLOWS.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        assert "windows-latest" not in text
        assert "WIN" not in text
        assert "powershell" not in text.lower()
