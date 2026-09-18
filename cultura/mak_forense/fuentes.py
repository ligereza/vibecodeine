#!/usr/bin/env python3
"""Adapters: from a real source into `Registro`. All READ-ONLY.

Each adapter does two things and nothing else: it builds the records and
declares the limits that concrete source imposes on the analysis. Those
limits travel through to the report (`Cobertura.limites`) so a total is
never read as complete.

The three that exist today cover the three ways MAK records facts:

  testeos_rd  legacy spreadsheet -- the historical problem, no load time
  muestras_rd XIO-RD -- each sample with its real instant, which is what
              lets the wrong event be detected
  jsonl       any other area, mapping fields by name
"""
from __future__ import annotations

import datetime
import json
import os
import sqlite3
from pathlib import Path

try:
    from .registro import Registro
except ImportError:  # direct execution through forense.py
    from registro import Registro

DB_RD = os.path.expanduser(os.environ.get("FLUJO_RD_DB", "~/data/rd.db"))


def _abrir(db_path: str | Path) -> sqlite3.Connection:
    """A genuinely read-only connection (uri mode=ro), not by convention."""
    ruta = Path(db_path).expanduser().resolve()
    if not ruta.is_file():
        raise FileNotFoundError(ruta)
    conn = sqlite3.connect(ruta.as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _texto(valor) -> str:
    return str(valor).strip().lower() if valor is not None else ""


def _tiene_tabla(conn: sqlite3.Connection, nombre: str) -> bool:
    fila = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (nombre,),
    ).fetchone()
    return fila is not None


def epoch(valor) -> float | None:
    """Epoch instant from a number or an ISO string, or None.

    A date WITHOUT a time returns None on purpose: `2025-02-08` doesn't say
    when it was recorded, it says which day passed. Treating it as an
    instant would invent a load time (midnight) and would make every
    whole-day record look like it was loaded before its own event.
    """
    if valor is None or valor == "":
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    if texto.replace(".", "", 1).isdigit():
        return float(texto)
    if len(texto) <= 10:
        return None
    try:
        dt = datetime.datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.timestamp()


# --------------------------------------------------------------------------

def desde_testeos_rd(db_path: str | Path = DB_RD) -> tuple[list[Registro], tuple[str, ...]]:
    """`testeo_filas_fuente` -- the legacy spreadsheet, 2024/2025/2026.

    The content is the six fields that define a testing annotation.
    `test_2_raw`/`result_2_raw` are deliberately left out going forward:
    in the corpus copies those columns vary between copies of the same
    block, so including them made two identical rows look different --
    that was exactly the error that produced "26 unique sessions" where
    there were 9.
    """
    conn = _abrir(db_path)
    filas = conn.execute("""
        SELECT f.test_id, f.source_sheet_name, f.source_row, f.row_status,
               f.substance_raw, f.format_raw,
               f.test_1_raw, f.result_1_raw, f.test_2_raw, f.result_2_raw,
               e.date_iso_candidate, e.date_confidence, e.producer_name_candidate
          FROM testeo_filas_fuente f
          JOIN testeo_eventos_fuente e USING(event_id)
      ORDER BY f.source_sheet_name, f.source_row
    """).fetchall()
    conn.close()

    registros = [
        Registro(
            id=str(r["test_id"]),
            grupo=r["source_sheet_name"],
            orden=int(r["source_row"]),
            contenido=(_texto(r["substance_raw"]), _texto(r["format_raw"]),
                       _texto(r["test_1_raw"]), _texto(r["result_1_raw"]),
                       _texto(r["test_2_raw"]), _texto(r["result_2_raw"])),
            fecha_declarada=r["date_iso_candidate"],
            instante_registro=None,
            es_encabezado=(r["row_status"] == "repeated_header"),
            etiqueta=r["source_sheet_name"],
        )
        for r in filas
    ]

    inciertas = sum(1 for r in filas if (r["date_confidence"] or "none") in ("low", "none"))
    sin_productora = sum(1 for r in filas if not (r["producer_name_candidate"] or "").strip())
    limites = (
        "una planilla no guarda cuando se escribio una celda: sin instante de "
        "carga, el evento equivocado solo se detecta por contenido",
        f"{inciertas} de {len(filas)} filas tienen fecha de confianza baja o "
        f"nula (leida del nombre de la hoja): la direccion de un tramo ajeno "
        f"se corrobora con un dato debil",
        f"{sin_productora} filas pertenecen a jornadas sin productora resuelta: "
        f"un patron no se puede atribuir a quien organizo",
    )
    return registros, limites


