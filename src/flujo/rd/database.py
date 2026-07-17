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
_VENUES_DIR = _REPO / "knowledge" / "venues"     # *.yaml canonicos
_LOGOS_DIR = _REPO / "knowledge" / "logos"       # *.yaml canonicos
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
CREATE TABLE venues (
    id            TEXT PRIMARY KEY,   -- id canonico (espacio_riesco)
    nombre        TEXT NOT NULL,
    tipo          TEXT,               -- convention_center, club, ...
    escala        TEXT,               -- scale_default (mainstream/base/under)
    capacidad     TEXT,               -- capacity_bucket
    preset_reco   TEXT,               -- recommended_preset
    voluntarios_min INTEGER,
    requisitos    TEXT,               -- JSON: requirements_defaults
    notas         TEXT                -- JSON: notes[]
);
CREATE TABLE productora_tipos (
    id             INTEGER PRIMARY KEY,
    productora_slug TEXT NOT NULL REFERENCES productoras(slug),
    tipo           TEXT NOT NULL       -- vocab.TIPOS_FECHA
);
CREATE INDEX idx_prodtipos_slug ON productora_tipos(productora_slug);
CREATE INDEX idx_prodtipos_tipo ON productora_tipos(tipo);
CREATE TABLE productora_venues (
    id             INTEGER PRIMARY KEY,
    productora_slug TEXT NOT NULL REFERENCES productoras(slug),
    venue_nombre   TEXT NOT NULL,      -- nombre libre; venue_id si matchea uno canonico
    venue_id       TEXT REFERENCES venues(id),
    preferido      INTEGER NOT NULL,   -- 0/1: el reiterado/preferido
    estado         TEXT,               -- confirmado | inferido | ejemplo
    notas          TEXT
);
CREATE INDEX idx_prodvenues_slug ON productora_venues(productora_slug);
CREATE TABLE productora_logos (
    id             INTEGER PRIMARY KEY,
    productora_slug TEXT NOT NULL REFERENCES productoras(slug),
    logo_id        TEXT,               -- id del logo (thegrid_primary)
    knowledge      TEXT,               -- ruta al yaml de knowledge/logos
    estado         TEXT                -- status (source_needed, listo, ...)
);
CREATE INDEX idx_prodlogos_slug ON productora_logos(productora_slug);
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


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Lee un yaml canonico si PyYAML esta disponible. Sin yaml, devuelve None
    (la tabla venues queda vacia; el resto de la DB no se afecta)."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


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
    Pista derivada, no un dato del evento. Tras reconciliar precios con la
    fuente real (jefe area eventos 2026-07-02), INFO y TESTEO comparten 6
    voluntarios: para 6 el conteo NO distingue (lo hace incluye_testeo), asi
    que si mas de un pack matchea se devuelve None (ambiguo) en vez de adivinar.
    COMPLETO=15 sigue siendo unico."""
    if voluntarios is None:
        return None
    matches = [pid for pid, p in _load_packs().items() if int(p["voluntarios"]) == int(voluntarios)]
    return matches[0] if len(matches) == 1 else None


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


def build_rd_db(
    db_path: str | Path | None = None,
    *,
    productoras_dir: str | Path | None = None,
    venues_dir: str | Path | None = None,
) -> Path:
    """(Re)construye la DB RD desde las fuentes canonicas. Idempotente:
    borra el archivo previo y lo reescribe entero. Devuelve la ruta.

    productoras_dir/venues_dir permiten apuntar a directorios de prueba (los
    tests cargan una productora sintetica con venue preferido sin tocar el
    store real). Por defecto usan los canonicos del repo.
    """
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    prod_dir = Path(productoras_dir) if productoras_dir is not None else _PRODUCTORAS_DIR
    ven_dir = Path(venues_dir) if venues_dir is not None else _VENUES_DIR
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

        # venues canonicos (knowledge/venues/*.yaml)
        venue_ids: set[str] = set()
        if ven_dir.exists():
            for vf in sorted(ven_dir.glob("*.yaml")):
                v = _load_yaml(vf)
                if not v:
                    continue
                vid = str(v.get("id", vf.stem))
                venue_ids.add(vid)
                rs = v.get("recommended_service", {}) or {}
                conn.execute(
                    "INSERT OR REPLACE INTO venues(id, nombre, tipo, escala, capacidad, "
                    "preset_reco, voluntarios_min, requisitos, notas) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        vid,
                        str(v.get("name", vf.stem)),
                        v.get("type"),
                        v.get("scale_default"),
                        v.get("capacity_bucket"),
                        v.get("recommended_preset") or rs.get("default_preset"),
                        rs.get("volunteers_min") or (v.get("requirements_defaults", {}) or {}).get("volunteers_min"),
                        json.dumps(v.get("requirements_defaults", {}), ensure_ascii=False),
                        json.dumps(v.get("notes", []), ensure_ascii=False),
                    ),
                )

        # productoras conocidas (store) + tablas hijas: tipos, venues, logos
        tipo_id = vnk_id = logo_id = 0
        if prod_dir.exists():
            for pf in sorted(prod_dir.glob("*.json")):
                try:
                    d = json.loads(pf.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                slug = pf.stem
                conn.execute(
                    "INSERT OR REPLACE INTO productoras(slug, nombre, instagram, aliases, confirmado, notas) "
                    "VALUES (?,?,?,?,?,?)",
                    (
                        slug,
                        str(d.get("name", slug)),
                        d.get("instagram"),
                        json.dumps(d.get("aliases", []), ensure_ascii=False),
                        d.get("confirmed"),
                        d.get("notes"),
                    ),
                )
                # tipos de fecha (vocabulario controlado)
                from .vocab import normalize_tipos

                for tipo in normalize_tipos(d.get("tipos_fecha")):
                    tipo_id += 1
                    conn.execute(
                        "INSERT INTO productora_tipos(id, productora_slug, tipo) VALUES (?,?,?)",
                        (tipo_id, slug, tipo),
                    )
                # venues (anotados; preferido = el reiterado); venue_id si matchea uno canonico
                for v in d.get("venues", []) or []:
                    vnk_id += 1
                    vid = v.get("venue_id")
                    conn.execute(
                        "INSERT INTO productora_venues(id, productora_slug, venue_nombre, venue_id, "
                        "preferido, estado, notas) VALUES (?,?,?,?,?,?,?)",
                        (
                            vnk_id, slug,
                            str(v.get("nombre", vid or "")),
                            vid if vid in venue_ids else None,
                            1 if v.get("preferido") else 0,
                            v.get("estado", "confirmado"),
                            v.get("notas"),
                        ),
                    )
                # logos (enlace a knowledge/logos)
                for lg in d.get("logos", []) or []:
                    logo_id += 1
                    conn.execute(
                        "INSERT INTO productora_logos(id, productora_slug, logo_id, knowledge, estado) "
                        "VALUES (?,?,?,?,?)",
                        (logo_id, slug, lg.get("id"), lg.get("knowledge"), lg.get("estado")),
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


def venues(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Venues canonicos (requisitos y notas deserializados)."""
    conn = connect(db_path)
    try:
        out: list[dict[str, Any]] = []
        for v in conn.execute("SELECT * FROM venues ORDER BY nombre").fetchall():
            d = dict(v)
            d["requisitos"] = json.loads(d["requisitos"]) if d.get("requisitos") else {}
            d["notas"] = json.loads(d["notas"]) if d.get("notas") else []
            out.append(d)
        return out
    finally:
        conn.close()


