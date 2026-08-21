import json

from typer.testing import CliRunner

from flujo import autonomia
from flujo.cli import app


runner = CliRunner()


def test_autonomy_status_reports_clean_blockers(monkeypatch, tmp_path):
    monkeypatch.setattr(autonomia, "_branch_state", lambda: {
        "current": "codex/test",
        "dirty": [" M src/x.py"],
        "remote_branches": ["main", "mak", "rd", "iskvw"],
        "canonical_present": {"main": True},
        "legacy_transition_branches": ["iskvw", "mak", "rd"],
        "source_copy_branches": [],
        "temporary_work_branches": [],
        "unclassified_remote_branches": [],
    })
    monkeypatch.setattr(autonomia, "_open_prs", lambda: [])
    monkeypatch.setattr(autonomia, "_provider_state", lambda: {
        "watsonx": False,
        "aws": False,
        "ollama": False,
        "free_cloud": {"cerebras": False, "groq": False},
    })

    status = autonomia.autonomy_status(
        common_path=str(tmp_path / "common.jsonl"),
        batch_path=str(tmp_path / "batches.jsonl"),
    )

    assert status["ready"] is False
    assert status["blockers"] == ["repo_dirty"]
    assert status["batch_contract"]["areas"] == list(autonomia.DEFAULT_AREAS)


def test_autonomy_status_surfaces_quarantine(tmp_path):
    common = tmp_path / "common.jsonl"
    quarantine = tmp_path / "common_ledger_quarantine.jsonl"
    quarantine.write_text(json.dumps({
        "schema": "mak-ledger-quarantine-v1",
        "status": "quarantined",
        "domain": "svg",
        "original_id": "old1",
    }) + "\n", encoding="utf-8")

    status = autonomia.autonomy_status(
        common_path=str(common), batch_path=str(tmp_path / "batches.jsonl"))

    assert status["ledgers"]["quarantine"]["total"] == 1
    assert status["ledgers"]["quarantine"]["by_domain"] == {"svg": 1}
    assert status["next_actions"] == ["review_quarantined_evidence"]


def test_open_prs_treats_gh_timeout_as_unavailable(monkeypatch):
    def timed_out(*_args, **_kwargs):
        raise autonomia.subprocess.TimeoutExpired("gh", 30)

    monkeypatch.setattr(autonomia.subprocess, "run", timed_out)

    assert autonomia._open_prs() == []


def test_autonomy_status_derives_operational_surface(monkeypatch, tmp_path):
    monkeypatch.setattr(autonomia, "_branch_state", lambda: {
        "current": "mak",
        "dirty": [],
        "remote_branches": ["main", "mak", "rd", "iskvw"],
        "canonical_present": {"main": True},
        "legacy_transition_branches": ["iskvw", "mak", "rd"],
        "source_copy_branches": [],
        "temporary_work_branches": [],
        "unclassified_remote_branches": [],
    })
    monkeypatch.setattr(autonomia, "_open_prs", lambda: [{
        "number": 507,
        "mergeStateStatus": "BLOCKED",
    }])
    monkeypatch.setattr(autonomia, "_readme_svg_state", lambda: {"status": "clean"})

    status = autonomia.autonomy_status(
        common_path=str(tmp_path / "common.jsonl"),
        batch_path=str(tmp_path / "batches.jsonl"),
    )

    assert status["operational"]["promotion"] == {
        "open_prs": 1,
        "blocked_prs": [507],
    }
    assert status["operational"]["visual_surface"] == {"readme_svg": "clean"}
    assert "review_open_promotion_prs" in status["operational"]["next_actions"]


def test_branch_classifier_separates_current_and_historical_refs():
    assert autonomia._classify_branch("main") == "canonical"
    assert autonomia._classify_branch("mak-svg") == "legacy_transition"
    assert autonomia._classify_branch("source/iskvw") == "source_copy"
    assert autonomia._classify_branch("work/portfolio-rebuild") == "temporary_work"
    assert autonomia._classify_branch("dependabot/pip/pytest") == "temporary_work"
    assert autonomia._classify_branch("feature/unknown") == "unclassified"


def test_branch_state_reports_source_copies_without_blocking_them(monkeypatch):
    outputs = {
        ("branch", "--show-current"): "work/portfolio-rebuild",
        ("status", "--porcelain"): "",
        ("for-each-ref", "--format=%(refname:short)",
         "refs/remotes/origin"): "\n".join([
             "origin/HEAD", "origin/main", "origin/source/iskvw",
             "origin/source/rd", "origin/work/portfolio-rebuild",
             "origin/feature/unknown",
         ]),
    }
    monkeypatch.setattr(
        autonomia, "_run_git",
        lambda args: outputs.get(tuple(args), ""),
    )

    state = autonomia._branch_state()

    assert state["current_classification"] == "temporary_work"
    assert state["canonical_present"] == {"main": True}
    assert state["source_copy_branches"] == ["source/iskvw", "source/rd"]
    assert state["temporary_work_branches"] == ["work/portfolio-rebuild"]
    assert state["unclassified_remote_branches"] == ["feature/unknown"]