def desde_muestras_rd(db_path: str | Path = DB_RD) -> tuple[list[Registro], tuple[str, ...]]:
    """`muestras` -- what XIO-RD loads in the field.

    Here there IS a load instant, and that's why the detectors the
    spreadsheet could never have run here: a sample saved before its
    event happens, or long after, is the volunteer who picked the wrong
    session from the list.

    The event date is looked up in the catalog, NEVER in the sample
    itself: comparing a field against itself detects nothing.
    """
    conn = _abrir(db_path)
    fechas_evento: dict[str, str] = {}
    for tabla, clave, fecha in (("productora_eventos", "id", "fecha"),
                                ("productora_eventos", "nombre", "fecha"),
                                ("testeo_eventos_fuente", "event_id", "date_iso_candidate"),
                                ("testeo_eventos_fuente", "event_label_candidate",
                                 "date_iso_candidate")):
        try:
            for row in conn.execute(f"SELECT {clave} k, {fecha} f FROM {tabla}"):
                if row["k"] and row["f"]:
                    fechas_evento.setdefault(str(row["k"]).strip().lower(), row["f"])
        except sqlite3.Error:
            continue

    tiene_capturas = _tiene_tabla(conn, "muestra_capturas")
    if tiene_capturas:
        filas = conn.execute("""
            SELECT m.id, m.fecha, m.evento_ref, m.evento_origen,
                   m.codigo_muestra, m.sustancia_declarada, m.tipo_muestra,
                   m.color, m.textura, m.logo_o_marca, m.peso_mg,
                   MIN(c.captured_at_epoch) AS captured_at_epoch
              FROM muestras AS m
              LEFT JOIN muestra_capturas AS c ON c.muestra_id = m.id
             WHERE COALESCE(m.descartada, 0) = 0
          GROUP BY m.id
          ORDER BY m.evento_ref, m.id
        """).fetchall()
    else:
        filas = conn.execute("""
            SELECT id, fecha, evento_ref, evento_origen, codigo_muestra,
                   sustancia_declarada, tipo_muestra, color, textura,
                   logo_o_marca, peso_mg, NULL AS captured_at_epoch
              FROM muestras
             WHERE COALESCE(descartada, 0) = 0
          ORDER BY evento_ref, id
        """).fetchall()
    conn.close()

    registros = []
    sin_evento = 0
    for r in filas:
        ref = (r["evento_ref"] or r["evento_origen"] or "sin_evento").strip()
        declarada = fechas_evento.get(ref.lower())
        if declarada is None:
            sin_evento += 1
        registros.append(Registro(
            id=str(r["codigo_muestra"] or r["id"]),
            grupo=ref,
            orden=int(r["id"]),
            contenido=(_texto(r["sustancia_declarada"]), _texto(r["tipo_muestra"]),
                       _texto(r["color"]), _texto(r["textura"]),
                       _texto(r["logo_o_marca"]), _texto(r["peso_mg"])),
            fecha_declarada=declarada,
            # `muestras.fecha` is the declared event date, not the time
            # the sample was captured. The real instant lives in XIO in
            # `muestra_capturas.captured_at_epoch`; if it doesn't exist,
            # it's left absent so the report declares the blind spot.
            instante_registro=(
                float(r["captured_at_epoch"])
                if r["captured_at_epoch"] is not None else None
            ),
            etiqueta=str(r["codigo_muestra"] or ""),
        ))

    sin_instante = sum(1 for r in registros if r.instante_registro is None)
    limites = (
        f"{sin_evento} muestras cuyo evento no esta fechado en el catalogo: "
        f"no se puede juzgar si la carga cae dentro de su jornada",
        (
            f"{sin_instante} muestras sin captura con timestamp: `muestras.fecha` "
            "es fecha del evento y no se usa como hora de carga"
        ),
    )
    return registros, limites


def desde_jsonl(path: str | Path, *, campo_grupo: str, campos_contenido: list[str],
                campo_orden: str | None = None, campo_id: str | None = None,
                campo_fecha: str | None = None,
                campo_instante: str | None = None,
                ) -> tuple[list[Registro], tuple[str, ...]]:
    """Any other MAK area: a JSONL and the name of its fields.

    This is the door that keeps the analysis from being just about the
    spreadsheet. The only thing each area has to decide is which field is
    the group and which fields define "the same annotation"; that
    decision belongs to the area, so it's requested explicitly instead of
    being guessed.
    """
    ruta = Path(path).expanduser()
    registros: list[Registro] = []
    faltantes = 0
    with ruta.open(encoding="utf-8", errors="replace") as fh:
        for i, linea in enumerate(fh):
            linea = linea.strip()
            if not linea:
                continue
            try:
                fila = json.loads(linea)
            except ValueError:
                faltantes += 1
                continue
            grupo = _texto(fila.get(campo_grupo)) or "sin_grupo"
            registros.append(Registro(
                id=str(fila.get(campo_id) or i),
                grupo=grupo,
                orden=int(fila.get(campo_orden) or i) if campo_orden else i,
                contenido=tuple(_texto(fila.get(c)) for c in campos_contenido),
                fecha_declarada=(str(fila[campo_fecha])
                                 if campo_fecha and fila.get(campo_fecha) else None),
                instante_registro=epoch(fila.get(campo_instante)) if campo_instante else None,
            ))
    limites = (
        f"los campos que definen «la misma anotacion» los eligio quien corrio "
        f"esto ({', '.join(campos_contenido)}): el analisis no puede validar "
        f"esa eleccion",
    )
    if faltantes:
        limites += (f"{faltantes} lineas ilegibles quedaron fuera",)
    return registros, limites
