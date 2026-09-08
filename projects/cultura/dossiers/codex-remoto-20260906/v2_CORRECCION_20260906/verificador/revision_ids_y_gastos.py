#!/usr/bin/env python3
"""Revision de IDs de coste, gastos comunes duplicados y exclusion Creacion/Difusion.

Tres comprobaciones que el verificador de presupuestos no hace:

  1. IDs de coste: unicos en todo el paquete y con prefijo coherente con el
     proyecto que paga.
  2. Gastos comunes: conceptos que suelen repetirse entre proyectos (hosting,
     registro, desarrollo, difusion, respaldo). Si aparecen en mas de un
     presupuesto deben tener producto y periodo distintos; si el producto se
     repite, es doble imputacion.
  3. Exclusion mutua Creacion/Difusion: el Anexo 3 II.4 de las bases declara
     fuera de convocatoria las postulaciones de mismo contenido aunque cambien
     de linea. Los documentos del paquete deben declarar que se envia una sola,
     y nunca presentarlas como simultaneas.

Sale con codigo 1 ante cualquier hallazgo. Uso:
    python3 verificador/revision_ids_y_gastos.py
"""
from __future__ import annotations
import csv, re, sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRES = RAIZ / "presupuestos"

CSVS = {
    "01_ama_amoedo.csv":        ("AMA", "Ama Amoedo 2026 Artistas"),
    "02_fondart_creacion.csv":  ("CRE", "Fondart Creacion 2027"),
    "03_fondart_difusion.csv":  ("DIF", "Fondart Difusion 2027"),
    "04_fondart_formativas.csv":("FOR", "Fondart Formativas 2027"),
}

# Conceptos que tipicamente se cobran dos veces cuando hay un motor comun.
COMUNES = {
    "hosting":   r"hosting|dominio",
    "registro":  r"registro (documental|audiovisual|y sistematizacion|fotografico)",
    "desarrollo":r"desarrollo|implementaci[oó]n del|exportaci[oó]n",
    "respaldo":  r"respaldo|almacenamiento",
    "difusion":  r"difusi[oó]n (de|y convocatoria)",
    "impresion": r"impresi[oó]n",
}

errores: list[str] = []
notas: list[str] = []

def leer(nombre: str) -> list[dict]:
    p = PRES / nombre
    if not p.exists():
        errores.append(f"falta {nombre}")
        return []
    return [r for r in csv.DictReader(p.open(encoding="utf-8"))
            if (r.get("categoria") or "").strip().upper() not in ("TOTAL", "")]

# ---------- 1. IDs ----------
print("## 1. IDs de coste")
vistos: dict[str, str] = {}
n_ids = 0
for nombre, (pref, proyecto) in CSVS.items():
    for r in leer(nombre):
        idc = (r["id_coste"] or "").strip()
        n_ids += 1
        if not idc:
            errores.append(f"{nombre}: fila con id_coste vacio ({r['concepto'][:40]})")
            continue
        if idc in vistos:
            errores.append(f"id_coste {idc!r} repetido en {vistos[idc]} y {nombre}")
        vistos[idc] = nombre
        if not re.match(rf"^[A-Z]{{1,3}}-{pref}-\d{{2}}$", idc):
            errores.append(f"{nombre}: id_coste {idc!r} no sigue el patron X-{pref}-NN")
        if (r["proyecto_que_paga"] or "").strip() != proyecto:
            errores.append(f"{nombre}: {idc} declara proyecto_que_paga "
                           f"{r['proyecto_que_paga']!r}, se esperaba {proyecto!r}")
print(f"   {n_ids} ids revisados, {len(vistos)} unicos")