def test_missing_main_blocks_but_source_copies_do_not(monkeypatch, tmp_path):
    monkeypatch.setattr(autonomia, "_branch_state", lambda: {
        "current": "source/rd",
        "dirty": [],
        "remote_branches": ["source/rd"],
        "canonical_present": {"main": False},
        "legacy_transition_branches": [],
        "source_copy_branches": ["source/rd"],
        "temporary_work_branches": [],
        "unclassified_remote_branches": [],
    })
    monkeypatch.setattr(autonomia, "_open_prs", lambda: [])
    monkeypatch.setattr(autonomia, "_readme_svg_state", lambda: {"status": "clean"})

    status = autonomia.autonomy_status(
        common_path=str(tmp_path / "common.jsonl"),
        batch_path=str(tmp_path / "batches.jsonl"),
    )

    assert status["ready"] is False
    assert status["blockers"] == ["missing_canonical_branches:main"]


def test_run_autonomy_dry_run_writes_briefs(monkeypatch, tmp_path):
    monkeypatch.setattr(autonomia, "autonomy_status", lambda **_kwargs: {
        "ready": True,
        "blockers": [],
    })

    result = autonomia.run_autonomy(autonomia.RunOptions(
        areas=("rd_evidence",),
        providers=("watsonx", "aws"),
        round_id="rtest",
        out_dir=str(tmp_path),
        common_ledger_path=str(tmp_path / "common.jsonl"),
        batch_ledger_path=str(tmp_path / "batches.jsonl"),
        dry_run=True,
    ))

    assert result["ok"] is True
    assert result["status"] == "briefed"
    assert len(result["runs"]) == 2
    assert (tmp_path / "rd_evidence-rtest-watsonx.json").is_file()
    assert (tmp_path / "rd_evidence-rtest-aws.json").is_file()


def test_run_autonomy_blocks_dirty_repo_by_default(monkeypatch, tmp_path):
    monkeypatch.setattr(autonomia, "autonomy_status", lambda **_kwargs: {
        "ready": False,
        "blockers": ["repo_dirty"],
    })

    result = autonomia.run_autonomy(autonomia.RunOptions(
        areas=("rd_evidence",),
        providers=("watsonx",),
        out_dir=str(tmp_path),
    ))

    assert result["ok"] is False
    assert result["status"] == "blocked"
    assert result["errors"] == ["repo_dirty"]
    assert result["runs"] == []


def test_cli_autonomia_run_dry_run(tmp_path):
    result = runner.invoke(app, [
        "autonomia", "run",
        "--executor", "local",
        "--areas", "svg_pipeline",
        "--providers", "cerebras",
        "--round-id", "cli",
        "--out-dir", str(tmp_path),
        "--common-ledger", str(tmp_path / "common.jsonl"),
        "--batch-ledger", str(tmp_path / "batches.jsonl"),
        "--dry-run",
        "--allow-dirty",
        "--no-ollama",
    ])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "briefed"
    assert payload["runs"][0]["area"] == "svg_pipeline"
    assert (tmp_path / "svg_pipeline-cli-cerebras.json").is_file()


def test_mak_executor_delegates_run_over_ssh(monkeypatch):
    commands = []

    def fake_ssh(target, command, timeout=900):
        commands.append((target, command, timeout))
        return {"ok": True, "status": "briefed", "runs": []}

    monkeypatch.setattr(autonomia, "_ssh_json", fake_ssh)

    result = autonomia.run_autonomy(autonomia.RunOptions(
        areas=("mak_quality",),
        providers=("watsonx",),
        round_id="remote01",
        dry_run=True,
        executor="mak",
        ssh_target="mak@example",
        mak_repo="~/flujo",
    ))

    assert result["ok"] is True
    assert result["executor"] == "mak"
    assert commands[0][0] == "mak@example"
    assert "python3 -m flujo autonomia run" in commands[0][1]
    assert "--executor local" in commands[0][1]
    assert "--areas 'mak_quality'" in commands[0][1]


def test_ssh_json_preserves_completed_payload_with_review_exit(monkeypatch):
    class Result:
        returncode = 2
        stdout = '{"ok": false, "status": "completed", "runs": [{"status": "revise"}]}'
        stderr = ""

    monkeypatch.setattr(autonomia.subprocess, "run", lambda *args, **kwargs: Result())

    payload = autonomia._ssh_json("mak@example", "remote command")

    assert payload["status"] == "completed"
    assert payload["runs"][0]["status"] == "revise"
    assert payload["remote_exit_code"] == 2
