#!/usr/bin/env python3
"""iconos.py -- CODEX: brief -> spec SEMANTICA -> compilador determinista -> SVG.

    python3 iconos.py "el muro que se parte y libera ondas"
                      [--densidad corto|medio|largo] [--tono X] [--ntfy]

La tesis, y la razon por la que este modo existe separado de `generar`: si el
agente SOLO puede expresar significado, no puede producir geometria rota. El
modelo no ve lo que escribe -- tiene un modelo estructural de la imagen, no
pictorico -- asi que escribir `<path d="M60,47 L36,-6...">` es escribir a
ciegas. Medido en la sesion que produjo el motor (2026-07-28): 44% de defectos
visuales escribiendo SVG directo contra ~11% via spec, con XML 100% valido en
los dos casos. La falla que sobrevive un pipeline sin supervision es
justamente la silenciosa: el XML roto grita, el circulo vacio no dice nada.

Cuatro modos de falla eliminados por CONSTRUCCION, no por revision:
  1. invisible en el frame 0 -- no hay forma de expresar "empieza en opacidad 0"
  2. texto desbordado       -- se mide antes de dibujarse
  3. contraste insuficiente -- WCAG calculado; si falla, cambia el rol de color
  4. XML roto               -- el agente no concatena strings

Lo que este modo NO resuelve, dicho sin adornos: el techo creativo. La metafora
queda en la ELECCION de piezas, no en la geometria especifica, y eso es una
expresividad menor. El motor es el piso para volumen; una pieza insignia se
sigue escribiendo a mano y se mira.
"""
import argparse
import json
import os
import re
import sys
import time

from codex_lib import (PIEZAS, guardar_pieza_generica, guardia_espera,
                       planner_llm, tiempo_ms)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_semantico import compilador, critico, esquema, calidad_svg  # noqa: E402
from motor_semantico.compilador import ErrorSemantico  # noqa: E402

sys.path.insert(0, "/home/mak/research")

# Dos rondas: la spec es corta y el error de validacion dice exactamente que
# palabra no existe y cuales son las validas, asi que reparar es barato. Mas
# de dos rondas y el problema no es el formato, es el pedido.
MAX_REPARACIONES = 2
TOK_SPEC = {"corto": 600, "medio": 900, "largo": 1400}


def _sistema():
    """El vocabulario CERRADO va en el prompt, no en la esperanza. No hay
    JSON-mode ni grammar-constrained decoding en estos proveedores (el wrapper
    postea messages/max_tokens y nada mas), asi que la garantia real es la
    validacion posterior: una palabra fuera de las listas se rechaza con las
    opciones validas en el mensaje."""
    return ("Eres el ilustrador del departamento Codex de MAK. NO dibujas: "
            "describes SIGNIFICADO. Nunca escribes coordenadas, ni colores, ni "
            "animaciones.\n\n" + esquema.resumen_para_prompt() +
            "\n\nDevuelves UN objeto JSON y nada mas: sin explicacion, sin "
            "bloque de codigo alrededor. Campos: slug, titulo, brief, "
            "composicion, tono, capas[]. Cada capa: rol y (figura o texto), "
            "mas gesto y ritmo opcionales. La capa 'protagonista' es la "
            "lectura principal y casi siempre hace falta.")


def _extraer_json(bruto):
    """El primer objeto JSON del texto del LLM, tolerando fences."""
    if not bruto:
        raise ValueError("el modelo devolvio vacio")
    m = re.search(r"\{.*\}", bruto, re.S)
    if not m:
        raise ValueError("el modelo no devolvio JSON: %r" % bruto[:160])
    return json.loads(m.group(0))


def _pedir_spec(planner, pedido, densidad, tono=None):
    extra = ("\nUSA el tono '%s'." % tono) if tono else ""
    return planner.call(
        _sistema(),
        'PEDIDO: "%s"%s\n\nEscribe la spec semantica.' % (pedido, extra),
        TOK_SPEC.get(densidad, 900))


