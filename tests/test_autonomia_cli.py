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
        "canonical_present": {
            "main": True,
            "mak": True,
            "rd": True,
            "iskvw": True,
        },
        "extra_remote_branches": [],
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


def test_autonomy_status_derives_operational_surface(monkeypatch, tmp_path):
    monkeypatch.setattr(autonomia, "_branch_state", lambda: {
        "current": "mak",
        "dirty": [],
        "remote_branches": ["main", "mak", "rd", "iskvw"],
        "canonical_present": {name: True for name in autonomia.CANONICAL_BRANCHES},
        "extra_remote_branches": [],
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
        "--providers", "watsonx",
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
    assert (tmp_path / "svg_pipeline-cli-watsonx.json").is_file()


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