# ---------- 2. Gastos comunes ----------
print("## 2. Gastos comunes entre proyectos")
for etiqueta, patron in COMUNES.items():
    apar = []
    for nombre, (_pref, proyecto) in CSVS.items():
        for r in leer(nombre):
            if re.search(patron, r["concepto"], re.I):
                apar.append((nombre, r["id_coste"], r["producto"].strip(),
                             r["periodo"].strip(), r["concepto"][:60]))
    if len(apar) <= 1:
        notas.append(f"{etiqueta}: aparece {len(apar)} vez -> sin riesgo de duplicacion")
        continue
    productos = defaultdict(list)
    for a in apar:
        productos[a[2].lower()].append(a)
    repetidos = {p: v for p, v in productos.items() if len(v) > 1}
    if repetidos:
        for p, v in repetidos.items():
            errores.append(f"{etiqueta}: el producto {p!r} se paga en "
                           f"{', '.join(x[0] for x in v)} -> posible doble imputacion")
    else:
        notas.append(f"{etiqueta}: {len(apar)} apariciones con "
                     f"{len(productos)} productos distintos -> separado correctamente")
        for a in apar:
            notas.append(f"      {a[1]:<10} {a[0]:<26} producto={a[2]!r} periodo={a[3]}")
print(f"   {len(COMUNES)} conceptos comunes revisados")

# ---------- 3. Exclusion Creacion / Difusion ----------
print("## 3. Exclusion mutua Creacion / Difusion")
MD = {p: p.read_text(encoding="utf-8", errors="replace")
      for p in RAIZ.rglob("*.md") if "v1_ENTREGA" not in str(p)}

# 3a. debe existir una declaracion explicita de exclusion
DECLARA = re.compile(
    r"(no se postulan las dos|no se envían las dos|no se envian las dos|"
    r"no debe(?:n)? (?:enviar|presentar)se|se postula (?:sólo )?una|"
    r"sustituye a difusi[oó]n|alternativa de difusi[oó]n|"
    r"nunca una postulaci[oó]n simult|no se env[ií]a junto)", re.I)
declarantes = [p for p, t in MD.items() if DECLARA.search(t)]
if not declarantes:
    errores.append("ningun documento declara que Creacion y Difusion son excluyentes")
print(f"   documentos que declaran la exclusion: {len(declarantes)}")

# 3b. ningun documento puede presentarlas como simultaneas
SIMULT = re.compile(
    r"(creaci[oó]n\s+y\s+difusi[oó]n|difusi[oó]n\s+y\s+creaci[oó]n)", re.I)
# Sólo es un hallazgo si la mención conjunta aparece junto a un verbo de envío
# o de recomendación: nombrar ambas bases en una tabla normativa es legítimo.
ENVIO = re.compile(r"postul|env[íi]|present|recomend|adjudic|simult", re.I)
NEG = re.compile(r"\bno\b|nunca|riesgo|mismo contenido|excluyent|una de las dos|"
                 r"sustituye|alternativa|en vez de|en lugar de|s[oó]lo una", re.I)
for p, t in MD.items():
    for m in SIMULT.finditer(t):
        ventana = t[max(0, m.start() - 220): m.end() + 220]
        if not ENVIO.search(ventana):
            notas.append(f"{p.relative_to(RAIZ)}: menciona {m.group(0)!r} en contexto "
                         f"normativo, sin verbo de envío -> no aplica")
            continue
        if not NEG.search(ventana):
            errores.append(f"{p.relative_to(RAIZ)}: menciona "
                           f"{m.group(0)!r} junto a un verbo de envío "
                           f"sin marcar que son excluyentes")

# 3c. la recomendacion vigente no debe incluir Creacion
leeme = RAIZ / "LEEME_CIERRE.md"
if leeme.exists():
    t = leeme.read_text(encoding="utf-8")
    bloque = t[:t.index("## 3.")] if "## 3." in t else t
    if re.search(r"^\|\s*\*\*[123]\*\*\s*\|.*creaci[oó]n", bloque, re.I | re.M):
        errores.append("LEEME_CIERRE.md: Creacion aparece en la tabla de las tres recomendadas")
print("   revisada la tabla de recomendacion vigente")

# ---------- salida ----------
print()
for n in notas:
    print(f"   {n}")
print()
if errores:
    print(f"RESULTADO: FALLA con {len(errores)} hallazgo(s)")
    for e in errores:
        print(f"  ERROR  {e}")
    sys.exit(1)
print("RESULTADO: OK. IDs unicos, gastos comunes separados y exclusion Creacion/Difusion declarada")
