#!/usr/bin/env python3
"""
esquema.py — Genera el JSON Schema del spec a partir del vocabulario.

Para qué: los 4 agentes usan `structured output` / grammar-constrained
decoding con este esquema. Entonces un spec malformado deja de ser
"improbable" y pasa a ser IMPOSIBLE de emitir — sin gastar tokens en
reintentos ni en explicarle el formato al modelo.

Respaldo: Grammar-Constrained Decoding (ICML 2025) — restringir la salida a
una gramática formal garantiza validez sintáctica por construcción, y los
modelos restringidos igualan o superan a los afinados para la tarea.

USO:
    python3 motor/esquema.py                 # imprime el esquema
    python3 motor/esquema.py schema.json     # lo guarda
"""
import json, sys, pathlib

if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    __package__ = "motor_semantico"

from .vocabulario import FIGURAS, GESTOS, TONOS, COMPOSICIONES, ROLES  # noqa: E402
from .compilador import RITMOS  # noqa: E402


def construir():
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "SpecIcono",
        "description": (
            "Descripción SEMÁNTICA de un ícono. No contiene coordenadas, "
            "colores ni animaciones: solo intención. El compilador produce la "
            "geometría."),
        "type": "object",
        "additionalProperties": False,
        "required": ["slug", "titulo", "composicion", "tono", "capas"],
        "properties": {
            "slug": {"type": "string", "pattern": "^[a-z0-9-]+$",
                     "description": "identificador en minúsculas con guiones"},
            "titulo": {"type": "string", "maxLength": 60},
            "brief": {"type": "string", "maxLength": 240,
                      "description": "la metáfora en una frase; guía al QA"},
            "composicion": {
                "enum": sorted(COMPOSICIONES),
                "description": "dónde se ubican las piezas. Define qué roles existen."},
            "tono": {
                "enum": sorted(TONOS),
                "description": "paleta verificada; el contraste está garantizado"},
            "capas": {
                "type": "array", "minItems": 1, "maxItems": 6,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["rol"],
                    "properties": {
                        "rol": {"enum": ROLES,
                                "description": "debe existir en la composición elegida"},
                        "figura": {
                            "enum": sorted(FIGURAS),
                            "description": " - ".join(
                                f"{k}: {v[1]}" for k, v in sorted(FIGURAS.items()))},
                        "texto": {"type": "string", "maxLength": 22,
                                  "description": "se mide antes de dibujar; si no cabe, se rechaza"},
                        "gesto": {
                            "enum": sorted(GESTOS),
                            "description": " - ".join(
                                f"{k}: {v[1]}" for k, v in sorted(GESTOS.items()))},
                        "ritmo": {"enum": sorted(RITMOS)},
                    },
                    "oneOf": [{"required": ["figura"]}, {"required": ["texto"]}],
                },
            },
        },
    }


# Una spec COMPLETA y valida, para que el prompt MUESTRE la forma en vez de
# describirla. Medido el 2026-07-30 contra un modelo real (gpt-4.1-mini via
# GitHub Models, tres briefs, hasta tres rondas de reparacion): sin ejemplo el
# modelo usaba el vocabulario correcto pero colgado de otra estructura
# --`composicion` y `tono` llegaban vacios-- y solo 1 de 3 briefs terminaba en
# SVG. El vocabulario cerrado impide inventar palabras; no alcanza para fijar
# la FORMA.
EJEMPLO = {
    "slug": "berlin-muro",
    "titulo": "El muro que se parte",
    "brief": "dos muros se abren y liberan una onda",
    "composicion": "confrontacion",
    "tono": "concreto",
    "capas": [
        {"rol": "lado_izq", "figura": "muro", "gesto": "desplazar_fuera",
         "ritmo": "lento"},
        {"rol": "lado_der", "figura": "muro", "gesto": "desplazar_fuera",
         "ritmo": "lento"},
        {"rol": "protagonista", "figura": "onda", "gesto": "emanar",
         "ritmo": "rapido"},
    ],
}


def resumen_para_prompt():
    """Vocabulario en texto compacto, para pegar en el prompt del agente."""
    L = ["VOCABULARIO CERRADO — usa solo estas palabras.", "", "FIGURAS:"]
    L += [f"  {k:<11} {v[1]}" for k, v in sorted(FIGURAS.items())]
    L += ["", "GESTOS:"]
    L += [f"  {k:<19} {v[1]}" for k, v in sorted(GESTOS.items())]
    L += ["", "TONOS: " + ", ".join(sorted(TONOS))]
    L += ["", "COMPOSICIONES (y sus roles):"]
    for c, r in sorted(COMPOSICIONES.items()):
        L.append(f"  {c:<24} {', '.join(sorted(r))}")
    L += ["", "RITMOS: " + ", ".join(sorted(RITMOS))]
    L += ["", "LA FORMA EXACTA, con todos los campos en el nivel de arriba:",
          json.dumps(EJEMPLO, ensure_ascii=False, indent=1),
          "", "Devuelve UN objeto con ESA forma: slug, titulo, brief, "
          "composicion, tono y capas van en el nivel de arriba, nunca "
          "anidados dentro de otra cosa."]
    return "\n".join(L)


if __name__ == "__main__":
    esquema = construir()
    if len(sys.argv) > 1:
        pathlib.Path(sys.argv[1]).write_text(
            json.dumps(esquema, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"OK {sys.argv[1]}")
        ruta = pathlib.Path(sys.argv[1]).with_name("vocabulario-prompt.txt")
        ruta.write_text(resumen_para_prompt(), encoding="utf-8")
        print(f"OK {ruta}")
    else:
        print(json.dumps(esquema, ensure_ascii=False, indent=2))
