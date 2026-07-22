#!/usr/bin/env python3
"""Repara de forma conservadora el sync GitHub -> MAK.

Uso desde Windows:
  py repair_mak_sync.py --apply --output mak_sync_repair.md

Hace SOLO lo siguiente en MAK:
1. detiene si el checkout tiene cambios sin commit;
2. crea una rama backup/rescue apuntando al HEAD actual;
3. respalda el crontab actual en ~/plataforma/backups/;
4. corrige MAK-REPO-SYNC para actualizar refs/remotes/origin/main;
5. sincroniza una vez el checkout a origin/main;
6. copia los tres espejos a los directorios vivos con el mismo cp -ru ya
   usado por el cron;
7. verifica branch, hashes, cron y APIs.

No toca secretos, datos RD, servicios, red, XIO, modelos ni GitHub. No borra
el commit previo: queda anclado en la rama backup/rescue creada antes del reset.
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path

HOST = "mak@192.168.50.2"
REMOTE = r'''set -eu
STAMP=$(date +%Y%m%d_%H%M%S)
REPO="$HOME/flujo"
PLAT="$HOME/plataforma"
BACKUPS="$PLAT/backups"
SYNC='*/10 * * * * git -C /home/mak/flujo fetch -q origin +refs/heads/main:refs/remotes/origin/main && git -C /home/mak/flujo checkout -q -B main origin/main && git -C /home/mak/flujo reset -q --hard origin/main && cp -ru /home/mak/flujo/cultura/mak_plataforma/. /home/mak/plataforma/ && cp -ru /home/mak/flujo/cultura/mak_research/. /home/mak/research/ && cp -ru /home/mak/flujo/cultura/mak_codex/. /home/mak/codex/ # MAK-REPO-SYNC'

say() { printf '\n@@ %s @@\n' "$1"; }
fail() { say BLOCKED; printf '%s\n' "$1"; exit 20; }

[ -d "$REPO/.git" ] || fail "No existe checkout Git en $REPO"

say BEFORE
printf 'branch='; git -C "$REPO" branch --show-current
printf 'head='; git -C "$REPO" rev-parse HEAD
printf 'status='; git -C "$REPO" status --porcelain

# Nunca resetear un trabajo sin commit: no hay forma segura de reconstruirlo.
if [ -n "$(git -C "$REPO" status --porcelain)" ]; then
  fail "El checkout tiene cambios sin commit. No se modifico nada. Commit/stash humano requerido."
fi

mkdir -p "$BACKUPS"
BACKUP_BRANCH="backup/pre-sync-$STAMP"
git -C "$REPO" branch "$BACKUP_BRANCH" HEAD
crontab -l > "$BACKUPS/crontab_pre_sync_$STAMP.txt"

# Reemplaza SOLO la linea marcada. Si no existe, agrega exactamente una.
TMP=$(mktemp)
(crontab -l | grep -v 'MAK-REPO-SYNC' || true) > "$TMP"
printf '%s\n' "$SYNC" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

say BACKUP
printf 'backup_branch=%s\n' "$BACKUP_BRANCH"
printf 'crontab_backup=%s\n' "$BACKUPS/crontab_pre_sync_$STAMP.txt"

say SYNC
# El refspec explicito arregla el bug: `git fetch origin main` solo deja FETCH_HEAD.
git -C "$REPO" fetch -q origin +refs/heads/main:refs/remotes/origin/main
git -C "$REPO" checkout -q -B main origin/main
git -C "$REPO" reset -q --hard origin/main
cp -ru "$REPO/cultura/mak_plataforma/." "$HOME/plataforma/"
cp -ru "$REPO/cultura/mak_research/." "$HOME/research/"
cp -ru "$REPO/cultura/mak_codex/." "$HOME/codex/"

say AFTER
printf 'branch='; git -C "$REPO" branch --show-current
printf 'head='; git -C "$REPO" rev-parse HEAD
printf 'origin_main='; git -C "$REPO" rev-parse origin/main
printf 'status='; git -C "$REPO" status --porcelain
printf 'cron='; crontab -l | grep 'MAK-REPO-SYNC' || true

say APIS
for url in http://127.0.0.1:8890/ http://127.0.0.1:8891/ http://127.0.0.1:8900/api/salud; do
  printf '%s ' "$url"
  curl -sS -m 5 -o /dev/null -w 'HTTP=%{http_code}\n' "$url" || true
done
'''


def run_remote() -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST, "bash", "-s"],
            input=REMOTE.encode(), capture_output=True, text=False, timeout=90, check=False,
        )
        return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")
    except FileNotFoundError:
        return 127, "", "No se encontro ssh en Windows."
    except subprocess.TimeoutExpired:
        return 124, "", "La reparacion excedio 90 segundos. No reintentes sin revisar el estado remoto."


def main() -> int:
    p = argparse.ArgumentParser(description="Reparacion conservadora de MAK-REPO-SYNC")
    p.add_argument("--apply", action="store_true", help="requerido: confirma backup + cambio cron + sync")
    p.add_argument("--output", default="mak_sync_repair.md")
    a = p.parse_args()
    if not a.apply:
        print("No se hizo nada. Reejecuta con --apply tras revisar el proposito con --help.")
        return 2
    code, out, err = run_remote()
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    report = f"# Reparacion MAK-REPO-SYNC\n\nFecha: `{now}`\nExit code: `{code}`\n\n## Salida remota\n\n```text\n{out.strip()}\n```\n\n## STDERR\n\n```text\n{err.strip() or '(vacio)'}\n```\n\n## Interpretacion\n\n- Exit `0` y `branch=main` con `head == origin_main`: sync reparado.\n- `@@ BLOCKED @@`: no se modifico checkout ni cron; hay cambios sin commit.\n- Otro exit code: no repetir a ciegas; adjunta este reporte al agente.\n"
    Path(a.output).write_text(report, encoding="utf-8")
    print(f"Reporte escrito: {Path(a.output).resolve()} (exit={code})")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
