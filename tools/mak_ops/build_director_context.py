#!/usr/bin/env python3
"""Arma un unico contexto local para el modelo Windows. No toca MAK ni Git."""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path.cwd()
FILES = [
    "PLAN.md",
    "CLAUDE.md",
    "context/LAST_HANDOFF.md",
    "cultura/mak_plataforma/GENESIS.md",
    "cultura/mak_plataforma/trabajo.py",
    "cultura/mak_plataforma/guardia.py",
    "cultura/mak_plataforma/filtro_entrada.py",
    "tools/mak/delegar.py",
    "docs/AGENT_AIRDROP_PROTOCOL.md",
]
PROMPT = '''# Instruccion al modelo director

No ejecutes comandos, no escribas codigo y no propongas cambios aun.
Trabaja solo con las fuentes incluidas. El snapshot vivo tiene prioridad sobre
handoffs/documentacion historica cuando se contradigan.

Entrega un informe Markdown de maximo 900 palabras con:
1. HECHOS VIVOS CONFIRMADOS (cita archivo/seccion).
2. ESTADO DOCUMENTADO PERO NO CONFIRMADO.
3. CONTRADICCIONES O RIESGOS.
4. MAPA DE CONTROL: Windows, GitHub, MAK, research, codex, hub, cron y sync.
5. QUE INFORMACION YA ES SUFICIENTE PARA ACTUAR.
6. UNA SOLA SIGUIENTE ACCION, de bajo riesgo, con resultado esperado.

Reglas: no proponer recoleccion de datos personales; no tocar red, XIO,
credenciales, servicios, cron, modelos, datos RD ni merges. No inventar.
'''

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", default="director_snapshot_3.md")
    p.add_argument("--output", default="director_context.md")
    a = p.parse_args()
    out = ["# Contexto Director Local\n", PROMPT]
    snap = ROOT / a.snapshot
    if not snap.exists():
        raise SystemExit(f"Falta snapshot: {snap}")
    out += ["\n## SNAPSHOT VIVO\n", snap.read_text(encoding="utf-8", errors="replace")]
    for rel in FILES:
        path = ROOT / rel
        if path.exists():
            out += [f"\n\n## ARCHIVO: {rel}\n```text\n", path.read_text(encoding="utf-8", errors="replace"), "\n```\n"]
        else:
            out += [f"\n\n## ARCHIVO AUSENTE: {rel}\n"]
    Path(a.output).write_text("".join(out), encoding="utf-8")
    print(f"Contexto escrito: {Path(a.output).resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
