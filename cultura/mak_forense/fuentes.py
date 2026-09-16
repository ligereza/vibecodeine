#!/usr/bin/env python3
"""Adaptadores: de una fuente real a `Registro`. Todo en SOLO LECTURA.

Cada adaptador hace dos cosas y ninguna mas: arma los registros y declara los
limites que esa fuente concreta le impone al analisis. Esos limites viajan
hasta el informe (`Cobertura.limites`) para que un total nunca se lea como
completo.

Los tres que hay hoy cubren las tres formas en que MAK registra hechos:

  testeos_rd  planilla heredada -- el problema historico, sin hora de carga
  muestras_rd XIO-RD -- cada muestra con su instante real, que es lo que
              permite detectar el evento equivocado
  jsonl       cualquier otra area, mapeando campos por nombre
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
    """Conexion de solo lectura de verdad (uri mode=ro), no por convencion."""
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
    """Instante en epoch desde un numero o un ISO, o None.

    Una fecha SIN hora devuelve None a proposito: `2025-02-08` no dice cuando
    se anoto, dice que dia paso. Tratarla como instante inventaria una hora
    de carga (medianoche) y haria que cada registro de dia completo pareciera
    cargado antes de su propio evento.
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
    """`testeo_filas_fuente` -- la planilla heredada, 2024/2025/2026.

    El contenido son los seis campos que definen una anotacion de testeo. Se
    deja fuera `test_2_raw`/`result_2_raw` hacia adelante a proposito: en las
    copias del corpus esas columnas varian entre copias del mismo bloque, asi
    que incluirlas hacia que dos filas identicas parecieran distintas -- fue
    exactamente el error que dio "26 jornadas unicas" donde habia 9.
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
    """`muestras` -- lo que carga XIO-RD en terreno.

    Aca si hay instante de carga, y por eso aca si corren los detectores que
    la planilla nunca pudo tener: una muestra guardada antes de que su evento
    ocurra, o mucho despues, es el voluntario que eligio mal en la lista.

    La fecha del evento se busca en el catalogo, NUNCA en la propia muestra:
    comparar un campo contra si mismo no detecta nada.
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
            # `muestras.fecha` es la fecha declarada del evento, no la hora
            # en que se capturo la muestra. El instante real vive en XIO en
            # `muestra_capturas.captured_at_epoch`; si no existe, se deja
            # ausente para que el informe declare la ceguera.
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
    """Cualquier otra area de MAK: un JSONL y el nombre de sus campos.

    Esta es la puerta que hace que el analisis no sea de la planilla. Lo unico
    que hay que decidir por area es cual es el grupo y que campos definen
    "la misma anotacion"; esa decision es del area y por eso se pide explicita
    en vez de adivinarse.
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
