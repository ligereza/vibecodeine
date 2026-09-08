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
