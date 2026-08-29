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

It changes nothing: not the crontab, not a service, not a file.

The output is Spanish because a person reads it; identifiers and comments are
English because tests/test_idioma_ratchet.py enforces that for new code, and it
caught the first version of this file.
"""
from __future__ import annotations

import json
import re
import shlex
import socket
import subprocess
from pathlib import Path

HOME = Path("/home/mak")
REPO = HOME / "flujo"
ORGANS = [("research", 8890), ("codex", 8891), ("plataforma", 8900)]


def sh(*args: str, timeout: int = 60) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              timeout=timeout).stdout
    except (subprocess.SubprocessError, OSError):
        return ""


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


def cron_state() -> tuple[int, int, list[str]]:
    text = sh("crontab", "-l")
    active = [x for x in text.splitlines()
              if x.strip() and not x.lstrip().startswith("#")]
    paused = [x for x in text.splitlines() if x.lstrip().startswith("# PAUSED")]
    return len(active), len(paused), paused


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
    path = Path(script.replace("~", str(HOME)))
    if not path.is_absolute():
        path = HOME / "plataforma" / path
    if not path.exists():
        return False
    if path.suffix == ".sh":
        # follow the symlink: several of these point into the repo, and the
        # execute bit that matters is the target's, not the link's.
        return bool(path.resolve().stat().st_mode & 0o111)
    probe = subprocess.run(
        [interpreter, "-c",
         f"import importlib.util as u;s=u.spec_from_file_location('x','{path}');"
         f"m=u.module_from_spec(s);s.loader.exec_module(m)"],
        capture_output=True, timeout=60)
    return probe.returncode == 0


def main() -> int:
    print("MAK, medido ahora. Solo lectura.\n")

    active, paused_count, paused_lines = cron_state()
    print(f"1. capa de cron: {'CORRIENDO' if active else 'PAUSADA'}"
          f"   ({active} activas, {paused_count} pausadas)")
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
    xio = sh("systemctl", "--user", "is-active", "mak-xio").strip()
    print(f"     {'lenguaje':<12} cli/cron  "
          f"{'pausado con el cron' if not active else 'segun cron'}")
    print(f"     {'xio_puente':<12} daemon    {xio or 'sin dato'}")
    print(f"     -> {alive} de 5 organos responden")

    print("\n3. proteccion de rama en main (hay un cron que mergea)")
    protection = sh("gh", "api", "repos/:owner/:repo/branches/main/protection")
    rules = sh("gh", "api", "repos/:owner/:repo/rules/branches/main")
    try:
        rule_count = len(json.loads(rules)) if rules.strip() else 0
    except json.JSONDecodeError:
        rule_count = 0
    if "Not Found" in protection or not protection.strip():
        print(f"     SIN proteccion clasica (404) y {rule_count} reglas de ruleset")
        print("     revisor.py --enforce llama a `gh pr merge`. No hay red.")
    else:
        print("     proteccion presente")

    print("\n4. reanudacion: cuantas lineas arrancarian")
    ok = 0
    failing: list[str] = []
    for line in paused_lines:
        found = target(line)
        if not found:
            continue
        if would_start(*found):
            ok += 1
        else:
            failing.append(found[1])
    print(f"     {ok} arrancarian, {len(failing)} no")
    for path in failing:
        print(f"       FALLA {path}")
    versioned = REPO / "cultura" / "mak_plataforma" / "crontab.mak"
    if versioned.exists():
        print(f"     el crontab sin pausar esta versionado: "
              f"{versioned.relative_to(REPO)}")

    print("\n5. entornos Python")
    for env in sorted(HOME.glob("venvs/*")) + [HOME / "plataforma/.venv",
                                               HOME / "research/.venv",
                                               REPO / ".venv"]:
        if (env / "bin" / "python").exists():
            size = sh("du", "-sh", str(env), timeout=90).split("\t")[0] or "?"
            print(f"     {size:>7}  {env}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
