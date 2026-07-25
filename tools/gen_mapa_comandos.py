#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la tabla de comandos de MAPA.md preguntandole al CLI, no a la memoria.

Por que existe (2026-07-25): tres auditorias seguidas se equivocaron sobre lo
que el repo tiene porque leyeron prosa vieja en vez de medir. La tabla de
comandos de MAPA.md no se escribe a mano: se genera desde `flujo --help`, asi
un comando nuevo aparece solo y uno retirado desaparece solo.

Uso:
    py tools/gen_mapa_comandos.py            # reescribe el bloque en MAPA.md
    py tools/gen_mapa_comandos.py --check    # falla si MAPA.md quedo desfasado

El bloque vive entre los marcadores INICIO/FIN; el resto de MAPA.md se escribe
a mano y este script no lo toca.

Retiro: cuando el CLI exponga su propio `flujo mapa` y este script sea el que
lo llame.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MAPA = RAIZ / "MAPA.md"
INICIO = "<!-- COMANDOS:INICIO -- generado por tools/gen_mapa_comandos.py, no editar a mano -->"
FIN = "<!-- COMANDOS:FIN -->"

# Que necesita cada comando ANTES de funcionar. Vacio = nada, se corre y anda.
# Se escribe a mano a proposito: es la unica columna que el --help no sabe.
REQUISITOS: dict[str, str] = {
    "index": "`FLUJO_RD_ROOT` apuntando al arbol de material",
    "hub index": "`FLUJO_RD_ROOT` apuntando al arbol de material",
    "hub route": "`FLUJO_RD_ROOT` apuntando al arbol de material",
    "flyer-import": "casilla de correo: `FLUJO_IMAP_HOST`, `FLUJO_IMAP_USER`, "
                    "`FLUJO_IMAP_PASSWORD`, `FLUJO_IMAP_ALLOWED_SENDERS`",
    "eventos flyer-auto": "`pip install parth-dl`; para render tambien Blender",
    "ig-redownload": "`pip install parth-dl`",
    "render run": "Blender instalado",
    "render bridge": "Blender instalado",
    "render illustrator": "Adobe Illustrator (solo Windows/macOS)",
    "suplementos illustrator": "Adobe Illustrator (solo Windows/macOS)",
    "resolume automatizar": "Chataigne y Resolume abiertos en la maquina del show",
    "package": "solo Windows; empaqueta un .exe",
    "rd-db build": "fuentes de datos en `data/` (la DB se regenera, no se versiona)",
    "rd-datos ingest": "un CSV de campo; la DB privacy-first se crea sola",
    "tapiz": "nada; el instrumento vive en `tools/compete_engine.py`",
}


def _help(path: list[str]) -> str:
    entorno = {**os.environ, "COLUMNS": "400", "TERM": "dumb", "NO_COLOR": "1"}
    r = subprocess.run(
        [sys.executable, "-m", "flujo", *path, "--help"],
        capture_output=True, text=True, env=entorno, cwd=RAIZ,
    )
    return r.stdout


def _parse(texto: str) -> list[tuple[str, str]]:
    """Saca (comando, descripcion) del panel Commands de typer/rich."""
    filas: list[list[str]] = []
    dentro = False
    for linea in texto.splitlines():
        if "─ Commands ─" in linea:
            dentro = True
            continue
        if dentro and linea.startswith("╰"):
            break
        if not dentro or not linea.startswith("│"):
            continue
        cuerpo = linea[1:-1].rstrip()
        m = re.match(r"^\s*(\S+)\s\s+(.*)$", cuerpo)
        if m and not m.group(1).startswith("-"):
            filas.append([m.group(1), m.group(2).strip()])
        elif filas and cuerpo.strip():
            # descripcion que sigue en la linea de abajo
            filas[-1][1] = (filas[-1][1] + " " + cuerpo.strip()).strip()
    return [(a, b) for a, b in filas]


def arbol_cli() -> dict[str, dict]:
    arbol: dict[str, dict] = {}
    for nombre, desc in _parse(_help([])):
        arbol[nombre] = {"desc": desc, "sub": _parse(_help([nombre]))}
    return arbol


def invocables(arbol: dict[str, dict]) -> list[str]:
    """Todo lo que un humano puede tipear y que hace algo."""
    out = []
    for nombre, datos in arbol.items():
        if datos["sub"]:
            out += [f"{nombre} {sub}" for sub, _ in datos["sub"]]
        else:
            out.append(nombre)
    return out


def _fila(cmd: str, desc: str) -> str:
    req = REQUISITOS.get(cmd, "")
    desc = desc.replace("|", "\\|").strip() or "(sin descripcion en el --help)"
    if len(desc) > 200:
        desc = desc[:197].rstrip() + "..."
    return f"| `py -m flujo {cmd}` | {desc} | {req or 'nada'} |"


def render(arbol: dict[str, dict]) -> str:
    L = [INICIO, ""]
    L.append(f"Medido sobre el CLI real: **{len(invocables(arbol))} comandos** "
             f"({sum(1 for d in arbol.values() if not d['sub'])} sueltos + "
             f"{sum(len(d['sub']) for d in arbol.values())} dentro de "
             f"{sum(1 for d in arbol.values() if d['sub'])} grupos).")
    L.append("")
    sueltos = [(n, d["desc"]) for n, d in arbol.items() if not d["sub"]]
    if sueltos:
        L += ["### Comandos sueltos", "",
              "| Comando | Que hace | Que necesita antes |", "|---|---|---|"]
        L += [_fila(n, d) for n, d in sorted(sueltos)]
        L.append("")
    for nombre in sorted(n for n, d in arbol.items() if d["sub"]):
        datos = arbol[nombre]
        L += [f"### Grupo `{nombre}` -- {datos['desc']}", "",
              "| Comando | Que hace | Que necesita antes |", "|---|---|---|"]
        L += [_fila(f"{nombre} {sub}", desc) for sub, desc in datos["sub"]]
        L.append("")
    L.append(FIN)
    return "\n".join(L)


def aplicar(bloque: str) -> str:
    texto = MAPA.read_text(encoding="utf-8")
    if INICIO not in texto or FIN not in texto:
        raise SystemExit("MAPA.md no tiene los marcadores COMANDOS:INICIO/FIN")
    antes = texto[: texto.index(INICIO)]
    despues = texto[texto.index(FIN) + len(FIN):]
    return antes + bloque + despues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="no escribe: falla si MAPA.md quedo desfasado del CLI")
    args = ap.parse_args()

    nuevo = aplicar(render(arbol_cli()))
    actual = MAPA.read_text(encoding="utf-8")
    if nuevo == actual:
        print("MAPA.md al dia con el CLI.")
        return 0
    if args.check:
        print("MAPA.md DESFASADO del CLI. Corre: py tools/gen_mapa_comandos.py",
              file=sys.stderr)
        return 1
    MAPA.write_text(nuevo, encoding="utf-8")
    print("MAPA.md actualizado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
