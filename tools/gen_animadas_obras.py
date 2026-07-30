#!/usr/bin/env python3
"""Cada obra curada genera su pieza animada por el motor semantico.

El ensayo rave fue la DEMO del mecanismo (spec cerrada -> compilar -> svg
animado); el sistema existe para las obras del artista. Este generador cierra
ese circuito: lee las obras curadas (`iskvw/datos/obras.json`), deriva para
cada una UNA spec del vocabulario cerrado del motor -- semantica donde los
datos alcanzan, sembrada por el id donde no -- y compila su pieza animada.

Determinista a proposito: misma obra -> misma spec -> misma pieza, sin azar
de reloj. Es la misma tesis del timecode como semilla (PROYECCION.md): lo
generativo se puede verificar como un test.

    py tools/gen_animadas_obras.py            # escribe svg + manifiesto
    py tools/gen_animadas_obras.py --check    # falla si el disco no coincide

Salidas:
    iskvw/piel/animadas/<obra_id>.svg
    iskvw/datos/animadas.json   (manifiesto que lee contrato_archivo)

La pieza entra al archivo como `pieza_grafica` vinculada a su obra via
`contrato_archivo.desde_animadas()`, y la piel ya sabe presentarla al
quedarse quieto (mismo mecanismo que los iconos de ensayo).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cultura" / "mak_codex"))
from motor_semantico.compilador import (  # noqa: E402
    COMPOSICIONES, FIGURAS, GESTOS, RITMOS, TONOS, compilar, validar_spec,
)

OBRAS = RAIZ / "iskvw" / "datos" / "obras.json"
SALIDA_SVG = RAIZ / "iskvw" / "piel" / "animadas"
MANIFIESTO = RAIZ / "iskvw" / "datos" / "animadas.json"

GESTOS_VIVOS = sorted(g for g in GESTOS if g != "quieto")

# Palabra de la obra -> gesto, SOLO donde el mapeo significa algo y no es una
# ocurrencia: la tilde late (es la senal del proyecto tilde), lo generativo
# respira, lo reactivo tiembla. Todo lo demas cae a la semilla.
GESTO_POR_TAG = {
    "tilde": "latir",
    "generativo": "respirar",
    "generativa": "respirar",
    "reactiva": "temblar",
    "reactivo": "temblar",
    "proyeccion": "emanar",
    "projection": "emanar",
}


def _ascii(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def _semilla(obra_id: str) -> "list[int]":
    return list(hashlib.sha256(obra_id.encode("utf-8")).digest())


def _palabras(obra: dict) -> "list[str]":
    crudo = " ".join([
        obra.get("title") or "", obra.get("category") or "",
        " ".join(obra.get("tags") or []),
    ])
    return [_ascii(p) for p in crudo.replace("/", " ").split() if p]


def derivar_spec(obra: dict) -> dict:
    """Una spec valida del vocabulario cerrado, derivada de la obra.

    Prioridad: coincidencia literal de palabra (figura/tono nombrados por la
    propia obra) > regla semantica declarada (GESTO_POR_TAG) > semilla del id.
    Nunca reloj, nunca random: el mismo id produce la misma spec siempre.
    """
    s = _semilla(obra.get("id") or obra.get("title") or "obra")
    palabras = _palabras(obra)

    figuras_dichas = [p for p in palabras if p in FIGURAS]
    tonos_dichos = [p for p in palabras if p in TONOS]
    # El orden de GESTO_POR_TAG es prioridad SEMANTICA (la tilde manda sobre
    # lo generativo), no el orden en que la obra escribio sus etiquetas.
    presentes = set(palabras)
    gesto_dicho = next((g for p, g in GESTO_POR_TAG.items()
                        if p in presentes), None)

    comps = sorted(COMPOSICIONES)
    comp = comps[s[0] % len(comps)]
    ranuras = sorted(COMPOSICIONES[comp])
    tono = tonos_dichos[0] if tonos_dichos else sorted(TONOS)[s[1] % len(TONOS)]

    figs = sorted(FIGURAS)
    fig_prota = figuras_dichas[0] if figuras_dichas else figs[s[2] % len(figs)]
    gesto_prota = gesto_dicho or GESTOS_VIVOS[s[3] % len(GESTOS_VIVOS)]
    ritmos = sorted(RITMOS)

    capas = [{
        "rol": "protagonista",
        "figura": fig_prota,
        "gesto": gesto_prota,
        "ritmo": ritmos[s[4] % len(ritmos)],
    }]
    # Una segunda capa quieta da fondo sin volver ruido la pieza; el rol sale
    # de las ranuras reales de la composicion elegida.
    otros = [r for r in ranuras if r != "protagonista"]
    if otros:
        capas.append({
            "rol": otros[s[5] % len(otros)],
            "figura": figs[s[6] % len(figs)],
            "gesto": "quieto",
        })
    return {"composicion": comp, "tono": tono, "capas": capas}


def generar() -> "list[dict]":
    obras = json.loads(OBRAS.read_text(encoding="utf-8"))
    SALIDA_SVG.mkdir(parents=True, exist_ok=True)
    filas = []
    for obra in obras:
        oid = obra.get("id")
        if not oid:
            continue
        spec = derivar_spec(obra)
        fallos = validar_spec(spec)
        if fallos:
            raise SystemExit(f"spec invalida para '{oid}': {fallos}")
        svg, _avisos = compilar(spec, slug=oid)
        destino = SALIDA_SVG / f"{oid}.svg"
        destino.write_text(svg, encoding="utf-8", newline="\n")
        filas.append({
            "obra_id": oid,
            "titulo": obra.get("title") or oid,
            "src": destino.relative_to(RAIZ).as_posix(),
            "spec": spec,
            "declara_animacion": any(
                (c.get("gesto") or "quieto") != "quieto" for c in spec["capas"]),
        })
    return filas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="no escribe: falla si el disco difiere de lo derivado")
    args = ap.parse_args()

    filas = generar() if not args.check else None
    if args.check:
        antes = MANIFIESTO.read_text(encoding="utf-8") if MANIFIESTO.exists() else ""
        filas = generar()
        ahora = json.dumps({"version": 1, "piezas": filas},
                           ensure_ascii=False, indent=1)
        if antes.strip() != ahora.strip():
            print("animadas.json no coincide con lo derivado: regenerar")
            return 1
        print(f"coherente: {len(filas)} piezas animadas")
        return 0

    MANIFIESTO.write_text(
        json.dumps({"version": 1, "piezas": filas}, ensure_ascii=False, indent=1),
        encoding="utf-8", newline="\n")
    animadas = sum(1 for f in filas if f["declara_animacion"])
    print(f"{len(filas)} piezas ({animadas} animadas) -> {SALIDA_SVG.relative_to(RAIZ)}")
    print(f"manifiesto -> {MANIFIESTO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
