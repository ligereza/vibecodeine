#!/usr/bin/env python3
"""Snapshot read-only Windows -> MAK para dirigir el siguiente paso con evidencia.

Uso en Windows, desde la raiz del repo:
    py tools/mak/director_snapshot.py --output director_snapshot.md

No modifica MAK, GitHub, cron, servicios, red, archivos ni datos. Solo hace:
- HTTP GET a research/codex/hub en la LAN privada;
- un SSH de solo lectura a mak@192.168.50.2;
- lee el estado del checkout local (Windows).

El Markdown producido esta pensado para adjuntarlo a una conversacion o darlo
al modelo local. Nunca incluye contenido de .env, tokens, logs ni datos RD.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MAK_HOST = os.environ.get("MAK_HOST", "192.168.50.2")
MAK_USER = os.environ.get("MAK_USER", "mak")
SSH_TARGET = f"{MAK_USER}@{MAK_HOST}"
def _find_repo_root() -> Path:
    """Funciona tanto dentro de tools/mak/ como si el archivo se copia a la raiz."""
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for candidate in (start, *start.parents):
            if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
                return candidate
    return Path.cwd()


ROOT = _find_repo_root()

# No se leen logs: son una fuente frecuente de tokens y datos accidentales.
REMOTE_READONLY = r'''set -u
say() { printf '\n@@ %s @@\n' "$1"; }
say IDENTITY
hostname 2>&1 || true
date -Is 2>&1 || true
uname -srmo 2>&1 || true
say RESOURCES
uptime 2>&1 || true
free -h 2>&1 || true
df -h / 2>&1 || true
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader 2>&1 || true
say PORTS
ss -ltn 2>&1 | grep -E ':(8890|8891|8900|11434|1234)[[:space:]]' || true
say CRON
crontab -l 2>&1 || true
say PROCESSES
ps -eo pid=,etimes=,comm=,args= 2>/dev/null | grep -E '[r]esearch|[c]odex|[h]ub.py|[t]rabajo.py|[c]apataz.py|[a]gente_real.py|[w]atchdog' | head -40 || true
say LIVE_DIRS
for d in "$HOME/flujo" "$HOME/plataforma" "$HOME/research" "$HOME/codex"; do
  if [ -d "$d" ]; then printf '%s=present\n' "$d"; else printf '%s=missing\n' "$d"; fi
done
say GIT
if [ -d "$HOME/flujo/.git" ]; then
  git -C "$HOME/flujo" status -sb 2>&1 || true
  git -C "$HOME/flujo" log -1 --format='HEAD=%H%nDATE=%ad%nSUBJECT=%s' --date=iso 2>&1 || true
else
  echo 'checkout=missing'
fi
say CONTROL_FILES
for f in "$HOME/plataforma/trabajo.py" "$HOME/plataforma/guardia.py" "$HOME/plataforma/agente_real.py"; do
  [ -f "$f" ] && printf '%s=present\n' "$f" || printf '%s=missing\n' "$f"
done
'''

SECRET_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z_-]{20,}"), "[REDACTED_GOOGLE_KEY]"),
    (re.compile(r"sk-[A-Za-z0-9_-]{12,}"), "[REDACTED_API_KEY]"),
    (re.compile(r"(?i)(authorization|bearer|token|api[_ -]?key|password)\s*[:=]\s*[^\s]+"), r"\1=[REDACTED]"),
]


def redact(text: str) -> str:
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def local_git() -> dict[str, str]:
    def run(args: list[str]) -> str:
        try:
            r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=10, check=False)
            return (r.stdout or r.stderr).strip()
        except (OSError, subprocess.TimeoutExpired) as exc:
            return f"unknown: {exc}"
    return {"root": str(ROOT), "head": run(["git", "rev-parse", "HEAD"]),
            "branch": run(["git", "branch", "--show-current"]),
            "status": run(["git", "status", "--short"])}


def http_probe(name: str, url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, method="GET", headers={"User-Agent": "vibecodeine-director-snapshot/1"})
        with urllib.request.urlopen(request, timeout=6) as response:
            raw = response.read(2000).decode("utf-8", "replace")
            summary = f"HTTP {response.status}"
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    summary += "; JSON keys: " + ", ".join(sorted(map(str, data.keys()))[:12])
            except ValueError:
                pass
            return {"name": name, "url": url, "status": "ok", "summary": redact(summary)}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"name": name, "url": url, "status": "unreachable", "summary": redact(str(exc)[:240])}


def ssh_snapshot() -> tuple[str, str]:
    try:
        # bytes evita que Windows convierta \n en \r\n dentro del script remoto.
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", SSH_TARGET, "bash", "-s"],
            input=REMOTE_READONLY.encode("utf-8"), capture_output=True, text=False, timeout=35, check=False,
        )
        stdout = result.stdout.decode("utf-8", "replace")
        stderr = result.stderr.decode("utf-8", "replace")
        if result.returncode != 0:
            return "unreachable", redact((stderr or stdout or "ssh failed")[:1000])
        return "ok", redact(stdout[:14000])
    except FileNotFoundError:
        return "unavailable", "No se encontro el comando ssh en Windows."
    except subprocess.TimeoutExpired:
        return "unreachable", "SSH excedio 35 segundos."
    except OSError as exc:
        return "unreachable", redact(str(exc))


def fence(text: str) -> str:
    return "```text\n" + (text.strip() or "(sin salida)") + "\n```"


def make_markdown(local: dict[str, str], probes: list[dict[str, Any]], ssh_state: str, ssh_text: str) -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    rows = "\n".join(f"| {p['name']} | {p['status']} | {p['summary']} |" for p in probes)
    unreachable = [p["name"] for p in probes if p["status"] != "ok"]
    return f'''# Director snapshot — Windows → MAK

Generado: `{now}`  
Modo: **solo lectura**. Este archivo no prueba que una configuracion documentada siga vigente: registra lo que fue observable durante esta corrida.

## Resumen rapido

- SSH MAK: **{ssh_state}**
- APIs inaccesibles: **{', '.join(unreachable) if unreachable else 'ninguna'}**
- Repo local Windows: rama `{local['branch'] or 'unknown'}`, HEAD `{local['head'][:12]}`

## APIs LAN

| Servicio | Estado | Evidencia minima |
|---|---|---|
{rows}

## Checkout Windows

```text
root={local['root']}
branch={local['branch']}
head={local['head']}
status={local['status'] or '(limpio)'}
```

## Lectura remota MAK por SSH

{fence(ssh_text)}

## Contrato de interpretacion

- `ok` significa que esta corrida obtuvo respuesta; no significa que todo el sistema este sano.
- `unreachable` significa que no hubo respuesta mediante este canal; no autoriza cambiar configuracion.
- No hay logs, secretos, .env, datos de RD ni contenido de bases en este snapshot.
- El siguiente paso debe basarse en diferencias entre esta evidencia y la documentacion, no en suposiciones.

## Prompt para analisis local o agente director

Usa exclusivamente este snapshot y las fuentes versionadas del repo. Responde en maximo 500 palabras:

1. Separa hechos observados, documentacion historica y datos desconocidos.
2. Enumera contradicciones relevantes con `context/LAST_HANDOFF.md`, `cultura/mak_plataforma/GENESIS.md`, `tools/mak/delegar.py` y `cultura/mak_plataforma/trabajo.py`.
3. Elige UNA siguiente observacion de solo lectura que reduzca mas incertidumbre.
4. Indica explicitamente si corresponde o no crear un airdrop. Por defecto: NO.
5. No propongas cambios de red, cron, servicios, credenciales, XIO, datos RD, modelos, instalaciones ni merges.
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot read-only Windows -> MAK")
    parser.add_argument("--output", default="director_snapshot.md", help="Markdown de salida")
    args = parser.parse_args()
    probes = [
        http_probe("research :8890", f"http://{MAK_HOST}:8890/"),
        http_probe("codex :8891", f"http://{MAK_HOST}:8891/"),
        http_probe("hub :8900", f"http://{MAK_HOST}:8900/api/salud"),
    ]
    ssh_state, ssh_text = ssh_snapshot()
    output = Path(args.output)
    output.write_text(make_markdown(local_git(), probes, ssh_state, ssh_text), encoding="utf-8")
    print(f"Snapshot escrito: {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