def generar_icono(pedido, densidad="medio", tono=None):
    """Devuelve (path_md, meta). Nunca levanta: una spec irreparable tambien es
    una pieza, guardada con smoke_ok=False para que la mire un humano -- misma
    convencion que la ejecucion bloqueada de generar.py."""
    t0 = time.time()
    planner = planner_llm()

    print("STATUS: Escribiendo spec semantica (vocabulario cerrado)...",
          flush=True)
    bruto, real = _pedir_spec(planner, pedido, densidad, tono)

    spec, problemas = None, []
    for ronda in range(MAX_REPARACIONES + 1):
        try:
            candidata = _extraer_json(bruto)
            fallos = compilador.validar_spec(candidata)
            if fallos:
                raise ValueError("; ".join(fallos))
            spec = candidata
            break
        except (ValueError, json.JSONDecodeError) as e:
            problemas.append(str(e)[:220])
            if ronda == MAX_REPARACIONES:
                break
            print("STATUS: Spec invalida (ronda %d de %d), reparando..."
                  % (ronda + 1, MAX_REPARACIONES), flush=True)
            bruto, _ = planner.call(
                _sistema(),
                "Esta spec no paso la validacion:\n%s\n\nMOTIVO: %s\n\n"
                "Devuelve la spec JSON COMPLETA corregida, usando SOLO el "
                "vocabulario cerrado." % (bruto[:1200], str(e)[:400]),
                TOK_SPEC.get(densidad, 900))

    if spec is None:
        print("HALLAZGO: spec irreparable tras %d rondas -- %s"
              % (MAX_REPARACIONES, problemas[-1] if problemas else "?"),
              flush=True)
        meta = {"pedido": pedido, "modo": "iconos", "spec_por": real,
                "problemas": problemas, "smoke_ok": False,
                "smoke_stderr_tail": ("spec irreparable: "
                                      + " | ".join(problemas))[-300:],
                "llmCalls": {"planner": planner.stats},
                "errors": planner.errors[:10], "ms": tiempo_ms(t0)}
        _, path_md = guardar_pieza_generica(
            pedido, "", meta, ext="svg", lang="xml",
            nota_md="**Spec semantica irreparable tras %d rondas.** No hay SVG.\n\n"
                    "Motivos:\n\n- %s" % (MAX_REPARACIONES,
                                          "\n- ".join(problemas)))
        return path_md, meta

    print("STATUS: Compilando SVG (geometria determinista)...", flush=True)
    try:
        svg, avisos = compilador.compilar(spec, spec.get("slug", "icono"))
        error_compilador = ""
    except ErrorSemantico as e:
        svg, avisos, error_compilador = "", [], str(e)

    visual = (calidad_svg.validate(svg, spec.get("slug", "icono"))
              if svg else {"ok": False, "status": "invalid",
                           "reason": "compiler produced no SVG"})
    dedupe = (calidad_svg.find_duplicate(svg, PIEZAS)
              if svg else {"status": "unique", "method": "none"})
    veredicto = visual.get("metrics") or {}
    if not visual.get("ok"):
        avisos = list(avisos) + ["visual validation: %s" % visual.get("reason", "unknown")]
    if dedupe.get("status") == "duplicate":
        avisos = list(avisos) + ["duplicate visual: %s" % dedupe.get("duplicate_of", "?")]

    smoke_ok = (bool(svg) and not error_compilador and visual.get("ok") and
                dedupe.get("status") != "duplicate")
    meta = {"pedido": pedido, "modo": "iconos", "spec_por": real, "spec": spec,
            "avisos": list(avisos), "problemas": problemas,
            "visual_validation": visual, "dedupe": dedupe,
            "critico": {k: v for k, v in veredicto.items()
                        if k in ("puntaje", "alertas", "notas", "error")},
            "smoke_ok": smoke_ok,
            "llmCalls": {"planner": planner.stats},
            "errors": planner.errors[:10], "ms": tiempo_ms(t0)}
    if not smoke_ok:
        meta["smoke_stderr_tail"] = error_compilador[-300:]
    print("HALLAZGO: %s -- %s%s"
          % ("compilado" if smoke_ok else "rechazado por el compilador",
             real, ", %d avisos" % len(avisos) if avisos else ""), flush=True)

    nota = ["Spec semantica (lo unico que escribio el modelo):", "",
            "```json", json.dumps(spec, ensure_ascii=False, indent=1), "```"]
    if avisos:
        nota += ["", "Avisos del compilador:", ""] + ["- " + a for a in avisos]
    if visual:
        nota += ["", "Visual validation:", "```json",
                 json.dumps(visual, ensure_ascii=False, indent=1), "```"]
    if dedupe.get("status") == "duplicate":
        nota += ["", "Duplicate candidate preserved for audit: " +
                 str(dedupe.get("duplicate_of", "?"))]
    if veredicto.get("puntaje") is not None:
        nota += ["", "Critico perceptual: %s/100%s"
                 % (veredicto["puntaje"],
                    " -- " + "; ".join(veredicto["alertas"])
                    if veredicto.get("alertas") else "")]
    if error_compilador:
        nota += ["", "**Rechazado por el compilador:**", "", error_compilador]
    _, path_md = guardar_pieza_generica(pedido, svg, meta, ext="svg", lang="xml",
                                        nota_md="\n".join(nota))
    return path_md, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pedido")
    ap.add_argument("--densidad", choices=("corto", "medio", "largo"),
                    default="medio")
    ap.add_argument("--tono", default=None,
                    help="fuerza un tono del vocabulario (por defecto lo elige "
                         "el modelo: cada tema pide su propia presentacion)")
    ap.add_argument("--ntfy", action="store_true")
    a = ap.parse_args()

    if not guardia_espera():
        print("INFORME: (ninguno)")
        return 1
    path_md, meta = generar_icono(a.pedido, a.densidad, a.tono)
    estado = "ok" if meta.get("smoke_ok") else "fallo"
    print("codex iconos: %s, spec por %s, %d ms"
          % (estado, meta.get("spec_por", "?"), meta["ms"]))
    if a.ntfy:
        from research_lib import ntfy_publish
        ntfy_publish(os.environ.get("NTFY_TOPIC_OUT", ""),
                     "icono codex (%s): %s" % (estado, path_md),
                     title="codex iconos: " + a.pedido[:70])
    print("INFORME: " + path_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
