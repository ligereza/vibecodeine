"""Regression gates for fail-closed whole-box measurements."""

import tools.medir_organismo as organismo


def test_crontab_failure_is_unknown_not_zero(monkeypatch):
    monkeypatch.setattr(organismo, "sh_result", lambda *args, **kwargs: ("", "boom", False))

    active, paused, lines, available = organismo.cron_state()

    assert (active, paused, lines) == (0, 0, [])
    assert available is False


def test_snapshot_preserves_unknown_external_probes(monkeypatch):
    monkeypatch.setattr(organismo, "sh_result", lambda *args, **kwargs: ("", "boom", False))
    monkeypatch.setattr(organismo, "port_open", lambda _port: False)
    monkeypatch.setattr(organismo, "process_on", lambda _port: "")

    snapshot = organismo.heartbeat_snapshot(0, [], cron_available=False)

    assert snapshot["cron"]["available"] is False
    assert snapshot["organs"][-2]["alive"] is None
    assert snapshot["organs"][-1]["alive"] is None
    assert snapshot["branch_protection"]["available"] is False
    assert snapshot["branch_protection"]["classic_present"] is None
    assert snapshot["branch_protection"]["ruleset_count"] is None


def test_repository_snapshot_fails_closed_when_git_is_unavailable(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    monkeypatch.setattr(organismo, "REPOSITORIES", (("fixture", repo),))
    monkeypatch.setattr(organismo, "sh_result", lambda *args, **kwargs: ("", "boom", False))

    result = organismo.repository_snapshot()

    assert result == [{
        "name": "fixture",
        "path": str(repo),
        "available": False,
        "reason": "git_probe_failed",
    }]


def test_mount_snapshot_reports_mount_probe_without_remote_access(monkeypatch, tmp_path):
    mount = tmp_path / "mount"
    mount.mkdir()
    monkeypatch.setattr(organismo, "MOUNTS", (("fixture", mount),))
    calls = []

    def fake_sh_result(*args, **kwargs):
        calls.append(args)
        return "", "", True

    monkeypatch.setattr(organismo, "sh_result", fake_sh_result)

    result = organismo.mount_snapshot()

    assert result == [{
        "name": "fixture",
        "path": str(mount),
        "exists": True,
        "mounted": True,
        "probe": "ok",
    }]
    assert calls == [("mountpoint", "-q", str(mount))]
