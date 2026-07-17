"""Constructor y consultas de la base de datos RD (SQLite).

Fuentes canonicas (unica verdad; la DB es su proyeccion):
- projects/cultura/identidad/reactivos.json  -> tabla `reactivos` + `meta` (disclaimer)
- src/flujo/plano/packs.py (PACKS)           -> tablas `packs` e `inclusiones`
- projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json
                                             -> tabla `suplementos`
- data/productoras/*.json                    -> tabla `productoras` (promotoras conocidas)
- jobs/**/evento*.json + projects/plano/ejemplos/evento*.json
                                             -> tabla `eventos` (con pack sugerido por voluntarios)

Regenerar: `build_rd_db()` borra y reescribe todo desde las fuentes. Nunca se
edita la DB a mano; si un dato cambia, se cambia la fuente y se reconstruye.

Nota de seguridad del dominio: el test de reactivo es PRESUNTIVO (indica familia
posible, no identifica ni mide pureza). El disclaimer canonico viaja en la tabla
`meta` y toda salida que muestre un color debe poder citarlo -- un color no
vuelve segura una sustancia.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = _REPO / "data" / "rd.db"

# Fuentes canonicas
_REACTIVOS_JSON = _REPO / "projects" / "cultura" / "identidad" / "reactivos.json"
_SUPLEMENTOS_JSON = (
    _REPO / "projects" / "piezas_vectoriales" / "suplementos_rd"
    / "01_contenido" / "contenido_suplementos_rd.json"
)
_PRODUCTORAS_DIR = _REPO / "data" / "productoras"
# Directorios donde viven jsons con forma de evento (voluntarios/asistentes/...)
_EVENTOS_GLOBS = (
    (_REPO / "jobs", "**/evento*.json"),
    (_REPO / "projects" / "plano" / "ejemplos", "evento*.json"),
)
# Campos minimos para considerar un json como "evento" (evita packs_servicios y otros)
_EVENTO_MARKERS = ("voluntarios", "asistentes_estimados")

_SCHEMA = """
CREATE TABLE meta (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
CREATE TABLE reactivos (
    id INTEGER PRIMARY KEY,
    reactivo TEXT NOT NULL,     -- Marquis, Mecke, ...
    familia  TEXT NOT NULL,     -- MDMA / MDA, anfetamina, opiaceos, ...
    reaccion TEXT NOT NULL,     -- descripcion del cambio de color
    hex      TEXT NOT NULL      -- color de referencia estetica (#rrggbb)
);
CREATE INDEX idx_reactivos_familia  ON reactivos(familia);
CREATE INDEX idx_reactivos_reactivo ON reactivos(reactivo);
CREATE TABLE packs (
    id          TEXT PRIMARY KEY,   -- INFO | TESTEO | COMPLETO
    nombre      TEXT NOT NULL,
    label       TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio      INTEGER NOT NULL,   -- CLP
    voluntarios INTEGER NOT NULL,
    m2          INTEGER NOT NULL,
    stands      INTEGER NOT NULL,
    orden       INTEGER NOT NULL
);
CREATE TABLE inclusiones (
    id      INTEGER PRIMARY KEY,
    pack_id TEXT NOT NULL REFERENCES packs(id),
    texto   TEXT NOT NULL,
    orden   INTEGER NOT NULL
);
CREATE INDEX idx_inclusiones_pack ON inclusiones(pack_id);
CREATE TABLE suplementos (
    id            TEXT PRIMARY KEY,
    titulo        TEXT NOT NULL,
    tag           TEXT,
    accent        TEXT,
    descripcion   TEXT,
    section_title TEXT,
    items         TEXT              -- JSON: lista de items del flyer
);
CREATE TABLE productoras (
    slug      TEXT PRIMARY KEY,     -- slug del nombre (match)
    nombre    TEXT NOT NULL,
    instagram TEXT,
    aliases   TEXT,                 -- JSON: formas literales que extrae la vision
    confirmado TEXT,                -- nota de confirmacion humana
    notas     TEXT
);
CREATE TABLE eventos (
    id                   INTEGER PRIMARY KEY,
    nombre               TEXT NOT NULL,
    fuente               TEXT NOT NULL,   -- ruta relativa del json de origen
    duracion_horas       INTEGER,
    voluntarios          INTEGER,
    asistentes_estimados INTEGER,
    incluye_testeo       INTEGER,         -- 0/1
    masivo               INTEGER,         -- 0/1
    ubicacion            TEXT,
    pack_sugerido        TEXT REFERENCES packs(id),  -- por match de voluntarios
    notas                TEXT
);
"""


def _astext(value: Any) -> str | None:
    """Coacciona un campo a texto para SQLite. None queda None; listas/dicts se
    serializan a JSON (algunos flyers traen `description` como lista de parrafos);
    escalares a str."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _load_packs() -> dict[str, dict[str, Any]]:
    """Importa PACKS del modulo canonico (no duplica los numeros aca)."""
    from flujo.plano.packs import ALL_PACKS, PACKS

    return {pid: PACKS[pid] for pid in ALL_PACKS}


def _pack_por_voluntarios(voluntarios: int | None) -> str | None:
    """Sugiere el pack cuyo numero de voluntarios coincide con el del evento.
    Es una pista derivada, no un dato del evento (por eso vive en la DB, no en
    la fuente): INFO=2, TESTEO=6, COMPLETO=15."""
    if voluntarios is None:
        return None
    for pid, p in _load_packs().items():
        if int(p["voluntarios"]) == int(voluntarios):
            return pid
    return None


def _iter_evento_sources() -> list[tuple[str, dict[str, Any]]]:
    """Encuentra jsons con forma de evento y los devuelve como (ruta_rel, dict),
    ordenados por ruta para salida deterministica. Descarta jsons que no traen
    los marcadores de evento (packs_servicios, contenidos, etc.)."""
    encontrados: list[tuple[str, dict[str, Any]]] = []
    vistos: set[Path] = set()
    for base, patron in _EVENTOS_GLOBS:
        if not base.exists():
            continue
        for f in sorted(base.glob(patron)):
            if f in vistos:
                continue
            vistos.add(f)
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(d, dict):
                continue
            if not all(m in d for m in _EVENTO_MARKERS):
                continue
            encontrados.append((f.relative_to(_REPO).as_posix(), d))
    return encontrados


def build_rd_db(db_path: str | Path | None = None) -> Path:
    """(Re)construye la DB RD desde las fuentes canonicas. Idempotente:
    borra el archivo previo y lo reescribe entero. Devuelve la ruta."""
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()

    conn = sqlite3.connect(path)
    try:
        conn.executescript(_SCHEMA)

        # meta + reactivos
        reactivos_doc = json.loads(_REACTIVOS_JSON.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO meta(clave, valor) VALUES (?, ?)",
            ("reactivos_disclaimer", reactivos_doc.get("disclaimer", "")),
        )
        for i, r in enumerate(reactivos_doc.get("reacciones", []), start=1):
            conn.execute(
                "INSERT INTO reactivos(id, reactivo, familia, reaccion, hex) VALUES (?,?,?,?,?)",
                (i, r["reactivo"], r["familia"], r["reaccion"], r["hex"]),
            )

        # packs + inclusiones
        inc_id = 0
        for orden, (pid, p) in enumerate(_load_packs().items(), start=1):
            conn.execute(
                "INSERT INTO packs(id, nombre, label, descripcion, precio, voluntarios, m2, stands, orden) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (pid, p["nombre"], p["label"], p["desc"], int(p["precio"]),
                 int(p["voluntarios"]), int(p["m2"]), int(p["stands"]), orden),
            )
            for j, texto in enumerate(p.get("inclusiones", []), start=1):
                inc_id += 1
                conn.execute(
                    "INSERT INTO inclusiones(id, pack_id, texto, orden) VALUES (?,?,?,?)",
                    (inc_id, pid, texto, j),
                )

        # suplementos (flyers del contenido canonico)
        sup_doc = json.loads(_SUPLEMENTOS_JSON.read_text(encoding="utf-8"))
        for f in sup_doc.get("flyers", []):
            conn.execute(
                "INSERT INTO suplementos(id, titulo, tag, accent, descripcion, section_title, items) "
                "VALUES (?,?,?,?,?,?,?)",
                (
                    str(f.get("id")),
                    str(f.get("title", "")),
                    _astext(f.get("tag")),
                    _astext(f.get("accent")),
                    _astext(f.get("description")),
                    _astext(f.get("section_title")),
                    json.dumps(f.get("items", []), ensure_ascii=False),
                ),
            )

        # productoras conocidas (store de promotoras)
        if _PRODUCTORAS_DIR.exists():
            for pf in sorted(_PRODUCTORAS_DIR.glob("*.json")):
                try:
                    d = json.loads(pf.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                conn.execute(
                    "INSERT OR REPLACE INTO productoras(slug, nombre, instagram, aliases, confirmado, notas) "
                    "VALUES (?,?,?,?,?,?)",
                    (
                        pf.stem,
                        str(d.get("name", pf.stem)),
                        d.get("instagram"),
                        json.dumps(d.get("aliases", []), ensure_ascii=False),
                        d.get("confirmed"),
                        d.get("notes"),
                    ),
                )

        # eventos (jsons con forma de evento) + pack sugerido por voluntarios
        for i, (rel, d) in enumerate(_iter_evento_sources(), start=1):
            vol = d.get("voluntarios")
            conn.execute(
                "INSERT INTO eventos(id, nombre, fuente, duracion_horas, voluntarios, "
                "asistentes_estimados, incluye_testeo, masivo, ubicacion, pack_sugerido, notas) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    i,
                    str(d.get("nombre", rel)),
                    rel,
                    d.get("duracion_horas"),
                    vol,
                    d.get("asistentes_estimados"),
                    1 if d.get("incluye_testeo") else 0,
                    1 if d.get("masivo") else 0,
                    d.get("ubicacion"),
                    _pack_por_voluntarios(vol),
                    d.get("notas"),
                ),
            )
        conn.commit()
    finally:
        conn.close()
    return path


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Abre la DB (la construye si no existe). Filas como dict-like (Row)."""
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    if not path.exists():
        build_rd_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def reactivos_por_familia(familia: str, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Reacciones cuya familia contiene `familia` (case-insensitive).
    Ej: 'MDMA' -> las filas de Marquis/Mecke/... para MDMA."""
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT reactivo, familia, reaccion, hex FROM reactivos "
            "WHERE lower(familia) LIKE ? ORDER BY reactivo",
            (f"%{familia.lower()}%",),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def reactivos_por_reactivo(reactivo: str, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Todas las reacciones de un reactivo dado (Marquis, Mecke, ...)."""
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT reactivo, familia, reaccion, hex FROM reactivos "
            "WHERE lower(reactivo) = ? ORDER BY familia",
            (reactivo.lower(),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def packs(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Los packs de servicio con sus inclusiones anidadas, en orden."""
    conn = connect(db_path)
    try:
        out: list[dict[str, Any]] = []
        for p in conn.execute("SELECT * FROM packs ORDER BY orden").fetchall():
            d = dict(p)
            d["inclusiones"] = [
                r["texto"] for r in conn.execute(
                    "SELECT texto FROM inclusiones WHERE pack_id = ? ORDER BY orden", (d["id"],)
                ).fetchall()
            ]
            out.append(d)
        return out
    finally:
        conn.close()


def suplementos(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Los suplementos del catalogo (items deserializados)."""
    conn = connect(db_path)
    try:
        out: list[dict[str, Any]] = []
        for s in conn.execute("SELECT * FROM suplementos ORDER BY id").fetchall():
            d = dict(s)
            d["items"] = json.loads(d["items"]) if d.get("items") else []
            out.append(d)
        return out
    finally:
        conn.close()


def productoras(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Promotoras conocidas (aliases deserializados)."""
    conn = connect(db_path)
    try:
        out: list[dict[str, Any]] = []
        for p in conn.execute("SELECT * FROM productoras ORDER BY slug").fetchall():
            d = dict(p)
            d["aliases"] = json.loads(d["aliases"]) if d.get("aliases") else []
            out.append(d)
        return out
    finally:
        conn.close()


def eventos(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Eventos registrados con su pack sugerido por voluntarios."""
    conn = connect(db_path)
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM eventos ORDER BY id").fetchall()]
    finally:
        conn.close()


def disclaimer(db_path: str | Path | None = None) -> str:
    """El disclaimer canonico del testeo presuntivo (tabla meta)."""
    conn = connect(db_path)
    try:
        row = conn.execute("SELECT valor FROM meta WHERE clave = 'reactivos_disclaimer'").fetchone()
        return row["valor"] if row else ""
    finally:
        conn.close()
