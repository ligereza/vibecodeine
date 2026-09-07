#!/usr/bin/env python3
"""Genera ../PARA_COPIAR/: un archivo por documento, limpio y listo para pegar.

Sin tablas, sin notas internas, sin marcas de version: solo el texto que va al
formulario o a la impresora. Se genera desde campos_*.py; reejecutar tras editar.
"""
from __future__ import annotations
import re, textwrap
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DEST = AQUI.parent / "PARA_COPIAR"
DEST.mkdir(exist_ok=True)
import campos_ama, campos_difusion, campos_formativas, campos_creacion

# (modulo, prefijo de archivo, [(campo, nombre de salida)])
DOCS = [
 (campos_ama, "AMA", [
   ("Descripción del proyecto — versión extendida", "descripcion_del_proyecto"),
   ("Objetivos", "objetivos"),
   ("Plan de implementación", "plan_de_implementacion"),
   ("Justificación del interés en participar", "justificacion"),
   ("Presupuesto: destino de los fondos", "presupuesto_explicado"),
 ]),
 (campos_difusion, "DIFUSION", [
   ("Resumen — versión extendida", "resumen"),
   ("Fundamentación", "fundamentacion"),
   ("Objetivos", "objetivos"),
   ("Metodología", "metodologia"),
   ("Plan y fundamentación de la estrategia de difusión", "anexo_plan_de_difusion"),
   ("Estrategia de públicos y acceso", "anexo_estrategia_de_publicos"),
   ("Actividades, resultados e indicadores", "actividades_e_indicadores"),
   ("Presupuesto", "presupuesto_explicado"),
   ("Currículo del responsable", "curriculo"),
   ("Sostenibilidad", "sostenibilidad"),
 ]),
 (campos_formativas, "FORMATIVAS", [
   ("Resumen — versión extendida", "resumen"),
   ("Diagnóstico de la necesidad formativa", "anexo_diagnostico_de_necesidad"),
   ("Programa de la formación", "anexo_programa_formativo"),
   ("Estrategias de transferencia de aprendizajes", "anexo_transferencia"),
   ("Objetivos", "objetivos"),
   ("Indicadores y verificadores", "indicadores"),
   ("Presupuesto", "presupuesto_explicado"),
   ("Sostenibilidad", "sostenibilidad"),
 ]),
 (campos_creacion, "CREACION", [
   ("Resumen", "resumen"),
   ("Fundamentación", "fundamentacion"),
   ("Propuesta creativa", "anexo_propuesta_creativa"),
   ("Estrategias de difusión de la obra", "anexo_estrategias_de_difusion"),
   ("Objetivos, metodología y cronograma", "objetivos_metodologia_cronograma"),
   ("Producción y pruebas", "produccion_y_pruebas"),
   ("Espacio y montaje", "espacio_y_montaje"),
   ("Accesibilidad", "accesibilidad"),
   ("Indicadores y verificadores", "indicadores"),
   ("Currículo del responsable", "curriculo"),
   ("Presupuesto", "presupuesto_explicado"),
   ("Sostenibilidad", "sostenibilidad"),
 ]),
]

def limpio(t: str) -> str:
    """Quita marcas de markdown que no sirven pegadas en un formulario."""
    t = t.strip()
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)          # negritas
    t = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", t) # cursivas
    t = re.sub(r"`(.+?)`", r"\1", t)                # codigo
    return t

def envolver(t: str, ancho: int = 78) -> str:
    salida = []
    for bloque in t.split("\n\n"):
        lineas = bloque.split("\n")
        # las tablas y las listas numeradas se dejan como estan
        if any(l.lstrip().startswith("|") for l in lineas):
            salida.append(bloque); continue
        if all(re.match(r"^\s*(\d+[.)]|[-•])\s", l) or not l.strip() for l in lineas):
            salida.append("\n".join(textwrap.fill(l, ancho, subsequent_indent="   ")
                                    if l.strip() else "" for l in lineas)); continue
        salida.append(textwrap.fill(" ".join(l.strip() for l in lineas), ancho))
    return "\n\n".join(salida)

n = 0
for mod, pref, pares in DOCS:
    idx = {c["campo"].strip().lower(): c for c in mod.CAMPOS}
    for campo, salida in pares:
        c = idx.get(campo.strip().lower())
        if c is None:
            raise SystemExit(f"ERROR: el campo {campo!r} no existe en {mod.__name__}")
        cuerpo = envolver(limpio(c["texto"]))
        pal = len(re.findall(r"\S+", cuerpo))
        cab = (f"{campo}\n{'=' * len(campo)}\n"
               f"[{pal} palabras · {len(cuerpo)} caracteres · corte 2026-09-06]\n"
               f"[pegar desde la linea siguiente]\n\n")
        (DEST / f"{pref}__{salida}.txt").write_text(cab + cuerpo + "\n", encoding="utf-8")
        n += 1

# Indice de la carpeta
L = ["# PARA_COPIAR — textos limpios, listos para pegar o imprimir", "",
 "Generados por `postulaciones/generar_para_copiar.py`. Cada archivo lleva su",
 "conteo de palabras y caracteres en la cabecera, entre corchetes: **la cabecera",
 "no se pega**, el texto empieza en la linea que ella indica.", "",
 "Sin negritas, sin cursivas, sin comillas de codigo y con lineas de 78",
 "caracteres, para que entren en un campo de formulario o en una impresora sin",
 "arrastrar formato.", "",
 "**Ninguno de estos archivos requiere firma.** Los que si la requieren estan en",
 "`postulaciones/BORRADORES_SIN_FIRMA/`.", "",
 "| Archivo | Expediente | Documento | Palabras |", "|---|---|---|---:|"]
for f in sorted(DEST.glob("*.txt")):
    pref, resto = f.stem.split("__", 1)
    t = f.read_text(encoding="utf-8")
    m = re.search(r"\[(\d+) palabras", t)
    L.append(f"| `{f.name}` | {pref} | {resto.replace('_',' ')} | {m.group(1) if m else '?'} |")
L += ["", f"Total: **{n} archivos**.", "",
 "## Lo que no esta aqui, y donde esta", "",
 "| Documento | Donde |",
 "|---|---|",
 "| Ficha tecnica del instrumento | `postulaciones/ANEXOS/FICHA_TECNICA_IRIS.md` |",
 "| Guion de demostracion y capturas | `postulaciones/ANEXOS/GUION_DEMO.md` |",
 "| Cronograma de ejecucion | `cronogramas/EJECUCION_2027.md` |",
 "| Carga del responsable por escenario | `cronogramas/CARGA_Y_ESCENARIOS.md` |",
 "| Presupuestos con desglose por linea | `presupuestos/*.csv` |",
 "| Solicitud de espacio, cotizacion o carta | `postulaciones/BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md` |",
 "| Planilla de 15 compromisos de asistencia | `postulaciones/BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv` |",
 ""]
(DEST / "LEEME.md").write_text("\n".join(L), encoding="utf-8")
print(f"PARA_COPIAR: {n} archivos de texto + LEEME.md")
