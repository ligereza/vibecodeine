"""Pure tests for the MAK process guard and its cron entrypoint."""
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARDIA_PATH = ROOT / "cultura" / "mak_plataforma" / "guardia.py"
WATCHDOG_PATH = ROOT / "cultura" / "mak_plataforma" / "watchdog_mak.sh"
CURATORIA_GUARD_PATH = ROOT / "cultura" / "mak_curatoria" / "curatoria_guardia.sh"


def _load_guardia():
    spec = importlib.util.spec_from_file_location("mak_guardia", GUARDIA_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guardia = _load_guardia()


def test_old_orphaned_recursive_scan_is_a_candidate():
    assert guardia.is_stale_scan(
        "/usr/bin/grep -R -n --include=*.service /home/mak /etc/systemd",
        15 * 60,
        1,
        "",
    )


def test_old_scan_under_detached_shell_is_a_candidate():
    assert guardia.is_stale_scan(
        "rg --glob *.py /home/mak/flujo",
        16 * 60,
        241,
        "/bin/bash -c rg --glob *.py /home/mak/flujo",
    )


def test_guard_does_not_touch_young_or_non_recursive_commands():
    assert not guardia.is_stale_scan("grep /home/mak", 60 * 60, 1, "")
    assert not guardia.is_stale_scan(
        "grep -R /home/mak", 14 * 60, 1, ""
    )
    assert not guardia.is_stale_scan(
        "/usr/bin/python3 /home/mak/codex/iconos.py",
        60 * 60,
        1,
        "",
    )


def test_guard_can_discover_candidates_without_killing_them(monkeypatch):
    monkeypatch.setattr(
        guardia,
        "_process_table",
        lambda: {
            100: {
                "pid": 100,
                "ppid": 1,
                "command": "grep -R /home/mak",
                "started": 100.0,
            },
            101: {
                "pid": 101,
                "ppid": 1,
                "command": "/usr/bin/python3 /home/mak/codex/iconos.py",
                "started": 100.0,
            },
        },
    )
    found = guardia.stale_scan_candidates(now=100.0 + 20 * 60)
    assert [item["pid"] for item in found] == [100]
    assert guardia.reap_stale_scans(dry_run=True) == 1


def test_platform_watchdog_serializes_and_runs_process_guard():
    source = WATCHDOG_PATH.read_text(encoding="utf-8")
    assert 'exec 9>"$LOGDIR/watchdog.lock"' in source
    assert "flock -n 9" in source
    assert '"$GUARDIA" --reap-stale-scans' in source
    assert '>>"$LOGDIR/guardia.log"' in source
    assert "systemctl_user start" in source
    assert "systemctl_user restart" in source
    assert 'XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$mak_user_id}"' in source
    assert 'DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"' in source
    assert "user systemd bus unavailable: supervision deferred" in source
    assert "supervision check passed" in source
    assert "setsid" not in source
    assert "pgrep" not in source


def test_curatoria_guard_keeps_perception_attached_to_cron_lock():
    source = CURATORIA_GUARD_PATH.read_text(encoding="utf-8")
    assert "flock -n 9" in source
    assert "python3 percepcion.py correr" in source
    assert "setsid" not in source
    assert "nohup" not in source
    assert source.rstrip().endswith("2>&1")