def productora(slug: str, db_path: str | Path | None = None) -> dict[str, Any] | None:
    """Perfil completo de una productora: datos base + tipos de fecha + venues
    (con el preferido marcado) + logos. None si no existe."""
    conn = connect(db_path)
    try:
        row = conn.execute("SELECT * FROM productoras WHERE slug = ?", (slug,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["aliases"] = json.loads(d["aliases"]) if d.get("aliases") else []
        d["tipos_fecha"] = [
            r["tipo"] for r in conn.execute(
                "SELECT tipo FROM productora_tipos WHERE productora_slug = ?", (slug,)
            ).fetchall()
        ]
        d["venues"] = [
            dict(r) for r in conn.execute(
                "SELECT venue_nombre, venue_id, preferido, estado, notas FROM productora_venues "
                "WHERE productora_slug = ? ORDER BY preferido DESC, venue_nombre", (slug,)
            ).fetchall()
        ]
        d["venue_preferido"] = next((v["venue_nombre"] for v in d["venues"] if v["preferido"]), None)
        d["logos"] = [
            dict(r) for r in conn.execute(
                "SELECT logo_id, knowledge, estado FROM productora_logos WHERE productora_slug = ?", (slug,)
            ).fetchall()
        ]
        return d
    finally:
        conn.close()


def productoras_por_tipo(tipo: str, db_path: str | Path | None = None) -> list[str]:
    """Slugs de productoras que hacen fechas de un tipo dado (vocab canonico)."""
    from .vocab import normalize_tipo

    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT DISTINCT productora_slug FROM productora_tipos WHERE tipo = ? ORDER BY productora_slug",
            (normalize_tipo(tipo),),
        ).fetchall()
        return [r["productora_slug"] for r in rows]
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


def lookup_familia(familia: str, db_path: str | Path | None = None) -> dict[str, Any]:
    """Consulta de operador en terreno: para una familia de sustancia devuelve el
    panel de reactivos que la marcan + que packs incluyen servicio de testeo +
    el disclaimer presuntivo. Es el JOIN que justifica la DB sobre JSON planos:
    cruza reactivos (colorimetria) con packs (servicio) en una sola llamada.

    'Incluye testeo' se detecta en las inclusiones del pack (palabra 'testeo'),
    derivado del texto canonico -- no un flag aparte que pueda desincronizarse.
    """
    conn = connect(db_path)
    try:
        reacts = [
            dict(r) for r in conn.execute(
                "SELECT reactivo, familia, reaccion, hex FROM reactivos "
                "WHERE lower(familia) LIKE ? ORDER BY reactivo",
                (f"%{familia.lower()}%",),
            ).fetchall()
        ]
        packs_testeo = [
            dict(p) for p in conn.execute(
                "SELECT DISTINCT p.id, p.nombre, p.precio FROM packs p "
                "JOIN inclusiones i ON i.pack_id = p.id "
                "WHERE lower(i.texto) LIKE '%testeo%' ORDER BY p.orden"
            ).fetchall()
        ]
        disc_row = conn.execute(
            "SELECT valor FROM meta WHERE clave = 'reactivos_disclaimer'"
        ).fetchone()
        return {
            "familia": familia,
            "reactivos": reacts,
            "packs_con_testeo": packs_testeo,
            "disclaimer": disc_row["valor"] if disc_row else "",
        }
    finally:
        conn.close()
