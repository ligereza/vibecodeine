"""Guard the Git web boundary for the Linux MAK publisher."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_ci_targets_linux_and_separates_lanes_from_integrated_main():
    """The integrated baseline and the operational lanes have distinct CI."""
    for name in ("ci-mak.yml", "ci-integration.yml"):
        text = _workflow(name)
        assert "windows-latest" not in text, name
        assert "runs-on: ubuntu-latest" in text, name
        assert "mejoras" not in text, name

        # MAK CI belongs to MAK; the composition CI belongs to the integrated
        # main baseline. FLUJO has its own workflow in the portable lane.
        listas = re.findall(r"branches: \[([^\]]*)\]", text)
        assert listas, name
        for lista in listas:
            refs = {ref.strip() for ref in lista.split(",") if ref.strip()}
            expected = {"MAK"} if name == "ci-mak.yml" else {"main"}
            assert refs == expected, (name, sorted(refs))
            assert refs, name


def test_pull_request_composition_checks_the_revision_under_review():
    integration = _workflow("ci-integration.yml")
    assert "github.event.pull_request.merge_commit_sha" in integration
    assert "github.base_ref == 'MAK'" not in integration
    assert "github.base_ref == 'FLUJO'" not in integration
    assert "ref: ${{ github.event_name == 'pull_request'" in integration
    assert "path: flujo" not in integration


def test_automated_gates_cannot_publish_repo_changes():
    """No workflow that fires without a person may write to the repo.

    Until 2026-08-28 this checked one file, `airdrop_gate.yml`, which was
    retired with the rest of the airdrop chain. The property it names is about
    every gate that runs unattended, so it now covers all of them: the ones
    triggered by `push`, `pull_request`, `schedule` or `issues`. Workflows that
    only run on `workflow_dispatch` are excluded -- a person pressed the button.
    """
    automated = (
        # `ci.yml` until 2026-09-02, when it was split per lane.
        "ci-mak.yml",
        "ci-integration.yml",
        "seguridad.yml",
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
