#!/usr/bin/env python3
"""Mete el archivo del artista (iskvw) dentro del micelio.

El micelio relacionaba solo lo que MAK escribio sobre si mismo: 283 documentos,
todos informes propios. Las 709 obras del archivo del artista, ya percibidas el
2026-07-23, quedaban fuera. El mapa conceptual que el usuario queria -- "que
todas las obras estuvieran relacionadas semanticamente" -- no podia existir
porque las obras no eran nodos.

Esto convierte cada ficha de fuente 'ig' en un documento .md dentro de
~/research/corpus/, que es una FUENTE mas del indice. A partir de ahi el micelio
relaciona obras entre si y con la investigacion, que es el "todo" pedido.

RD queda FUERA a proposito. Son dos trabajos distintos (palabras del usuario,
2026-07-26): los flyers no son para curar sino para extraer datos, y su camino
es la triangulacion (headliner + fecha -> productora), no el mapa semantico.

Idempotente: reescribe solo si el contenido cambio, para no invalidar
embeddings ya calculados (el indice es incremental por mtime).
"""
import json
import os
import pathlib
import re

FICHAS = os.path.expanduser("~/curatoria/fichas/fichas.jsonl")
DESTINO = pathlib.Path(os.path.expanduser("~/research/corpus"))


def _slug(texto, n=60):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (texto or "").lower()).strip("-")
    return (s or "obra")[:n]


def documento(f):
    """La ficha como documento legible. Lo que se embebe es este texto."""
    v = f.get("vision") or {}
    partes = []
    desc = (v.get("descripcion") or "").strip()
    # El H1 es lo que memoria.py usa como titulo, y es lo unico que ve el usuario
    # cuando el hub le muestra con que se relaciona una idea suya. El id de
    # Instagram (18 digitos) no le dice nada a nadie, asi que el encabezado es la
    # primera frase de lo percibido. NO es un titulo del artista y no se presenta
    # como tal: el id sigue abajo, en la linea del archivo, que es el dato duro.
    id_archivo = pathlib.Path(f.get("ruta_rel") or "obra").stem
    frase = desc.split(". ")[0].strip().rstrip(".")
    titulo = frase[:90] if frase else id_archivo
    partes.append("# %s" % titulo)
    partes.append("")
    partes.append("Obra del archivo iskvw. Archivo: `%s`" % f.get("ruta_rel"))
    partes.append("")

    if desc:
        partes.append(desc)
        partes.append("")

    # Campos del prompt nuevo (aparecen cuando se vuelva a percibir con
    # PROMPT_ISKVW). Los viejos no los tienen y no se inventan.
    for clave, rotulo in (
        ("conceptos", "Conceptos"),
        ("materiales", "Materiales"),
        ("colores", "Colores"),
    ):
        val = v.get(clave)
        if isinstance(val, list) and val:
            partes.append("**%s:** %s" % (rotulo, ", ".join(str(x) for x in val)))
    for clave, rotulo in (
        ("tecnica", "Tecnica"),
        ("estilo", "Estilo"),
        ("datos_extraibles", "Datos extraibles"),
        ("linea_investigacion", "Linea de investigacion"),
        ("oportunidad_codigo", "Oportunidad de codigo"),
    ):
        val = (v.get(clave) or "").strip() if isinstance(v.get(clave), str) else ""
        if val:
            partes.append("**%s:** %s" % (rotulo, val))

    texto_visible = (v.get("texto_visible") or f.get("ocr_texto") or "").strip()
    if texto_visible:
        partes.append("")
        partes.append("**Texto en la obra:**")
        partes.append("")
        partes.append(texto_visible[:2000])

    partes.append("")
    partes.append("---")
    partes.append("meta: %s" % json.dumps(
        {"id": f.get("id"), "fuente": "iskvw", "tipo": f.get("tipo"),
         "categoria": f.get("categoria"), "mtime": f.get("mtime")},
        ensure_ascii=False))
    return "\n".join(partes) + "\n"


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    escritos = sin_cambio = saltados = 0
    with open(FICHAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except Exception:
                continue
            if f.get("fuente") != "ig":
                continue          # RD va por triangulacion, no por el mapa
            v = f.get("vision") or {}
            if not (v.get("descripcion") or "").strip():
                saltados += 1     # sin percepcion util no hay nodo
                continue
            nombre = "%s-%s.md" % (f.get("id", "sin-id"),
                                   _slug(pathlib.Path(f.get("ruta_rel") or "").stem))
            destino = DESTINO / nombre
            nuevo = documento(f)
            if destino.exists() and destino.read_text(encoding="utf-8") == nuevo:
                sin_cambio += 1
                continue
            destino.write_text(nuevo, encoding="utf-8")
            escritos += 1
    print("  obras escritas al corpus :", escritos)
    print("  sin cambios              :", sin_cambio)
    print("  saltadas (sin percepcion):", saltados)
    print("  carpeta                  :", DESTINO)


if __name__ == "__main__":
    main()
