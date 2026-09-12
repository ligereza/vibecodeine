#!/usr/bin/env python3
"""Measure the MAK organism and print it. Read-only.

This exists because docs/MAK_ORGANISMO.md reached 496 lines of prose in a repo
whose diagnosed problem was prose, and because rule 3 of docs/AUTORIDAD.md says
no measured figure is written without its measurement date. The answer is not to
write it: run this.

Usage:
    python3 tools/medir_organismo.py

What it answers, in order of consequence:
    1. how many cron lines are active and how many paused
    2. which of the five organs declared in /home/mak/GENESIS.md respond
    3. whether `main` has branch protection, because a cron line merges PRs
    4. how many cron lines would start if resumed
    5. the Python environments and their size
    6. the bounded Git state of the active component checkouts

It changes nothing: not the crontab, not a service, not a file.

The output is Spanish because a person reads it; identifiers and comments are
English because tests/test_idioma_ratchet.py enforces that for new code, and it
caught the first version of this file.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
import shlex
import shutil
import socket
import subprocess
from pathlib import Path

HOME = Path("/home/mak")
REPO = HOME / "flujo"
ORGANS = [("research", 8890), ("codex", 8891), ("plataforma", 8900)]
REPOSITORIES = (
    ("MAK", HOME),
    ("FLUJO", REPO),
    ("XIO", HOME / "XIO"),
    ("LUCIDA", HOME / "LUCIDA"),
    ("WACHUMA", HOME / "WACHUMA"),
    ("FARMAKSIA", HOME / "FARMAKSIA"),
    ("VIZZ", HOME / "VIZZ"),
    ("IRIS", HOME / "IRIS"),
    ("bucle", HOME / "bucle"),
    ("PUPILA", HOME / "PUPILA"),
)
MOUNTS = (
    ("google_drive", HOME / "GoogleDrive"),
    ("onedrive", HOME / "OneDrive"),
)


def sh_result(*args: str, timeout: int = 60) -> tuple[str, str, bool]:
    """Run a probe and preserve whether it actually ran successfully."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True,
                              timeout=timeout, check=False)
        return proc.stdout, proc.stderr, proc.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return "", "", False


def sh(*args: str, timeout: int = 60) -> str:
    """Compatibility helper for non-verdict display probes."""
    return sh_result(*args, timeout=timeout)[0]


