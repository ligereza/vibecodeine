#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bring a new perception pass into the live archive WITHOUT losing what the old
one knew.

The naive move is to replace each ficha by id. Measured on the real data, that
would destroy information: over the same 1.354 files, the new pass fills
`tipo_obra` where the old had nothing (67% -> 100%) but leaves
`oportunidad_codigo` empty on 225 images where the old pass had written one
(98,7% -> 77,9%). A row-level replace throws those 225 away in silence. A
row-level SKIP throws away the other 33 points. Neither is right.

So the merge is at FIELD level:

- a new non-empty value wins -- it comes from a better model, measured;
- a field the new pass did not fill KEEPS the old value, and that is recorded;
- nothing is ever silently dropped: the report counts what improved, what was
  inherited, and what was lost, and the last number must be zero.

The mixing is DECLARED, not hidden. `medicion.vision.motor` says who answered
the new pass, and `medicion.vision.heredado` lists the fields that survived
from the previous one. A ficha with fields from two engines and no record of it
is worse than either pass alone: whoever counts engines afterwards counts
ghosts. This is the same rule that killed the `or "ollama"` default.

Dry run by default. `--aplicar` writes, and only after a timestamped backup.

    py tools/consolidar_fichas.py ARCHIVO.jsonl NUEVA.jsonl
    py tools/consolidar_fichas.py ARCHIVO.jsonl NUEVA.jsonl --motor watsonx
    py tools/consolidar_fichas.py ARCHIVO.jsonl NUEVA.jsonl --aplicar
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Blocks merged field by field. Everything else (id, fuente, ruta_rel,
# bytes...) is the file's identity and is never touched.
BLOQUES = ("vision", "datos_evento")
# Loose top-level fields the perception pass produces.
SIMPLES = ("ocr_texto", "categoria", "calidad_senal")


def lleno(v) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict, tuple)):
        return bool(v)
    return True


