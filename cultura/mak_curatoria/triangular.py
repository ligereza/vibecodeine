#!/usr/bin/env python3
"""Convierte los flyers de RD ya percibidos en preguntas de investigacion.

La formula es del usuario (2026-07-26): "si tienes headliner y tienes fecha =
tienes productora potencialmente encontrable por research". Ese paso nunca se
construyo: desde el 2026-07-23 hay 132 flyers con fecha y productora/handle
esperando en ~/curatoria/fichas/fichas.jsonl, y nadie los mando a research.

Esto NO investiga: arma la cola. Cada flyer con datos suficientes y productora
DESCONOCIDA se convierte en una pregunta concreta y verificable. Los que ya
traen productora se listan aparte como confirmables.

Salida: ~/curatoria/triangulacion.jsonl (una linea por pregunta) y un resumen
por pantalla. Nada se despacha solo; el despacho es una decision aparte.

Nota sobre el material viejo: las fichas del 2026-07-23 se hicieron con el
prompt unico, que NUNCA pedia headliners. Por eso aca el headliner se busca en
el texto OCR. Cuando el corpus se vuelva a percibir con PROMPT_RD -- que si los
pide -- esta cola va a ser mucho mas rica.
"""
import json
import os
import re

FICHAS = os.path.expanduser("~/curatoria/fichas/fichas.jsonl")
SALIDA = os.path.expanduser("~/curatoria/triangulacion.jsonl")

# Palabras que aparecen en flyers y no son nombres de artista.
RUIDO = {
    "presenta", "presents", "open", "air", "club", "party", "fiesta", "tickets",
    "entradas", "puerta", "lineup", "line", "up", "dj", "live", "set", "show",
    "reduciendo", "dano", "daño", "instagram", "www", "com", "cl", "hrs", "hs",
}


def posibles_headliners(texto):
    """Nombres candidatos del cartel, desde el OCR. Heuristica honesta: no
    pretende acertar siempre, solo proponer para que research verifique."""
    if not texto:
        return []
    cands = []
    for linea in texto.splitlines():
        s = linea.strip()
        if not (3 <= len(s) <= 40):
            continue
        palabras = [p for p in re.split(r"[^\wÁÉÍÓÚÑáéíóúñ]+", s) if p]
        if not (1 <= len(palabras) <= 4):
            continue
        if any(p.lower() in RUIDO for p in palabras):
            continue
        if not any(c.isalpha() for c in s):
            continue
        # Un nombre de cartel suele ir en mayusculas o Capitalizado.
        if s.isupper() or all(p[:1].isupper() for p in palabras if p[:1].isalpha()):
            cands.append(s)
    vistos, salida = set(), []
    for c in cands:
        k = c.lower()
        if k not in vistos:
            vistos.add(k)
            salida.append(c)
    return salida[:5]



def _txt(v):
    """El modelo a veces devuelve lista donde el schema pide string."""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v if x).strip()
    return str(v or "").strip()

def main():
    con_fecha = con_prod = preguntas = 0
    filas = []
    ultimas = {}
    with open(FICHAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except Exception:
                continue
            clave = "%s:%s" % (f.get("fuente", ""), f.get("ruta_rel", ""))
            ultimas[clave] = f
    for f in ultimas.values():
        if f.get("fuente") != "rd":
            continue
        if f.get("categoria") not in ("flyer_evento", "foto_evento"):
            continue
        e = f.get("datos_evento") or {}
        fecha = _txt(e.get("fecha"))
        prod = _txt(e.get("productora"))
        venue = _txt(e.get("venue"))
        handles = e.get("handles") or []
        if isinstance(handles, str): handles = [handles]
        heads = posibles_headliners(f.get("ocr_texto") or "")

        if fecha:
            con_fecha += 1
        if prod:
            con_prod += 1

        # Solo vale preguntar si hay fecha Y algo que identifique el evento.
        if not fecha or not (heads or handles or venue):
            continue
        if prod:
            estado = "confirmar"
            pregunta = (
                "Verificar si la productora '%s' organizo el evento del %s"
                % (prod, fecha)
                + (" en %s" % venue if venue else "")
                + (" con %s en el cartel" % ", ".join(heads[:3]) if heads else "")
                + ". Responder con fuente."
            )
        else:
            estado = "descubrir"
            pregunta = (
                "Que productora organizo el evento del %s" % fecha
                + (" en %s" % venue if venue else "")
                + (" con %s en el cartel" % ", ".join(heads[:3]) if heads else "")
                + (" (cuentas visibles: %s)" % ", ".join(handles[:3]) if handles else "")
                + "? Responder con la fuente que lo confirma."
            )
        preguntas += 1
        filas.append({
            "id_ficha": f.get("id"),
            "archivo": f.get("ruta_rel"),
            "estado": estado,
            "fecha": fecha,
            "venue": venue,
            "productora_declarada": prod,
            "handles": handles,
            "headliners_candidatos": heads,
            "pregunta": pregunta,
        })

    with open(SALIDA, "w", encoding="utf-8") as fh:
        for r in filas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    descubrir = sum(1 for r in filas if r["estado"] == "descubrir")
    print("  flyers con fecha        :", con_fecha)
    print("  flyers con productora   :", con_prod)
    print("  PREGUNTAS armadas       :", preguntas)
    print("    a descubrir           :", descubrir)
    print("    a confirmar           :", preguntas - descubrir)
    print("  salida                  :", SALIDA)
    if filas:
        print()
        print("  ejemplo:", filas[0]["pregunta"][:150])


if __name__ == "__main__":
    main()