def port_open(port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(1.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def process_on(port: int) -> str:
    for line in sh("ss", "-ltnp").splitlines():
        if f":{port} " in line and "pid=" in line:
            found = re.search(r"pid=(\d+)", line)
            if found:
                cmd = sh("ps", "-o", "cmd=", "-p", found.group(1)).strip()
                return f"pid {found.group(1)}  {cmd[:78]}"
    return ""


def cron_state() -> tuple[int, int, list[str], bool]:
    text, _stderr, ok = sh_result("crontab", "-l")
    if not ok:
        return 0, 0, [], False
    active = [x for x in text.splitlines()
              if x.strip() and not x.lstrip().startswith("#")]
    paused = [x for x in text.splitlines() if x.lstrip().startswith("# PAUSED")]
    return len(active), len(paused), paused, True


def target(line: str):
    """(interpreter, script) for a cron line, or None."""
    body = re.sub(r"^#\s*PAUSED[A-Z0-9-]*\s*", "", line).strip()
    body = re.sub(r"^([^ ]+ +){5}", "", body)
    body = body.split("#")[0].split(">>")[0].split(">")[0].strip()
    if not body:
        return None
    try:
        parts = shlex.split(body)
    except ValueError:
        parts = body.split()
    interpreter = ""
    for part in parts:
        if part in ("cd", "&&") or part.startswith("~") or part.endswith("plataforma"):
            continue
        if part.endswith(("python3", "python")):
            interpreter = part
            continue
        if part.endswith((".py", ".sh")):
            return interpreter or "/usr/bin/python3", part
    return None


def would_start(interpreter: str, script: str) -> bool:
    return static_readiness(interpreter, script)[0]


def script_path(script: str) -> Path:
    path = Path(script.replace("~", str(HOME)))
    return path if path.is_absolute() else HOME / "plataforma" / path


def static_readiness(interpreter: str, script: str) -> tuple[bool, str]:
    """Check a cron target without importing or executing its module."""
    path = script_path(script)
    if not path.is_file():
        return False, "script_missing"
    if interpreter.startswith("/"):
        if not Path(interpreter).is_file():
            return False, "interpreter_missing"
    elif not shutil.which(interpreter):
        return False, "interpreter_missing"
    if path.suffix == ".sh":
        if not bool(path.resolve().stat().st_mode & 0o111):
            return False, "shell_not_executable"
        probe = subprocess.run(["/bin/bash", "-n", str(path)], capture_output=True,
                               text=True, timeout=30)
        return probe.returncode == 0, "ready" if probe.returncode == 0 else "shell_syntax"
    if path.suffix == ".py":
        try:
            compile(path.read_bytes(), str(path), "exec")
        except (OSError, SyntaxError):
            return False, "python_syntax"
    return True, "ready"


def cron_details(paused_lines: list[str]) -> list[dict[str, str | int | bool | None]]:
    """Return one static preflight record per paused cron line."""
    details: list[dict[str, str | int | bool | None]] = []
    for number, line in enumerate(paused_lines, 1):
        match = re.match(r"^#\s*(?P<marker>PAUSED[^\s]*)\s+(?P<body>.*)$", line)
        body = match.group("body") if match else line.lstrip("# ")
        fields = body.split(maxsplit=5)
        schedule = " ".join(fields[:5]) if len(fields) >= 5 else ""
        command = fields[5].strip() if len(fields) == 6 else ""
        found = target(line)
        interpreter = found[0] if found else None
        script = found[1] if found else None
        ready, reason = static_readiness(interpreter, script) if found else (False, "target_unparsed")
        details.append({
            "number": number,
            "marker": match.group("marker") if match else "",
            "schedule": schedule,
            "command": command,
            "interpreter": interpreter,
            "script": str(script_path(script)) if script else None,
            "static_ready": ready,
            "reason": reason,
        })
    return details


def repository_snapshot() -> list[dict[str, object]]:
    """Measure bounded Git transport state without fetch, checkout or writes."""
    rows: list[dict[str, object]] = []
    for name, path in REPOSITORIES:
        if not (path / ".git").exists():
            rows.append({"name": name, "path": str(path), "available": False,
                         "reason": "git_missing"})
            continue
        branch, branch_err, branch_ok = sh_result(
            "git", "-C", str(path), "branch", "--show-current")
        head, head_err, head_ok = sh_result(
            "git", "-C", str(path), "rev-parse", "--short", "HEAD")
        if not branch_ok or not head_ok:
            rows.append({"name": name, "path": str(path), "available": False,
                         "reason": "git_probe_failed"})
            continue
        status, _status_err, status_ok = sh_result(
            "git", "-C", str(path), "status", "--porcelain=v1")
        upstream, _upstream_err, upstream_ok = sh_result(
            "git", "-C", str(path), "rev-parse", "--abbrev-ref",
            "--symbolic-full-name", "@{upstream}")
        upstream_name = upstream.strip() if upstream_ok and upstream.strip() else None
        default_remote, _default_err, default_ok = sh_result(
            "git", "-C", str(path), "symbolic-ref", "--quiet", "--short",
            "refs/remotes/origin/HEAD"
        )
        branch_ref = f"refs/remotes/origin/{branch.strip()}"
        _remote_branch, _remote_branch_err, remote_branch_ok = sh_result(
            "git", "-C", str(path), "show-ref", "--verify", "--quiet", branch_ref
        )
        ahead = behind = None
        if upstream_name:
            transport, _transport_err, transport_ok = sh_result(
                "git", "-C", str(path), "rev-list", "--left-right", "--count",
                "HEAD...@{upstream}")
            if transport_ok:
                fields = transport.split()
                if len(fields) == 2 and all(field.isdigit() for field in fields):
                    ahead, behind = int(fields[0]), int(fields[1])
        rows.append({
            "name": name,
            "path": str(path),
            "available": True,
            "branch": branch.strip(),
            "head": head.strip(),
            "upstream": upstream_name,
            "origin_default": default_remote.strip() if default_ok and default_remote.strip() else None,
            "branch_published": remote_branch_ok,
            "ahead": ahead,
            "behind": behind,
            "dirty_files": len(status.splitlines()) if status_ok else None,
            "status_probe": "ok" if status_ok else "failed",
        })
    return rows


def mount_snapshot() -> list[dict[str, object]]:
    """Measure configured FUSE mountpoints without touching remote contents."""
    rows: list[dict[str, object]] = []
    for name, path in MOUNTS:
        exists = path.exists()
        if not exists:
            rows.append({"name": name, "path": str(path), "exists": False,
                         "mounted": False, "probe": "path_missing"})
            continue
        _stdout, stderr, ok = sh_result("mountpoint", "-q", str(path))
        probe = "ok" if ok or not stderr else "failed"
        rows.append({"name": name, "path": str(path), "exists": True,
                     "mounted": ok if probe == "ok" else None, "probe": probe})
    return rows


def heartbeat_snapshot(active: int, paused_lines: list[str],
                       *, cron_available: bool = True) -> dict[str, object]:
    """Emit a machine-readable organism pulse without changing the machine."""
    protection, protection_err, protection_ok = sh_result(
        "gh", "api", "repos/:owner/:repo/branches/main/protection")
    rules, rules_err, rules_ok = sh_result(
        "gh", "api", "repos/:owner/:repo/rules/branches/main")
    protection_not_found = "not found" in (protection + protection_err).lower()
    rules_not_found = "not found" in (rules + rules_err).lower()
    try:
        rule_count = (len(json.loads(rules)) if rules.strip() else 0) \
            if rules_ok or rules_not_found else None
    except json.JSONDecodeError:
        rule_count = None
    organs = []
    for name, port in ORGANS:
        organs.append({"name": name, "port": port, "alive": port_open(port),
                       "process": process_on(port)})
    organs.extend([
        {"name": "lenguaje", "port": None,
         "alive": bool(active) if cron_available else None,
         "process": ("cron" if active else "cron_paused")
                    if cron_available else "unknown"},
    ])
    xio, _xio_err, xio_ok = sh_result("systemctl", "--user", "is-active", "mak-xio")
    xio = xio.strip()
    xio_known = xio_ok or xio in {"active", "inactive", "failed", "dead"}
    organs.append({"name": "xio_puente", "port": None,
                   "alive": xio == "active" if xio_known else None,
                   "process": xio or "unknown"})
    details = cron_details(paused_lines)
    return {
        "schema": "mak-organism-heartbeat-v1",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "cron": {
            "available": cron_available,
            "active_lines": active,
            "paused_lines": len(paused_lines),
            "static_ready_lines": sum(bool(row["static_ready"]) for row in details),
            "details": details,
        },
        "organs": organs,
        "repositories": repository_snapshot(),
        "mounts": mount_snapshot(),
        "branch_protection": {
            "available": protection_ok or protection_not_found,
            "classic_present": (bool(protection.strip()) and not protection_not_found)
                               if protection_ok or protection_not_found else None,
            "ruleset_count": rule_count,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cron-detail", action="store_true",
                        help="mostrar preflight estatico de cada linea pausada")
    parser.add_argument("--json", action="store_true",
                        help="emitir el pulso del organismo como JSON")
    args = parser.parse_args(argv)

    active, paused_count, paused_lines, cron_available = cron_state()
    if args.json:
        print(json.dumps(heartbeat_snapshot(
            active, paused_lines, cron_available=cron_available),
            ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if cron_available else 1

    print("MAK, medido ahora. Solo lectura.\n")

    if cron_available:
        print(f"1. capa de cron: {'CORRIENDO' if active else 'PAUSADA'}"
              f"   ({active} activas, {paused_count} pausadas)")
    else:
        print("1. capa de cron: INDETERMINADA (no se pudo leer crontab)")
    for mark in sorted({m for x in paused_lines
                        for m in re.findall(r"PAUSED[A-Z0-9-]*", x)}):
        print(f"     marca: {mark}  ({sum(1 for x in paused_lines if mark in x)} lineas)")

    print("\n2. organos declarados en /home/mak/GENESIS.md")
    alive = 0
    for name, port in ORGANS:
        if port_open(port):
            alive += 1
            print(f"     {name:<12} :{port}  VIVO   {process_on(port)}")
        else:
            print(f"     {name:<12} :{port}  caido")
    xio, _xio_err, xio_ok = sh_result("systemctl", "--user", "is-active", "mak-xio")
    xio = xio.strip()
    xio_known = xio_ok or xio in {"active", "inactive", "failed", "dead"}
    print(f"     {'lenguaje':<12} cli/cron  "
          f"{'pausado con el cron' if not active else 'segun cron'}"
          if cron_available else "     lenguaje     cli/cron  indeterminado")
    print(f"     {'xio_puente':<12} daemon    {xio if xio_known else 'indeterminado'}")
    print(f"     -> {alive} de 5 organos responden")

    print("\n3. proteccion de rama en main (hay un cron que mergea)")
    protection, protection_err, protection_ok = sh_result(
        "gh", "api", "repos/:owner/:repo/branches/main/protection")
    rules, rules_err, rules_ok = sh_result(
        "gh", "api", "repos/:owner/:repo/rules/branches/main")
    protection_not_found = "not found" in (protection + protection_err).lower()
    rules_not_found = "not found" in (rules + rules_err).lower()
    try:
        rule_count = (len(json.loads(rules)) if rules.strip() else 0) \
            if rules_ok or rules_not_found else None
    except json.JSONDecodeError:
        rule_count = None
    if (protection_ok or protection_not_found) and (rules_ok or rules_not_found) \
            and (protection_not_found or not protection.strip()):
        print(f"     SIN proteccion clasica (404) y {rule_count} reglas de ruleset")
        print("     revisor.py --enforce llama a `gh pr merge`. No hay red.")
    elif not protection_ok or not rules_ok:
        print("     INDETERMINADA: no se pudo medir la proteccion de main")
    else:
        print("     proteccion presente")

    print("\n4. reanudacion: preflight estatico de lineas")
    details = cron_details(paused_lines)
    ok = sum(bool(row["static_ready"]) for row in details)
    failing = [str(row["script"] or row["command"]) for row in details
               if not row["static_ready"]]
    print(f"     {ok} listas, {len(failing)} con fallo estatico")
    for path in failing:
        print(f"       FALLA {path}")
    versioned = REPO / "cultura" / "mak_plataforma" / "crontab.mak"
    if versioned.exists():
        print(f"     el crontab sin pausar esta versionado: "
              f"{versioned.relative_to(REPO)}")
    if args.cron_detail:
        print("\n4b. detalle de reanudacion")
        for row in details:
            status = "LISTA" if row["static_ready"] else "FALLA"
            print(f"     {int(row['number']):02d} {status:<5} {row['marker']:<36} "
                  f"{row['schedule']:<14} {row['reason']:<20} {row['script'] or row['command']}")

    print("\n5. entornos Python")
    for env in sorted(HOME.glob("venvs/*")) + [HOME / "plataforma/.venv",
                                               HOME / "research/.venv",
                                               REPO / ".venv"]:
        if (env / "bin" / "python").exists():
            size = sh("du", "-sh", str(env), timeout=90).split("\t")[0] or "?"
            print(f"     {size:>7}  {env}")
    print("\n6. repositorios: estado Git acotado (sin fetch ni escritura)")
    for row in repository_snapshot():
        if not row["available"]:
            print(f"     {row['name']:<10} no disponible ({row['reason']})")
            continue
        transport = (
            f"sin upstream; origin_default={row['origin_default']} "
            f"branch_published={'si' if row['branch_published'] else 'no'}"
            if row["upstream"] is None else f"ahead={row['ahead']} behind={row['behind']}"
        )
        print(f"     {row['name']:<10} {row['branch'] or '(detached)':<36} "
              f"{row['head']}  dirty={row['dirty_files']}  {transport}")
    print("\n7. mounts FUSE")
    for row in mount_snapshot():
        if row["probe"] == "failed":
            state = "INDETERMINADO"
        else:
            state = "MONTADO" if row["mounted"] else "NO MONTADO"
        print(f"     {row['name']:<12} {state:<13} {row['path']}")
    return 0 if cron_available else 1


if __name__ == "__main__":
    raise SystemExit(main())
