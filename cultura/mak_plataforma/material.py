#!/usr/bin/env python3
"""La cola de trabajo que sale del material real, no de la propia salida.

MAK tenia cuatro fuentes de trabajo -- concepto, definir, modulo, backlog -- y
las cuatro nacen de lo que MAK ya escribio: el backlog se cosecha de las
"LAGUNAS DE INFORMACION" de sus propios informes, y las semillas son una lista
fija. Eso esta bien como MODO AUTONOMO (sin material nuevo, o sin internet), que
es para lo que se diseno. El defecto medido el 2026-07-26 es que corria como
modo POR DEFECTO teniendo 57 GB de material del usuario y red disponible: 2
trabajos de 24 ese dia, todos sobre genealogia cultural.

Esta cola invierte eso. Sale de lo percibido:

  RD    -> triangulacion: flyer con fecha + headliner y productora desconocida
           se convierte en una pregunta verificable para research.
           (formula del usuario: "si tienes headliner y tienes fecha = tienes
           productora potencialmente encontrable por research")

  iskvw -> lo que la propia obra propuso: `linea_investigacion` va a research,
           `oportunidad_codigo` va a codex.

Salida: ~/plataforma/material.jsonl, una tarea por linea, deduplicada por hash
del texto. trabajo.py la consume ANTES que las fuentes autonomas; cuando se
vacia, el organismo vuelve solo a su modo autonomo.

Uso:
    python3 material.py            # reconstruye la cola desde las fichas
    python3 material.py --contar   # solo informa cuanto hay
"""
import hashlib
import json
import os
import sys

FICHAS = os.path.expanduser("~/curatoria/fichas/fichas.jsonl")
COLA = os.path.expanduser("~/plataforma/material.jsonl")


# Palabras que aparecen en un cartel y no son el nombre de nadie. Sale de mirar
# lo que el modelo devolvio de verdad, no de imaginar: "FULL" fue el primer
# falso positivo que llego a produccion.
_NO_SON_ARTISTAS = {
    "full", "live", "set", "dj", "djs", "lineup", "line up", "guest",
    "invitado", "invitados", "residentes", "special", "guests", "b2b",
    "showcase", "presenta", "presents", "vs", "and", "more", "tba",
}


def _txt(v):
    if isinstance(v, list):
        return ", ".join(str(x) for x in v if x).strip()
    return str(v or "").strip()


def _hash(texto):
    return hashlib.sha1(texto.lower().encode("utf-8")).hexdigest()[:12]


def tareas_desde_fichas():
    vistos = set()
    tareas = []
    if not os.path.exists(FICHAS):
        return tareas
    with open(FICHAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except Exception:
                continue
            fuente = f.get("fuente")
            v = f.get("vision") or {}
            e = f.get("datos_evento") or {}

            if fuente == "rd":
                fecha = _txt(e.get("fecha"))
                heads = e.get("headliners") or []
                if isinstance(heads, str):
                    heads = [heads]
                heads = [h for h in (str(x).strip() for x in heads) if h]
                prod = _txt(e.get("productora"))
                venue = _txt(e.get("venue"))
                # Solo los flyers de evento triangulan. Medido el 2026-07-26:
                # el modelo le pone `headliners` a un LOGO ("GRID SYSTEM",
                # "street machine" son marcas, no artistas del cartel), y eso
                # ensuciaba la cola con preguntas que no son preguntas.
                if f.get("categoria") != "flyer_evento":
                    continue
                # Sin fecha o sin cartel no hay como triangular.
                if not fecha or not heads:
                    continue
                # Ruido tipico del OCR: una sola palabra generica y corta no es
                # el nombre de nadie ("FULL", "LIVE", "SET").
                heads = [h for h in heads
                         if len(h) > 3 and h.lower() not in _NO_SON_ARTISTAS]
                if not heads:
                    continue
                if prod:
                    continue  # ya se sabe quien fue; no se pregunta de nuevo
                texto = (
                    "Que productora organizo el evento del %s con %s en el cartel%s? "
                    "Responder solo si hay fuente que lo confirme; si no, decir que "
                    "no se encontro."
                    % (fecha, ", ".join(heads[:3]),
                       " en %s" % venue if venue else "")
                )
                depto, modo = "research", "research"

            elif fuente == "ig":
                # Una obra puede proponer las DOS cosas: una pregunta que vale
                # investigar y un procedimiento que vale programar. Antes esto
                # era un elif y la linea de investigacion se perdia cada vez que
                # tambien habia oportunidad de codigo -- probado el 2026-07-26
                # con una ficha que traia ambas y genero una sola tarea.
                propuestas = []
                oport = _txt(v.get("oportunidad_codigo"))
                if oport:
                    propuestas.append((oport, "codex", "generar"))
                linea_inv = _txt(v.get("linea_investigacion"))
                if linea_inv:
                    propuestas.append((linea_inv, "research", "research"))
                if not propuestas:
                    continue
            else:
                continue

            if fuente == "rd":
                propuestas = [(texto, depto, modo)]

            for texto_t, depto_t, modo_t in propuestas:
                h = _hash(texto_t)
                if h in vistos:
                    continue
                vistos.add(h)
                tareas.append({
                    "id": h,
                    "origen": fuente,
                    "ficha": f.get("id"),
                    "archivo": f.get("ruta_rel"),
                    "depto": depto_t,
                    "modo": modo_t,
                    "texto": texto_t,
                    "estado": "pendiente",
                })
    return tareas


def cargar():
    if not os.path.exists(COLA):
        return []
    filas = []
    with open(COLA, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                filas.append(json.loads(linea))
            except Exception:
                continue
    return filas


def guardar(filas):
    tmp = COLA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in filas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, COLA)


def pop_pendiente():
    """Saca la primera tarea pendiente y la marca. Devuelve None si no hay.

    Lo usa trabajo.py. Si devuelve None, el organismo cae a su modo autonomo,
    que es exactamente para lo que ese modo existe.
    """
    filas = cargar()
    for r in filas:
        if r.get("estado") == "pendiente":
            r["estado"] = "despachada"
            guardar(filas)
            return r
    return None


def reconstruir():
    previas = {r.get("id"): r for r in cargar()}
    nuevas = tareas_desde_fichas()
    salida = []
    for t in nuevas:
        # No revivir lo ya despachado: la cola no se repite sola.
        anterior = previas.get(t["id"])
        salida.append(anterior if anterior else t)
    guardar(salida)
    pend = sum(1 for r in salida if r.get("estado") == "pendiente")
    return len(salida), pend


def main():
    if "--contar" in sys.argv:
        filas = cargar()
        pend = sum(1 for r in filas if r.get("estado") == "pendiente")
        print("  tareas en cola: %d | pendientes: %d" % (len(filas), pend))
        return
    total, pend = reconstruir()
    por_depto = {}
    for r in cargar():
        if r.get("estado") == "pendiente":
            por_depto[r.get("depto")] = por_depto.get(r.get("depto"), 0) + 1
    print("  tareas totales   :", total)
    print("  pendientes       :", pend)
    print("  por departamento :", por_depto or "{}")
    print("  cola             :", COLA)


if __name__ == "__main__":
    main()