def cargar(ruta: Path) -> tuple[list[dict], dict[str, int]]:
    """Rows in order, plus an index id -> LAST position.

    The last one wins: the pipeline appends a ficha per attempt, so a retry
    writes a new row and that retry is the outcome that counts.
    """
    filas: list[dict] = []
    indice: dict[str, int] = {}
    malas = 0
    with ruta.open(encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue
            try:
                d = json.loads(linea)
            except ValueError:
                malas += 1
                continue
            filas.append(d)
            if d.get("id"):
                indice[d["id"]] = len(filas) - 1
    if malas:
        print("  aviso: %d lineas ilegibles en %s (se conservan fuera del "
              "indice, NO se reescriben)" % (malas, ruta.name), file=sys.stderr)
    return filas, indice


def fusionar(vieja: dict, nueva: dict) -> tuple[dict, dict]:
    """A new ficha over an old one. Returns (ficha, counts)."""
    salida = dict(nueva)
    mejorados: list[str] = []
    heredados: list[str] = []

    for bloque in BLOQUES:
        v_old = vieja.get(bloque) or {}
        v_new = dict(nueva.get(bloque) or {})
        if not isinstance(v_old, dict) or not isinstance(v_new, dict):
            continue
        for k, val in v_old.items():
            if lleno(val) and not lleno(v_new.get(k)):
                v_new[k] = val
                heredados.append("%s.%s" % (bloque, k))
            elif lleno(v_new.get(k)) and not lleno(val):
                mejorados.append("%s.%s" % (bloque, k))
        for k, val in (nueva.get(bloque) or {}).items():
            if lleno(val) and k not in v_old:
                mejorados.append("%s.%s" % (bloque, k))
        salida[bloque] = v_new

    for k in SIMPLES:
        if lleno(vieja.get(k)) and not lleno(nueva.get(k)):
            salida[k] = vieja[k]
            heredados.append(k)
        elif lleno(nueva.get(k)) and not lleno(vieja.get(k)):
            mejorados.append(k)

    # The mixing is DECLARED. A ficha carrying fields from two engines with no
    # record of which came from which is worse than either pass alone.
    med = dict(salida.get("medicion") or {})
    vis = dict(med.get("vision") or {})
    if heredados:
        vis["heredado"] = sorted(set(heredados))
        vis["motor_heredado"] = (
            ((vieja.get("medicion") or {}).get("vision") or {}).get("motor")
            or "sin_atribucion")
    med["vision"] = vis
    salida["medicion"] = med
    return salida, {"mejorados": mejorados, "heredados": heredados}


def perdidos(vieja: dict, fusionada: dict) -> list[str]:
    """Fields the old ficha had filled and the merged one does not. Must be
    empty -- if it is not, the merge has a hole and nothing gets written."""
    faltan = []
    for bloque in BLOQUES:
        v_old = vieja.get(bloque) or {}
        v_new = fusionada.get(bloque) or {}
        if not isinstance(v_old, dict):
            continue
        for k, val in v_old.items():
            if lleno(val) and not lleno(v_new.get(k)):
                faltan.append("%s.%s" % (bloque, k))
    for k in SIMPLES:
        if lleno(vieja.get(k)) and not lleno(fusionada.get(k)):
            faltan.append(k)
    return faltan


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo", type=Path, help="fichas.jsonl vivo")
    p.add_argument("nueva", type=Path, help="fichas.jsonl de la pasada nueva")
    p.add_argument("--motor", default="",
                   help="solo traer las fichas que ESE motor midio")
    p.add_argument("--aplicar", action="store_true",
                   help="escribir de verdad (por defecto solo informa)")
    a = p.parse_args()

    for ruta in (a.archivo, a.nueva):
        if not ruta.exists():
            print("no existe: %s" % ruta, file=sys.stderr)
            return 2

    filas, indice = cargar(a.archivo)
    nuevas_filas, nuevo_indice = cargar(a.nueva)

    reemplazadas = agregadas = 0
    total_mejorados = total_heredados = 0
    campos_mejorados: dict[str, int] = {}
    campos_heredados: dict[str, int] = {}
    perdidas: list[tuple[str, list[str]]] = []
    saltadas_por_motor = 0
    salida = list(filas)

    for fid, pos in nuevo_indice.items():
        nueva = nuevas_filas[pos]
        if a.motor:
            motor = ((nueva.get("medicion") or {}).get("vision") or {}).get("motor")
            if motor != a.motor:
                saltadas_por_motor += 1
                continue
        if fid in indice:
            vieja = filas[indice[fid]]
            fusion, cuentas = fusionar(vieja, nueva)
            faltan = perdidos(vieja, fusion)
            if faltan:
                perdidas.append((fid, faltan))
            salida[indice[fid]] = fusion
            reemplazadas += 1
            total_mejorados += len(cuentas["mejorados"])
            total_heredados += len(cuentas["heredados"])
            for c in cuentas["mejorados"]:
                campos_mejorados[c] = campos_mejorados.get(c, 0) + 1
            for c in cuentas["heredados"]:
                campos_heredados[c] = campos_heredados.get(c, 0) + 1
        else:
            salida.append(nueva)
            agregadas += 1

    print("archivo vivo:   %s (%d filas, %d ids)"
          % (a.archivo, len(filas), len(indice)))
    print("pasada nueva:   %s (%d filas, %d ids)"
          % (a.nueva, len(nuevas_filas), len(nuevo_indice)))
    if a.motor:
        print("filtrado a motor=%s (%d fichas de la pasada nueva quedan fuera)"
              % (a.motor, saltadas_por_motor))
    print()
    print("fichas que se REEMPLAZAN (fusion campo a campo): %d" % reemplazadas)
    print("fichas que se AGREGAN (no estaban):              %d" % agregadas)
    print("resultado: %d filas" % len(salida))
    print()
    print("campos MEJORADOS por la pasada nueva: %d" % total_mejorados)
    for c, n in sorted(campos_mejorados.items(), key=lambda x: -x[1])[:12]:
        print("   %5d  %s" % (n, c))
    print("campos HEREDADOS de la pasada vieja: %d" % total_heredados)
    for c, n in sorted(campos_heredados.items(), key=lambda x: -x[1])[:12]:
        print("   %5d  %s" % (n, c))
    print()
    if perdidas:
        print("!!! CAMPOS PERDIDOS en %d fichas -- la fusion tiene un agujero, "
              "NO se aplica" % len(perdidas))
        for fid, faltan in perdidas[:5]:
            print("   %s -> %s" % (fid, ", ".join(faltan)))
        return 1
    print("campos perdidos: 0")

    if not a.aplicar:
        print()
        print("(ensayo: no se escribio nada. Para aplicar: --aplicar)")
        return 0

    sello = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    respaldo = a.archivo.with_suffix(".jsonl.bak-" + sello)
    shutil.copy2(a.archivo, respaldo)
    tmp = a.archivo.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for d in salida:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    # Validated BEFORE overwriting: a half-written file on top of the live one
    # is worse than having done nothing.
    releidas, _ = cargar(tmp)
    if len(releidas) != len(salida):
        print("!!! el archivo temporal quedo con %d filas y esperaba %d; "
              "NO se piso el vivo (queda en %s)"
              % (len(releidas), len(salida), tmp), file=sys.stderr)
        return 1
    tmp.replace(a.archivo)
    print()
    print("aplicado. respaldo en %s" % respaldo.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
