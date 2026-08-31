#!/usr/bin/env python3
"""Compare MAK's measured state against a declared expected state. Read-only.

This exists because MAK was stopped for two weeks (crontab paused 2026-08-14,
CI red for six runs, one organ down) and nobody noticed: the test suite was
green and the hub answered, and neither of those was the signal that mattered.
`tools/medir_organismo.py` and `indexes/mak-procesos-20260829/medir_procesos.py`
can measure the real state, but they only speak when invoked, and only someone
who already suspects something is wrong invokes them. This tool does the other
half: it invokes itself (from cron, once resumed) and only ever speaks when the
measured state disagrees with a state someone declared on purpose.

What "expected state" means: a JSON file, versioned in the repo
(`data/mak_expected_state.json` by default), listing how many cron lines
should be active, which organs should answer and on what port, which systemd
units -- user AND system: ollama, postgresql, docker and the Actions runner
also count -- should be `active`, which file gates should exist, and which
docker containers should be running. Nothing here is guessed: `--capture`
measures the box right now and writes that as the new expected state, which
is how an operator fixes the baseline after resuming MAK on purpose.

Drift is bidirectional by design: something that should be alive and does not
answer is exactly as much a finding as something that should be off and came
up. Every category below is diffed both ways.

Usage:
    python3 tools/mak_heartbeat.py                 # compare, silent if clean
    python3 tools/mak_heartbeat.py --capture        # write current state as expected
    python3 tools/mak_heartbeat.py --expected P.json --topic ntfy-topic

Exit codes: 0 nothing to report (including a clean --capture). 1 drift found
(printed and, if a topic is configured, sent to ntfy). 2 no expected state is
declared yet, so nothing could be compared.

It changes nothing on MAK: no crontab edit, no service start or stop, no file
gate touched, no container managed. The notification path reuses
`ntfy_publish`/`load_env` from `cultura/mak_research/research_lib.py` on
purpose -- the whole point is one shared client, not a second one that drifts
from the first. If no ntfy topic is configured, or the send fails, this
degrades to a log line and SAYS so; it never fails silently, which is the
exact defect it exists to correct.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path("/home/mak")
REPO = Path(__file__).resolve().parents[1]
DEFAULT_EXPECTED = REPO / "data" / "mak_expected_state.json"
SCHEMA = "mak-expected-state-v1"

# Used only when no expected file exists yet, so a first --capture has
# something sensible to start from. Once a baseline exists, later captures
# keep whatever keys the (possibly hand-edited) baseline already declares.
DEFAULT_ORGAN_PORTS = {"research": 8890, "codex": 8891, "plataforma": 8900}
DEFAULT_SYSTEMD_USER_UNITS = (
    "mak-hub.service", "mak-codex.service", "mak-research.service",
    "mak-xio.service",
)
DEFAULT_SYSTEMD_SYSTEM_UNITS = (
    "ollama.service", "postgresql@15-main.service", "docker.service",
)
DEFAULT_FILE_GATES = (
    str(HOME / "curatoria" / "AUTONOMY_ENABLE"),
    str(HOME / "codex" / ".token.disabled"),
    str(HOME / "research" / ".cola.disabled.missing_ntfy"),
)

# research_lib is the one place `ntfy_publish`/`load_env` live in MAK; import
# it the same way tools/execute_research_job.py does. Guarded: a missing or
# broken research_lib must degrade to a log, not crash a read-only monitor.
sys.path.insert(0, str(REPO / "cultura" / "mak_research"))
try:
    from research_lib import load_env, ntfy_publish  # noqa: E402
except ImportError:
    load_env = None
    ntfy_publish = None


def sh(*args: str, timeout: int = 30) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              timeout=timeout, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def port_open(port: int | None) -> bool:
    if not port:
        return False
    with socket.socket() as sock:
        sock.settimeout(1.5)
        return sock.connect_ex(("127.0.0.1", int(port))) == 0


def cron_active_lines() -> int:
    text = sh("crontab", "-l")
    return sum(1 for line in text.splitlines()
               if line.strip() and not line.lstrip().startswith("#"))


def docker_containers() -> set[str]:
    out = sh("docker", "ps", "--format", "{{.Names}}")
    return {line.strip() for line in out.splitlines() if line.strip()}


def systemd_state(units: list[str], *, user: bool) -> dict[str, str]:
    """One `is-active` call for every unit, in order. Never raises: a unit
    that does not exist still gets a line (`unknown`/`inactive`), it just
    should not vanish from the dict."""
    units = list(units)
    if not units:
        return {}
    cmd = ["systemctl"] + (["--user"] if user else []) + ["is-active"] + units
    states = sh(*cmd).splitlines()
    while len(states) < len(units):
        states.append("unknown")
    return dict(zip(units, states))


def discover_runner_units() -> list[str]:
    """The GitHub Actions runner's unit name is host-specific
    (`actions.runner.<org>.<host>.service`), so find it instead of guessing."""
    found = []
    for line in sh("systemctl", "list-unit-files", "--no-pager", "--plain").splitlines():
        parts = line.split()
        if parts and parts[0].startswith("actions.runner.") and parts[0].endswith(".service"):
            found.append(parts[0])
    return found


def file_gate_exists(path: str) -> bool:
    return Path(os.path.expanduser(path)).exists()


def _measure_common(organ_ports: dict[str, int],
                    systemd_user_units: list[str],
                    systemd_system_units: list[str],
                    gate_paths: list[str]) -> dict:
    return {
        "cron": {"active_lines": cron_active_lines()},
        "organs": {name: {"port": port, "alive": port_open(port)}
                  for name, port in organ_ports.items()},
        "systemd_user": systemd_state(systemd_user_units, user=True),
        "systemd_system": systemd_state(systemd_system_units, user=False),
        "docker_containers": sorted(docker_containers()),
        "file_gates": {path: file_gate_exists(path) for path in gate_paths},
    }


def build_expected(existing: dict | None) -> dict:
    """Measure the box now and shape it as an expected-state document.

    Reuses the WATCHED identifiers (organ names/ports, unit names, gate
    paths) from `existing` when there is a prior baseline, so a re-capture
    after resuming MAK updates the values without silently dropping something
    an operator added by hand. Docker containers are the exception: the
    expected list is always whatever is running at capture time, because
    there is no separate declaration of "which containers" to preserve.
    """
    existing = existing or {}
    organ_ports = ({name: info.get("port") for name, info in
                   (existing.get("organs") or {}).items()}
                  or dict(DEFAULT_ORGAN_PORTS))
    systemd_user_units = (list((existing.get("systemd_user") or {}).keys())
                         or list(DEFAULT_SYSTEMD_USER_UNITS))
    systemd_system_units = (list((existing.get("systemd_system") or {}).keys())
                           or list(DEFAULT_SYSTEMD_SYSTEM_UNITS) + discover_runner_units())
    gate_paths = (list((existing.get("file_gates") or {}).keys())
                 or list(DEFAULT_FILE_GATES))

    data = _measure_common(organ_ports, systemd_user_units,
                           systemd_system_units, gate_paths)
    data["schema"] = SCHEMA
    data["captured_at"] = datetime.now(timezone.utc).isoformat()
    return data


def measure_against(expected: dict) -> dict:
    """Measure only what `expected` declares -- the expected state drives
    what gets checked, nothing is hardcoded here beyond cron."""
    organ_ports = {name: info.get("port") for name, info in
                  (expected.get("organs") or {}).items()}
    systemd_user_units = list((expected.get("systemd_user") or {}).keys())
    systemd_system_units = list((expected.get("systemd_system") or {}).keys())
    gate_paths = list((expected.get("file_gates") or {}).keys())
    return _measure_common(organ_ports, systemd_user_units,
                           systemd_system_units, gate_paths)


def diff_report(expected: dict, measured: dict) -> list[str]:
    """Every finding is bidirectional: a mismatch is a mismatch whichever way
    it points. Returns an empty list when nothing differs."""
    lines: list[str] = []

    exp_cron = (expected.get("cron") or {}).get("active_lines")
    got_cron = (measured.get("cron") or {}).get("active_lines")
    if exp_cron is not None and exp_cron != got_cron:
        lines.append(f"cron: se esperaban {exp_cron} lineas activas, hay {got_cron}")

    for name, info in (expected.get("organs") or {}).items():
        exp_alive = bool(info.get("alive"))
        got_alive = bool((measured.get("organs") or {}).get(name, {}).get("alive"))
        if exp_alive != got_alive:
            status_word = "responde" if got_alive else "no responde"
            expected_word = "debia responder" if exp_alive else "debia estar caido"
            lines.append(f"organo {name} (puerto {info.get('port')}): "
                        f"{expected_word} y ahora {status_word}")

    for user, label, key in ((True, "usuario", "systemd_user"),
                             (False, "sistema", "systemd_system")):
        for unit, exp_state in (expected.get(key) or {}).items():
            got_state = (measured.get(key) or {}).get(unit)
            if exp_state != got_state:
                lines.append(f"unidad systemd de {label} {unit}: "
                            f"se esperaba '{exp_state}', esta '{got_state}'")

    exp_docker = set(expected.get("docker_containers") or [])
    got_docker = set(measured.get("docker_containers") or [])
    for missing in sorted(exp_docker - got_docker):
        lines.append(f"contenedor docker '{missing}': deberia estar "
                    f"corriendo y no aparece")
    for extra in sorted(got_docker - exp_docker):
        lines.append(f"contenedor docker '{extra}': esta corriendo y no "
                    f"estaba declarado")

    for path, exp_bool in (expected.get("file_gates") or {}).items():
        got_bool = (measured.get("file_gates") or {}).get(path)
        if bool(exp_bool) != bool(got_bool):
            change_word = "aparecio" if got_bool else "desaparecio"
            lines.append(f"freno de archivo {path}: {change_word} "
                        f"(se esperaba existe={bool(exp_bool)})")

    return lines


def load_expected(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_expected(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
                    + "\n", encoding="utf-8")


def notify_or_log(lines: list[str], *, topic_override: str = "") -> bool:
    """Send the drift to ntfy, or say clearly why it did not go out.

    Never raises and never returns silently: the caller always gets a printed
    line explaining what happened to the notification, because a monitor that
    fails to alert without saying so recreates the exact problem it exists
    to fix.
    """
    if ntfy_publish is None or load_env is None:
        print("ntfy: research_lib no se pudo importar -- degradando a log, "
             "no se envio notificacion")
        return False
    load_env()
    topic = (topic_override or os.environ.get("MAK_HEARTBEAT_NTFY_TOPIC", "")
            or os.environ.get("NTFY_TOPIC_OUT", ""))
    if not topic:
        print("ntfy: sin tema configurado (NTFY_TOPIC_OUT / "
             "MAK_HEARTBEAT_NTFY_TOPIC) -- degradando a log, no se envio "
             "notificacion")
        return False
    errors: list[str] = []
    sent = ntfy_publish(topic, "\n".join(lines),
                        title="MAK latido: diferencia de estado",
                        priority="high", errors=errors)
    if sent:
        print(f"ntfy: notificacion enviada a {topic}")
    else:
        detail = "; ".join(errors) or "error desconocido"
        print(f"ntfy: fallo el envio a {topic} ({detail}) -- degradando a log")
    return sent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--expected", default=str(DEFAULT_EXPECTED),
                        help="path to the versioned expected-state JSON")
    parser.add_argument("--capture", action="store_true",
                        help="measure the box now and save it as the expected state")
    parser.add_argument("--topic", default="",
                        help="ntfy topic override (default: research.env)")
    parser.add_argument("--json", action="store_true",
                        help="on drift, also print the machine-readable diff")
    args = parser.parse_args(argv)
    expected_path = Path(args.expected)

    if args.capture:
        data = build_expected(load_expected(expected_path))
        save_expected(expected_path, data)
        print(f"linea base capturada: {expected_path}")
        print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    expected = load_expected(expected_path)
    if expected is None:
        msg = (f"no hay estado esperado declarado en {expected_path} -- "
              "correr con --capture para fijar una linea base antes de poder "
              "comparar")
        print(msg)
        notify_or_log([msg], topic_override=args.topic)
        return 2

    measured = measure_against(expected)
    diffs = diff_report(expected, measured)
    if not diffs:
        return 0  # todo calza: silencio total, exit 0

    print(f"MAK latido: {len(diffs)} diferencia(s) contra {expected_path}")
    for line in diffs:
        print("  - " + line)
    if args.json:
        print(json.dumps({"expected": expected, "measured": measured,
                          "diffs": diffs}, ensure_ascii=False, indent=2,
                         sort_keys=True))
    notify_or_log(diffs, topic_override=args.topic)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
