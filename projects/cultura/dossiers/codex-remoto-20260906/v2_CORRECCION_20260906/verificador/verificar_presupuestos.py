#!/usr/bin/env python3
"""Verificador de presupuestos de las tres postulaciones.

Lee los CSV entregados, no cifras embebidas. Aritmetica decimal exacta.
Termina con codigo 1 si encuentra cualquier inconsistencia; 0 solo si todo pasa.

Uso:
    python3 verificar_presupuestos.py [--dir DIR] [--json]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

COLUMNAS = [
    "id_coste", "categoria", "concepto", "actividad", "periodo",
    "cantidad", "unidad", "precio_unitario", "subtotal",
    "producto", "proyecto_que_paga", "fundamento", "origen_del_valor",
]

ORIGENES = {"cotizacion", "referencia", "estimacion", "tope_normativo"}

# Reglas por linea, tomadas de las bases. Ver MATRIZ_REQUISITOS.md.
REGLAS = {
    "01_ama_amoedo.csv": {
        "nombre": "Ama Amoedo 2026 - Artistas",
        "moneda": "USD",
        "tope": Decimal("10000"),
        "categorias": {"Personal", "Operacion"},
        "tope_responsable": None,      # la base no fija tope de asignacion
        "tope_imprevistos": None,      # la base no define el item
        "prohibidas": set(),
        "fuente_tope": "Bases 2026, seccion Artistas: becas de USD 10.000",
    },
    "02_fondart_creacion.csv": {
        "nombre": "Fondart Regional 2027 - Creacion Artistica (Diseno)",
        "moneda": "CLP",
        "tope": Decimal("18000000"),
        "categorias": {"Personal", "Operacion", "Inversion", "Imprevistos"},
        "tope_responsable": Decimal("0.40"),
        "tope_imprevistos": Decimal("0.02"),
        "prohibidas": set(),
        "fuente_tope": "Bases Creacion, cap. I.6.2 y I.7",
    },
    "03_fondart_difusion.csv": {
        "nombre": "Fondart Regional 2027 - Difusion",
        "moneda": "CLP",
        "tope": Decimal("18000000"),
        "categorias": {"Personal", "Operacion", "Imprevistos"},
        "tope_responsable": Decimal("0.40"),
        "tope_imprevistos": Decimal("0.02"),
        "prohibidas": {"Inversion"},   # la linea NO contempla el item
        "fuente_tope": "Bases Difusion, cap. I.6.2 y I.7",
    },
    "04_fondart_formativas.csv": {
        "nombre": "Fondart Regional 2027 - Actividades Formativas",
        "moneda": "CLP",
        "tope": Decimal("15000000"),
        "categorias": {"Personal", "Operacion", "Imprevistos"},
        "tope_responsable": Decimal("0.40"),
        "tope_imprevistos": Decimal("0.02"),
        "prohibidas": {"Inversion"},
        "fuente_tope": "Bases Formativas, cap. I.6.2 y I.7",
    },
}

MARCA_RESPONSABLE = "asignacion del responsable"


class Falla(Exception):
    pass


def dec(valor: str, campo: str, fila: int) -> Decimal:
    txt = (valor or "").strip().replace(" ", "")
    if not txt:
        raise Falla(f"fila {fila}: {campo} vacio")
    try:
        d = Decimal(txt)
    except InvalidOperation:
        raise Falla(f"fila {fila}: {campo}={valor!r} no es un numero decimal")
    if d != d.to_integral_value() and d.as_tuple().exponent < -4:
        raise Falla(f"fila {fila}: {campo}={valor!r} tiene mas de 4 decimales")
    return d


def verificar_archivo(ruta: Path, reglas: dict) -> dict:
    errores: list[str] = []
    avisos: list[str] = []

    with ruta.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))

    if not filas:
        return {"errores": [f"{ruta.name}: sin filas"], "avisos": [], "total": Decimal(0),
                "por_categoria": {}, "filas": 0}

    faltan = [c for c in COLUMNAS if c not in filas[0]]
    if faltan:
        errores.append(f"{ruta.name}: faltan columnas {faltan}")
        return {"errores": errores, "avisos": avisos, "total": Decimal(0),
                "por_categoria": {}, "filas": len(filas)}
    sobran = [c for c in filas[0] if c not in COLUMNAS]
    if sobran:
        errores.append(f"{ruta.name}: columnas no declaradas {sobran}")

    total = Decimal(0)
    por_categoria: dict[str, Decimal] = {}
    responsable = Decimal(0)
    imprevistos = Decimal(0)
    ids: dict[str, int] = {}
    datos = []

    for n, fila in enumerate(filas, start=2):
        cat = (fila["categoria"] or "").strip()
        if cat.upper() == "TOTAL":
            continue
        try:
            if not (fila["id_coste"] or "").strip():
                raise Falla(f"fila {n}: id_coste vacio")
            idc = fila["id_coste"].strip()
            if idc in ids:
                raise Falla(f"fila {n}: id_coste {idc!r} duplicado (ya en fila {ids[idc]})")
            ids[idc] = n

            for campo in ("concepto", "actividad", "periodo", "unidad",
                          "producto", "proyecto_que_paga", "fundamento"):
                if not (fila[campo] or "").strip():
                    raise Falla(f"fila {n}: {campo} vacio")

            if cat not in reglas["categorias"]:
                raise Falla(f"fila {n}: categoria {cat!r} no permitida en esta linea "
                            f"(permitidas: {sorted(reglas['categorias'])})")
            if cat in reglas["prohibidas"]:
                raise Falla(f"fila {n}: la linea no contempla el item {cat!r}")

            origen = (fila["origen_del_valor"] or "").strip().lower()
            if origen not in ORIGENES:
                raise Falla(f"fila {n}: origen_del_valor {origen!r} invalido "
                            f"(permitidos: {sorted(ORIGENES)})")

            q = dec(fila["cantidad"], "cantidad", n)
            p = dec(fila["precio_unitario"], "precio_unitario", n)
            s = dec(fila["subtotal"], "subtotal", n)
            if q <= 0:
                raise Falla(f"fila {n}: cantidad debe ser > 0, es {q}")
            if p < 0:
                raise Falla(f"fila {n}: precio_unitario negativo ({p})")
            if q * p != s:
                raise Falla(f"fila {n}: subtotal {s} != cantidad {q} x precio {p} = {q * p}")

            total += s
            por_categoria[cat] = por_categoria.get(cat, Decimal(0)) + s
            if MARCA_RESPONSABLE in fila["concepto"].lower():
                responsable += s
            if cat == "Imprevistos":
                imprevistos += s
            datos.append(fila)
        except Falla as e:
            errores.append(f"{ruta.name}: {e}")

    if total > reglas["tope"]:
        errores.append(f"{ruta.name}: total {total} EXCEDE el tope {reglas['tope']} "
                       f"{reglas['moneda']} ({reglas['fuente_tope']})")

    # Denominador exacto = total solicitado al fondo, que es el total del CSV.
    if reglas["tope_responsable"] is not None and total > 0:
        frac = responsable / total
        if responsable == 0:
            avisos.append(f"{ruta.name}: no se encontro fila de '{MARCA_RESPONSABLE}'")
        elif frac > reglas["tope_responsable"]:
            errores.append(f"{ruta.name}: asignacion del responsable {responsable} = "
                           f"{frac * 100:.2f}% EXCEDE el tope "
                           f"{reglas['tope_responsable'] * 100:.0f}% del total solicitado")
    if reglas["tope_imprevistos"] is not None and total > 0:
        frac = imprevistos / total
        if frac > reglas["tope_imprevistos"]:
            errores.append(f"{ruta.name}: imprevistos {imprevistos} = {frac * 100:.2f}% "
                           f"EXCEDE el tope {reglas['tope_imprevistos'] * 100:.0f}%")

    return {"errores": errores, "avisos": avisos, "total": total,
            "por_categoria": por_categoria, "responsable": responsable,
            "imprevistos": imprevistos, "filas": len(datos), "ids": set(ids)}


def verificar_cruce(resultados: dict, base: Path) -> list[str]:
    """Un id_coste no puede pagarse dos veces. Si se repite entre archivos,
    debe declarar productos distintos y el mismo proyecto_que_paga."""
    errores = []
    visto: dict[str, tuple[str, str, str]] = {}
    for nombre in resultados:
        ruta = base / nombre
        if not ruta.exists():
            continue
        with ruta.open(encoding="utf-8", newline="") as fh:
            for fila in csv.DictReader(fh):
                if (fila.get("categoria") or "").strip().upper() == "TOTAL":
                    continue
                idc = (fila.get("id_coste") or "").strip()
                if not idc:
                    continue
                clave = (nombre, fila.get("producto", ""), fila.get("proyecto_que_paga", ""))
                if idc in visto:
                    prev = visto[idc]
                    errores.append(
                        f"id_coste {idc!r} aparece en {prev[0]} y en {nombre}: "
                        f"un mismo identificador de coste no puede pagarse dos veces")
                else:
                    visto[idc] = clave
    return errores


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent.parent / "presupuestos"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    base = Path(args.dir)

    resultados, errores_todos = {}, []
    for nombre, reglas in REGLAS.items():
        ruta = base / nombre
        if not ruta.exists():
            errores_todos.append(f"FALTA el archivo {nombre} en {base}")
            continue
        r = verificar_archivo(ruta, reglas)
        resultados[nombre] = r
        errores_todos.extend(r["errores"])

    errores_todos.extend(verificar_cruce(REGLAS, base))

    if args.json:
        print(json.dumps({
            "ok": not errores_todos,
            "errores": errores_todos,
            "totales": {k: str(v["total"]) for k, v in resultados.items()},
        }, ensure_ascii=False, indent=2))
    else:
        print(f"# Verificacion de presupuestos  --  {base}")
        for nombre, r in resultados.items():
            reglas = REGLAS[nombre]
            print(f"\n## {nombre}  ({reglas['nombre']})")
            print(f"   filas validas: {r['filas']}")
            for cat in sorted(r["por_categoria"]):
                v = r["por_categoria"][cat]
                pct = (v / r["total"] * 100) if r["total"] else Decimal(0)
                print(f"   {cat:<14} {v:>14,} {reglas['moneda']}   {pct:5.2f}%")
            print(f"   {'TOTAL':<14} {r['total']:>14,} {reglas['moneda']}"
                  f"   (tope {reglas['tope']:,})")
            if reglas["tope_responsable"] is not None and r["total"]:
                print(f"   responsable    {r['responsable']:>14,} = "
                      f"{r['responsable'] / r['total'] * 100:.2f}% (tope 40%)")
                print(f"   imprevistos    {r['imprevistos']:>14,} = "
                      f"{r['imprevistos'] / r['total'] * 100:.2f}% (tope 2%)")
            for a in r["avisos"]:
                print(f"   AVISO: {a}")
        print()
        if errores_todos:
            print(f"RESULTADO: FALLA con {len(errores_todos)} error(es)")
            for e in errores_todos:
                print(f"  ERROR {e}")
        else:
            print("RESULTADO: OK, sin inconsistencias")

    return 1 if errores_todos else 0


if __name__ == "__main__":
    raise SystemExit(main())
