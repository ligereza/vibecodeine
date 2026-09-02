#!/usr/bin/env python3
"""Borrador de cierre de sesion desde git + pyproject (NO sobreescribe nada).

Uso: py tools/handoff.py
Imprime version/fecha/rama/commits recientes + una plantilla ASCII para pegar en
context/LAST_HANDOFF.md. El cierre real lo escribe el humano/agente revisando.
"""
import subprocess, re, datetime
from pathlib import Path

def ver():
    try:
        m = re.search(r'version\s*=\s*"([^"]+)"', Path("pyproject.toml").read_text(encoding="utf-8"))
        return m.group(1) if m else "?"
    except Exception:
        return "?"

def git(*a):
    try:
        return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""

def main():
    v = ver(); date = datetime.date.today().isoformat()
    br = git("branch", "--show-current"); log = git("log", "--oneline", "-8")
    print(f"""Date: {date}
Version: {v}   (debe coincidir con pyproject.toml y src/flujo/version.py)
Assistant: Cauce
Branch: {br}

== COMMITS RECIENTES ==
{log}

== PLANTILLA (ASCII-only; rellena y pega en context/LAST_HANDOFF.md) ==
== ESTADO ACTUAL ==
<foco de la sesion en 2-3 lineas>
== LISTO ==
- <que quedo hecho>
== PENDIENTE ==
- <que falta>
== BLOQUEADORES ==
- <reales, no adivinar>
== PROXIMO PASO RECOMENDADO ==
- <lo siguiente concreto>

Recuerda actualizar tambien context/SESSION_STATE.json (version={v}, date={date}).""")

if __name__ == "__main__":
    main()
