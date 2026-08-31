#!/usr/bin/env python3
"""Install the non-destructive MAK deploy path.

The human checkout at ``/home/mak/flujo`` is never reset, checked out, or used
as the deployment worktree. The deploy worktree is disposable and the live
mirror receives only a clean ``origin/main`` commit through
``sync_mak_safe.py``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
from pathlib import Path

HOST = "%s@%s" % (os.environ.get("MAK_USER", "mak"),
                  os.environ.get("MAK_HOST", "192.168.50.2"))
SAFE_SCRIPT = Path(__file__).with_name("sync_mak_safe.py")
REMOTE = r'''set -eu
STAMP=$(date +%Y%m%d_%H%M%S)
REPO="$HOME/flujo"
DEPLOY="$HOME/flujo-deploy"
BACKUPS="$HOME/plataforma/backups"
say() { printf '\n@@ %s @@\n' "$1"; }
fail() { say BLOCKED; printf '%s\n' "$1"; exit 20; }

[ -d "$REPO/.git" ] || fail "No existe checkout humano en $REPO"
if [ -n "$(git -C "$REPO" status --porcelain)" ]; then
  fail "El checkout humano tiene cambios sin commit. No se modifico nada."
fi

if [ ! -d "$DEPLOY/.git" ]; then
  git -C "$REPO" worktree add --detach "$DEPLOY" origin/main
else
  [ -z "$(git -C "$DEPLOY" status --porcelain)" ] ||
    fail "El deploy worktree tiene cambios sin commit."
fi

mkdir -p "$BACKUPS"
crontab -l > "$BACKUPS/crontab_pre_safe_sync_$STAMP.txt"
say BACKUP
printf 'crontab_backup=%s\n' "$BACKUPS/crontab_pre_safe_sync_$STAMP.txt"
say READY
printf 'human_checkout=%s\n' "$REPO"
printf 'deploy_worktree=%s\n' "$DEPLOY"
printf 'safe_script=/home/mak/bin/mak_sync_safe.py\n'
'''


def run_ssh(script: str) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
             "bash", "-s"],
            input=script.encode(), capture_output=True, text=False, timeout=90,
            check=False,
        )
        return (result.returncode, result.stdout.decode("utf-8", "replace"),
                result.stderr.decode("utf-8", "replace"))
    except FileNotFoundError:
        return 127, "", "No se encontro ssh en Windows."
    except subprocess.TimeoutExpired:
        return 124, "", "La provision excedio 90 segundos."


def install_script() -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["scp", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
             str(SAFE_SCRIPT), f"{HOST}:/tmp/mak_sync_safe.py"],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if result.returncode != 0:
            return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", "No se encontro scp en Windows."
    install = """set -eu
mkdir -p /home/mak/bin
install -m 0755 /tmp/mak_sync_safe.py /home/mak/bin/mak_sync_safe.py
rm -f /tmp/mak_sync_safe.py
"""
    return run_ssh(install)


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision the safe MAK deploy path")
    parser.add_argument("--apply", action="store_true",
                        help="install the script and provision the disposable worktree")
    parser.add_argument("--output", default="mak_sync_repair.md")
    args = parser.parse_args()
    if not args.apply:
        print("No se hizo nada. Usa --apply despues de revisar el alcance.")
        return 2

    code, out, err = install_script()
    if code == 0:
        code, provision_out, provision_err = run_ssh(REMOTE)
        out = out + provision_out
        err = err + provision_err
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    report = (
        "# Provision MAK safe sync\n\n"
        f"Fecha: `{now}`\nExit code: `{code}`\n\n"
        "## Salida remota\n\n```text\n"
        f"{out.strip()}\n```\n\n## STDERR\n\n```text\n"
        f"{err.strip() or '(vacio)'}\n```\n\n"
        "La provision no resetea el checkout humano ni activa el cron por si sola.\n"
    )
    Path(args.output).write_text(report, encoding="utf-8")
    print(f"Reporte escrito: {Path(args.output).resolve()} (exit={code})")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
