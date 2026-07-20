#!/usr/bin/env python3
"""expulsion.py -- P0-2 SHADOW MODE. Detecta candidatos a expulsion de
proveedor LLM cronicamente malo, sin aplicar nada todavia.

Formula de score: score_provider_health() en fallback_util.py
    score = successes / (successes + timeouts + api_errors + errors)
    (0.0 si no hubo intentos)

Regla de candidato: intentos >= 10 AND score < 0.3.

SEGURIDAD: un proveedor NUNCA se marca expulsable si es el unico proveedor
sano (score >= 0.3, o ausente de stats = asumido sano) en CUALQUIER cadena
de _SLOTS. Vaciar una cadena en produccion es el riesgo que este modo shadow
existe para evitar.

Modo default: SHADOW. Escribe reporte + evento, no toca salud/roles/cadenas.
--enforce: stub, no implementado todavia (deliberado).
"""
import argparse
import json
import os
import sys
import time

RESEARCH_DIR = os.path.expanduser("~/research")
SALUD_RUTA = os.path.join(RESEARCH_DIR, "salud_proveedores.json")
EVENTOS_RUTA = os.path.join(RESEARCH_DIR, "eventos.jsonl")
REFLEXIONES_DIR = os.path.expanduser("~/plataforma/reflexiones")
REPORTE_RUTA = os.path.join(REFLEXIONES_DIR, "expulsion_shadow.json")

sys.path.insert(0, RESEARCH_DIR)
try:
    from fallback_util import score_provider_health
except ImportError:
    score_provider_health = None

try:
    from research_lib import _SLOTS
except ImportError:
    # Replica de research_lib._SLOTS si el import fallara (no debe pasar).
    _SLOTS = {
        "razonar": "azure,cerebras,groq,ollama",
        "bulk": "cerebras,groq,azure,ollama",
        "barato": "ollama,cerebras,groq",
    }

INTENTOS_MIN = 10
SCORE_MAX = 0.3


def cargar_salud(ruta=None):
    ruta = ruta or SALUD_RUTA
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    proveedores = data.get("proveedores")
    return proveedores if isinstance(proveedores, dict) else {}


def chains_por_proveedor():
    """rol -> lista de proveedores en esa cadena."""
    out = {}
    for rol, s in _SLOTS.items():
        out[rol] = [p.strip() for p in s.split(",")]
    return out


def proveedor_sano(proveedor, stats, scores):
    """Un proveedor se considera sano si esta ausente de stats (sin
    intentos registrados, se asume disponible) O su score >= SCORE_MAX."""
    contadores = stats.get(proveedor)
    if not isinstance(contadores, dict):
        return True
    intentos = sum(contadores.values())
    if intentos == 0:
        return True
    return scores.get(proveedor, 0.0) >= SCORE_MAX


def evaluar(stats):
    """Devuelve lista de dicts candidatos (ver contrato en el modulo)."""
    if not stats or score_provider_health is None:
        return []
    scores = dict(score_provider_health(stats))
    chains = chains_por_proveedor()
    candidatos = []
    for proveedor, contadores in stats.items():
        if not isinstance(contadores, dict):
            continue
        intentos = sum(contadores.values())
        score = scores.get(proveedor, 0.0)
        if not (intentos >= INTENTOS_MIN and score < SCORE_MAX):
            continue
        chains_afectadas = [rol for rol, miembros in chains.items()
                            if proveedor in miembros]
        # Seguridad: si expulsar a `proveedor` deja alguna de sus cadenas
        # sin NINGUN proveedor sano, no es seguro expulsarlo.
        inseguro_en = []
        for rol in chains_afectadas:
            miembros = chains[rol]
            otros_sanos = [
                p for p in miembros
                if p != proveedor and proveedor_sano(p, stats, scores)
            ]
            if not otros_sanos:
                inseguro_en.append(rol)
        seguro_expulsar = not inseguro_en
        if seguro_expulsar:
            razon = "score %.2f < %.2f con %d intentos; hay alternativa sana en cada cadena (%s)" % (
                score, SCORE_MAX, intentos, ", ".join(chains_afectadas) or "ninguna")
        else:
            razon = "NO seguro: dejaria sin proveedor sano la(s) cadena(s) %s" % ", ".join(inseguro_en)
        candidatos.append({
            "proveedor": proveedor,
            "intentos": intentos,
            "score": round(score, 4),
            "chains_afectadas": chains_afectadas,
            "seguro_expulsar": seguro_expulsar,
            "razon": razon,
        })
    return candidatos


def escribir_reporte(candidatos):
    os.makedirs(REFLEXIONES_DIR, exist_ok=True)
    reporte = {
        "ts": time.time(),
        "candidatos": candidatos,
        "accion": "shadow -- no enforcement",
    }
    with open(REPORTE_RUTA, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    return reporte


def registrar_evento(candidatos):
    evento = {
        "tipo": "EXPULSION_SHADOW",
        "ts": time.time(),
        "n_candidatos": len(candidatos),
        "proveedores": [c["proveedor"] for c in candidatos],
    }
    try:
        os.makedirs(os.path.dirname(EVENTOS_RUTA), exist_ok=True)
        with open(EVENTOS_RUTA, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--enforce", action="store_true",
                    help="NO implementado todavia. Solo shadow por ahora.")
    args = ap.parse_args()

    stats = cargar_salud()
    candidatos = evaluar(stats)
    reporte = escribir_reporte(candidatos)
    registrar_evento(candidatos)

    if args.enforce:
        print("enforce no implementado, shadow only")
    else:
        print(json.dumps(reporte, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
