"""KNOWN DEFECT, documented not endorsed: `flujo doctor`'s "git working tree"
row reads a FAILED `git status --short` as a clean tree.

`doctor` runs three git calls to build its report. Two of them --
"git branch" and "git origin" -- correctly check `returncode == 0` and show
AVISO when git fails. The third does not:

    dirty = bool(status.stdout.strip())
    add("git working tree", not dirty, "limpio" if not dirty else "hay cambios locales")

Empty stdout from a git call that FAILED (not a repository, git missing,
timeout: `returncode != 0`) reads identically to empty stdout from a git call
that succeeded with a genuinely clean tree. Reproduced below by pointing
`repo_root()` at a directory with no `.git`: "git branch" and "git origin"
correctly show AVISO for the *same* failed git invocation, while "git working
tree" shows OK / "limpio".

This is the same class of bug already fixed elsewhere in this repo: `flujo
doctor` reporting `airdrop pendiente: OK` for a directory that did not exist,
and `flujo github-sync --status` (a sibling command in the same file)
printing "Working tree limpio" when every git call failed outside a
repository. That second one was fixed 2026-08-31 in `github_sync()`; this row
in `doctor()` was missed by that fix because it is a separate code path in
the same command file.

`cli.py` is out of this agent's zone (see task scope), so the defect is
pinned here rather than fixed: doing so makes a future fix a visible behavior
change instead of a silent one, per this repo's own doctrine (a defect found
and not fixed must be named with a test, not swept past).
"""
from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from flujo.cli import app
import flujo.paths as paths

runner = CliRunner()


def test_doctor_falsely_reports_a_clean_working_tree_when_git_status_fails(
        tmp_path: Path, monkeypatch):
    monkeypatch.setattr(paths, "repo_root", lambda: tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    # The other two git checks over the SAME failed git invocation correctly
    # name the failure:
    assert "git branch" in result.output
    assert "git origin" in result.output
    # ...but "git working tree" claims OK / limpio instead of naming that the
    # measurement never ran. THIS is the defect, pinned as it stands today:
    assert "git working tree" in result.output
    assert "limpio" in result.output, (
        "pinned: an unmeasured tree is currently reported as clean -- "
        "fixing this (naming the failed `git status` instead of asserting "
        "'limpio') should break this assertion")
