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
    """No workflow that fires without a person may write to the repo.

    Until 2026-08-28 this checked one file, `airdrop_gate.yml`, which was
    retired with the rest of the airdrop chain. The property it names is about
    every gate that runs unattended, so it now covers all of them: the ones
    triggered by `push`, `pull_request`, `schedule` or `issues`. Workflows that
    only run on `workflow_dispatch` are excluded -- a person pressed the button.
    """
    automated = (
        "ci.yml",
        "seguridad.yml",
        "git-topology.yml",
        "validar-piezas.yml",
        "render_piezas_vectoriales.yml",
        "issue_descarga_ig.yml",
        "ordenes_curatoria.yml",
    )
    for name in automated:
        text = _workflow(name)
        assert "git push" not in text, name
        assert "gh pr create" not in text, name
        assert "contents: write" not in text, name
        assert "pull-requests: write" not in text, name


def test_pages_publication_requires_explicit_dispatch():
    text = _workflow("publicar_iskvw.yml")

    assert "workflow_dispatch: {}" in text
    assert "\n  push:" not in text


def test_pages_publication_scope_excludes_rd_venue_mak_and_win():
    """The public portfolio must not become a dump of MAK's local box."""
    text = _workflow("publicar_iskvw.yml")

    assert "cp -r iskvw/. _sitio/" in text
    assert "data/rd.db" not in text
    assert "data/rd_datos.db" not in text
    assert "data/venues" not in text
    assert "cultura/" not in text
    assert "WIN/" not in text
    assert "cp -r . _sitio/" not in text


def test_workflows_do_not_treat_win_as_runtime():
    for path in WORKFLOWS.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        assert "windows-latest" not in text
        assert "WIN" not in text
        assert "powershell" not in text.lower()


def test_issue_render_ignores_unrelated_label_events():
    """Adding a bookkeeping label must not launch a second Blender render."""
    text = _workflow("issue_descarga_ig.yml")

    assert (
        "(github.event.action == 'opened' || "
        "github.event.label.name == 'action/descargar-ig')"
    ) in text
    assert "contains(github.event.issue.labels.*.name, 'action/descargar-ig')" in text
