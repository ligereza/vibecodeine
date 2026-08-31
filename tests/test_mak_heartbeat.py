# -*- coding: utf-8 -*-
"""tools/mak_heartbeat.py: silent when clean, loud only on drift.

Every measurement function is monkeypatched so these tests never touch the
real box (no crontab, no systemd, no docker, no network) and never depend on
whatever MAK happens to be doing right now. Each test fabricates an expected
state that disagrees with the faked "measured" state in exactly one way, in
both directions where the category allows it, and asserts the tool reports
that specific disagreement -- not just "something differs".
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"


def _load():
    spec = importlib.util.spec_from_file_location("mak_heartbeat_under_test",
                                                   TOOLS / "mak_heartbeat.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


heartbeat = _load()


BASE_EXPECTED = {
    "schema": "mak-expected-state-v1",
    "captured_at": "2026-08-30T00:00:00+00:00",
    "cron": {"active_lines": 23},
    "organs": {"research": {"port": 8890, "alive": True}},
    "systemd_user": {"mak-xio.service": "active"},
    "systemd_system": {"ollama.service": "active"},
    "docker_containers": ["searxng"],
    "file_gates": {"/home/mak/curatoria/AUTONOMY_ENABLE": True,
                   "/home/mak/codex/.token.disabled": False},
}


def _clean_measured():
    """A measured state that agrees with BASE_EXPECTED on every point."""
    return json.loads(json.dumps({
        "cron": {"active_lines": 23},
        "organs": {"research": {"port": 8890, "alive": True}},
        "systemd_user": {"mak-xio.service": "active"},
        "systemd_system": {"ollama.service": "active"},
        "docker_containers": ["searxng"],
        "file_gates": {"/home/mak/curatoria/AUTONOMY_ENABLE": True,
                       "/home/mak/codex/.token.disabled": False},
    }))


def test_diff_report_empty_when_everything_matches():
    assert heartbeat.diff_report(BASE_EXPECTED, _clean_measured()) == []


def test_cron_drift_23_to_0_is_reported():
    """The concrete incident this tool exists for: the crontab going from
    23 active lines to 0 without anyone noticing."""
    measured = _clean_measured()
    measured["cron"]["active_lines"] = 0
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any("cron" in line and "23" in line and "0" in line for line in lines)


def test_organ_stops_answering_is_reported():
    measured = _clean_measured()
    measured["organs"]["research"]["alive"] = False
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any("research" in line and "no responde" in line for line in lines)


def test_organ_that_should_be_down_comes_up_is_reported():
    """Drift runs both ways: something that should be OFF and started is as
    much a finding as something that should be alive and is not."""
    expected = json.loads(json.dumps(BASE_EXPECTED))
    expected["organs"]["research"]["alive"] = False
    measured = _clean_measured()
    measured["organs"]["research"]["alive"] = True
    lines = heartbeat.diff_report(expected, measured)
    assert any("research" in line and "debia estar caido" in line for line in lines)


def test_enabled_unit_gone_inactive_is_reported():
    measured = _clean_measured()
    measured["systemd_user"]["mak-xio.service"] = "inactive"
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any("mak-xio.service" in line and "'active'" in line
              and "'inactive'" in line for line in lines)


def test_system_unit_drift_is_reported():
    """System units (ollama, postgresql, docker, the Actions runner) must be
    watched the same way as user units."""
    measured = _clean_measured()
    measured["systemd_system"]["ollama.service"] = "inactive"
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any("ollama.service" in line for line in lines)


def test_file_gate_appearing_is_reported():
    measured = _clean_measured()
    measured["file_gates"]["/home/mak/codex/.token.disabled"] = True
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any(".token.disabled" in line and "aparecio" in line for line in lines)


def test_file_gate_disappearing_is_reported():
    measured = _clean_measured()
    measured["file_gates"]["/home/mak/curatoria/AUTONOMY_ENABLE"] = False
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any("AUTONOMY_ENABLE" in line and "desaparecio" in line for line in lines)


def test_docker_container_missing_and_extra_both_reported():
    measured = _clean_measured()
    measured["docker_containers"] = ["un-contenedor-fantasma"]
    lines = heartbeat.diff_report(BASE_EXPECTED, measured)
    assert any("searxng" in line and "no aparece" in line for line in lines)
    assert any("un-contenedor-fantasma" in line and "no estaba declarado" in line
              for line in lines)


def test_measure_against_is_driven_by_expected_keys(monkeypatch):
    """measure_against() must only look at what `expected` names -- it is
    the declared state that decides what gets measured, nothing hardcoded."""
    monkeypatch.setattr(heartbeat, "cron_active_lines", lambda: 0)
    monkeypatch.setattr(heartbeat, "port_open", lambda port: port == 8890)
    monkeypatch.setattr(heartbeat, "systemd_state",
                        lambda units, *, user: {u: "active" for u in units})
    monkeypatch.setattr(heartbeat, "docker_containers", lambda: {"searxng"})
    monkeypatch.setattr(heartbeat, "file_gate_exists", lambda path: True)

    expected = {
        "organs": {"research": {"port": 8890, "alive": True},
                  "codex": {"port": 9999, "alive": False}},
        "systemd_user": {"mak-xio.service": "active"},
        "systemd_system": {},
        "docker_containers": ["searxng"],
        "file_gates": {"/tmp/some-gate": True},
    }
    measured = heartbeat.measure_against(expected)
    assert measured["organs"]["research"]["alive"] is True
    assert measured["organs"]["codex"]["alive"] is False
    assert measured["systemd_user"] == {"mak-xio.service": "active"}
    assert measured["file_gates"] == {"/tmp/some-gate": True}
    assert heartbeat.diff_report(expected, measured) == []


def test_capture_reuses_watched_keys_from_existing_baseline(monkeypatch):
    """--capture on a machine that already has a baseline must keep watching
    the same organs/units/gates, only refreshing their values -- not fall
    back to the built-in defaults and silently stop watching something an
    operator added by hand."""
    monkeypatch.setattr(heartbeat, "cron_active_lines", lambda: 5)
    monkeypatch.setattr(heartbeat, "port_open", lambda port: False)
    monkeypatch.setattr(heartbeat, "systemd_state",
                        lambda units, *, user: {u: "inactive" for u in units})
    monkeypatch.setattr(heartbeat, "docker_containers", lambda: set())
    monkeypatch.setattr(heartbeat, "file_gate_exists", lambda path: False)

    existing = {
        "organs": {"custom-organ": {"port": 12345, "alive": True}},
        "systemd_user": {"custom.service": "active"},
        "systemd_system": {"custom-system.service": "active"},
        "docker_containers": ["whatever-was-running"],
        "file_gates": {"/tmp/custom-gate": True},
    }
    fresh = heartbeat.build_expected(existing)
    assert set(fresh["organs"]) == {"custom-organ"}
    assert fresh["organs"]["custom-organ"] == {"port": 12345, "alive": False}
    assert fresh["systemd_user"] == {"custom.service": "inactive"}
    assert fresh["systemd_system"] == {"custom-system.service": "inactive"}
    assert fresh["file_gates"] == {"/tmp/custom-gate": False}
    assert fresh["cron"]["active_lines"] == 5
    assert fresh["schema"] == heartbeat.SCHEMA


def test_capture_falls_back_to_defaults_with_no_prior_baseline(monkeypatch):
    monkeypatch.setattr(heartbeat, "cron_active_lines", lambda: 0)
    monkeypatch.setattr(heartbeat, "port_open", lambda port: False)
    monkeypatch.setattr(heartbeat, "systemd_state",
                        lambda units, *, user: {u: "inactive" for u in units})
    monkeypatch.setattr(heartbeat, "docker_containers", lambda: set())
    monkeypatch.setattr(heartbeat, "file_gate_exists", lambda path: False)
    monkeypatch.setattr(heartbeat, "discover_runner_units", lambda: [])

    fresh = heartbeat.build_expected(None)
    assert set(fresh["organs"]) == set(heartbeat.DEFAULT_ORGAN_PORTS)
    assert set(fresh["systemd_user"]) == set(heartbeat.DEFAULT_SYSTEMD_USER_UNITS)
    assert set(fresh["file_gates"]) == set(heartbeat.DEFAULT_FILE_GATES)


def test_silent_and_exit_zero_when_nothing_differs(tmp_path, monkeypatch, capsys):
    expected_path = tmp_path / "expected.json"
    expected_path.write_text(json.dumps(BASE_EXPECTED), encoding="utf-8")
    monkeypatch.setattr(heartbeat, "measure_against", lambda expected: _clean_measured())

    rc = heartbeat.main(["--expected", str(expected_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert out == ""  # sale 0 sin decir nada


def test_missing_baseline_is_exit_two_and_never_silent(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(heartbeat, "ntfy_publish", None)
    monkeypatch.setattr(heartbeat, "load_env", None)
    rc = heartbeat.main(["--expected", str(tmp_path / "does_not_exist.json")])
    out = capsys.readouterr().out
    assert rc == 2
    assert "captur" in out.lower()


def test_drift_is_printed_and_notify_is_attempted(tmp_path, monkeypatch, capsys):
    expected_path = tmp_path / "expected.json"
    expected_path.write_text(json.dumps(BASE_EXPECTED), encoding="utf-8")

    def _drifted(expected):
        measured = _clean_measured()
        measured["cron"]["active_lines"] = 0
        return measured

    monkeypatch.setattr(heartbeat, "measure_against", _drifted)
    calls = []
    monkeypatch.setattr(heartbeat, "notify_or_log",
                        lambda lines, *, topic_override="": calls.append(lines) or True)

    rc = heartbeat.main(["--expected", str(expected_path)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "MAK latido" in out
    assert calls and any("cron" in line for line in calls[0])


def test_notify_degrades_to_log_without_a_topic(monkeypatch, capsys):
    """No topic configured -> logged, never a silent no-op."""
    sent = []
    monkeypatch.setattr(heartbeat, "ntfy_publish",
                        lambda *a, **k: sent.append((a, k)) or False)
    monkeypatch.setattr(heartbeat, "load_env", lambda: None)
    monkeypatch.delenv("NTFY_TOPIC_OUT", raising=False)
    monkeypatch.delenv("MAK_HEARTBEAT_NTFY_TOPIC", raising=False)

    ok = heartbeat.notify_or_log(["algo cambio"])
    out = capsys.readouterr().out
    assert ok is False
    assert not sent  # never even tried to publish without a topic
    assert "sin tema configurado" in out
    assert "degradando a log" in out


def test_notify_degrades_to_log_when_publish_fails(monkeypatch, capsys):
    monkeypatch.setattr(heartbeat, "load_env", lambda: None)
    monkeypatch.setattr(heartbeat, "ntfy_publish",
                        lambda topic, message, **k: False)
    monkeypatch.setenv("MAK_HEARTBEAT_NTFY_TOPIC", "some-topic")

    ok = heartbeat.notify_or_log(["algo cambio"])
    out = capsys.readouterr().out
    assert ok is False
    assert "fallo el envio" in out
    assert "degradando a log" in out


def test_capture_writes_and_reports(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(heartbeat, "cron_active_lines", lambda: 0)
    monkeypatch.setattr(heartbeat, "port_open", lambda port: False)
    monkeypatch.setattr(heartbeat, "systemd_state",
                        lambda units, *, user: {u: "inactive" for u in units})
    monkeypatch.setattr(heartbeat, "docker_containers", lambda: set())
    monkeypatch.setattr(heartbeat, "file_gate_exists", lambda path: False)
    monkeypatch.setattr(heartbeat, "discover_runner_units", lambda: [])

    out_path = tmp_path / "captured.json"
    rc = heartbeat.main(["--capture", "--expected", str(out_path)])
    printed = capsys.readouterr().out
    assert rc == 0
    assert out_path.exists()
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert saved["schema"] == heartbeat.SCHEMA
    assert "linea base capturada" in printed


def test_tool_is_read_only_over_mak():
    """No function in this module invokes anything that could change MAK:
    no crontab write, no service start/stop, no docker run/stop/rm."""
    source = (TOOLS / "mak_heartbeat.py").read_text(encoding="utf-8")
    forbidden = ("crontab -", "systemctl start", "systemctl stop",
                "systemctl restart", "systemctl enable", "systemctl disable",
                "docker run", "docker stop", "docker rm", "docker start")
    offenders = [f for f in forbidden if f in source]
    assert not offenders, offenders
