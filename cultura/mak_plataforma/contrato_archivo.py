# -*- coding: utf-8 -*-
"""The substrate contract: micelio graph -> pieces + relations, ONE shape.

Why this module exists (2026-07-29): the data/contract/skin split existed only
for iskvw, and MAK's micelio had its own nodes and its own drawing -- the same
work done twice, so a new skin served only one of them. The layer in between
is a contract of PIECES and RELATIONS that does not know whether the works are
the artist's or MAK's (iskvw/ESQUEMA_ARCHIVO.md). This module is that
conversion as a PURE function, shared by the two consumers:

- `tools/gen_archivo_iskvw.py` (repo side) delegates its micelio branch here,
  so id formation lives in exactly one place -- the "<hash>-<mediaid>.md" vs
  stem mismatch that once produced 1004 pieces / 0 positions cannot fork again.
- `cultura/mak_plataforma/hub.py` (box side, covered by the MAK-REPO-SYNC
  cron) serves it at GET /api/archivo, so any skin or external agent can ask
  the organism's face for "the pieces and their links" and always get the
  same shape, without knowing the micelio's internal node schema.

The rule it inherits is the doublecup thesis: no element may claim a datum it
does not encode. An artist work keeps an EMPTY titulo (machine perception is
not authorship; it travels as extra.percibido), an absent date stays absent,
and every field a consumer does not know is a field it ignores.

Pure stdlib, no I/O: callers fetch the graph payload themselves.

Retirement: when the contract gains a schema version the micelio itself emits.
"""
from __future__ import annotations

import re
import unicodedata

# 'corpus' are the artist's perceived works; the rest MAK wrote itself.
_CLASE_POR_DIR = {"corpus": "obra", "codex": "codigo"}

_EXTENSIONES = (".md", ".txt", ".json", ".jpg", ".jpeg", ".png", ".webp")


def _id(texto: str) -> str:
    base = unicodedata.normalize("NFKD", str(texto or ""))
    base = base.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:60] or "sin-id"


def _id_pieza(texto: str) -> str:
    """A piece's id, without the file suffix.

    The micelio names its nodes after the whole file
    ("b7fd4e77b4a2-17926032902806396.md") while the campo uses the stem, so
    `_id()` produced "...-md" on one side and not the other and positions
    NEVER joined: 1004 pieces, 0 with position. The extension is where the
    datum is stored, not which piece it is.
    """
    s = str(texto or "")
    for ext in _EXTENSIONES:
        if s.lower().endswith(ext):
            s = s[: -len(ext)]
            break
    return _id(s)


def convertir(grafo: dict) -> dict:
    """Micelio graph payload ({"nodes": [...], "edges": [...]}) -> the
    contract shape {"piezas": [...], "vinculos": [...]}.

    What MAK wrote ABOUT an artist work is PERCEPTION, not a title. It used
    to enter as `titulo`, and the contract ended up asserting that a work is
    called "Una mujer sentada bajo una estructura de madera" -- machine voice
    signing as the artist. For works the title stays EMPTY (silence before
    borrowed voice) and the text travels as `extra.percibido`, which a skin
    may use to search and place without showing it as authorship. For reports
    and code, which MAK wrote, the title IS its own.
    """
    piezas = []
    for n in grafo.get("nodes", []):
        cl = _CLASE_POR_DIR.get(n.get("dir"), "informe")
        texto = str(n.get("titulo") or "").strip()
        es_obra = cl == "obra"
        piezas.append({
            "id": _id_pieza(n.get("id")),
            "titulo": "" if es_obra else (texto or _id_pieza(n.get("id"))),
            "clase": cl,
            "fecha": None,
            "resumen": None,
            "etiquetas": [n["dir"]] if n.get("dir") else [],
            "peso": int(n.get("chunks") or 1),
            "medio": {"tipo": "texto"},
            "estado": "publicada",
            "extra": {k: v for k, v in (
                ("carpeta", n.get("dir")),
                ("percibido", texto if es_obra else None),
            ) if v},
        })

    conocidas = {p["id"] for p in piezas}
    vinculos = [{
        "de": _id_pieza(e["a"]), "a": _id_pieza(e["b"]),
        "peso": round(float(e.get("w") or 0), 3), "clase": "semantico",
    } for e in grafo.get("edges", [])
        if _id_pieza(e.get("a")) in conocidas and _id_pieza(e.get("b")) in conocidas]
    return {"piezas": piezas, "vinculos": vinculos}


def desde_ensayo(ensayo: dict) -> dict:
    """An ENSAYO with its iconographic annex -> the same contract shape.

    Why here and not in the generator: an essay exists on BOTH sides. The repo
    keeps the curated ones under `docs/cultura/ensayos/<tema>/`, and the box
    writes them to `~/research/informes/` (`research.py --formato ensayo`). One
    pure function, two consumers -- the same reason `convertir()` lives here.
    This is what makes MAK's output reach the portfolio instead of stopping at
    a folder nobody reads.

    `ensayo` is what the caller already has on disk, nothing invented:
        {"slug", "titulo", "fecha"?, "resumen"?, "ruta"?,
         "conceptos": [{"n", "slug", "titulo", "descripcion", "ancla"?,
                        "archivo"?, "estilo"?}]}

    Three classes of piece and two of link, and every one of them encodes
    something the manifest really says (the doublecup rule -- no element claims
    a datum it does not encode):

    - the essay              -> clase `informe`, its own title (MAK wrote it)
    - each nameable concept  -> clase `concepto`, linked to the essay
    - each icon that EXISTS  -> clase `pieza_grafica`, medio svg, linked to its
      concept. An icon declared in the manifest but missing from disk produces
      NO piece: a piece that claims a file that is not there is exactly the
      lie this contract forbids.

    Links are `clase: "manual"`, never `semantico`: nobody measured a distance
    here, the relation is declared by the manifest. Calling it measured would
    be the same defect as the tag-derived links pretending to be semantic.
    """
    slug_ensayo = _id(ensayo.get("slug") or ensayo.get("titulo") or "ensayo")
    id_ensayo = "ensayo-%s" % slug_ensayo
    piezas = [{
        "id": id_ensayo,
        "titulo": str(ensayo.get("titulo") or slug_ensayo),
        "clase": "informe",
        "fecha": ensayo.get("fecha"),
        "resumen": ensayo.get("resumen"),
        "etiquetas": ["ensayo", "cultura"],
        "peso": max(1, len(ensayo.get("conceptos") or [])),
        "medio": ({"tipo": "texto", "src": ensayo["ruta"]}
                  if ensayo.get("ruta") else {"tipo": "texto"}),
        "estado": "publicada",
        "extra": {"formato": "ensayo"},
    }]
    vinculos = []
    for c in ensayo.get("conceptos") or []:
        titulo = str(c.get("titulo") or "").strip()
        if not titulo:
            continue                      # sin nombre no es un concepto nombrable
        id_concepto = "concepto-%s-%s" % (slug_ensayo, _id(c.get("slug") or titulo))
        piezas.append({
            "id": id_concepto,
            "titulo": titulo,
            "clase": "concepto",
            "fecha": None,
            "resumen": str(c.get("descripcion") or "").strip() or None,
            "etiquetas": ["ensayo", slug_ensayo],
            "peso": 1,
            "medio": {"tipo": "texto"},
            "estado": "publicada",
            "extra": {k: v for k, v in (("ancla", c.get("ancla")),
                                        ("n", c.get("n"))) if v},
        })
        vinculos.append({"de": id_concepto, "a": id_ensayo, "peso": 1.0,
                         "clase": "manual"})
        src = c.get("archivo_src")
        if not src:
            continue                      # el icono no existe en disco: no entra
        id_icono = "icono-%s-%s" % (slug_ensayo, _id(c.get("slug") or titulo))
        piezas.append({
            "id": id_icono,
            "titulo": titulo,
            "clase": "pieza_grafica",
            "fecha": None,
            "resumen": str(c.get("descripcion") or "").strip() or None,
            "etiquetas": [e for e in ["icono", "animado", slug_ensayo,
                                      (c.get("estilo") or "").strip()] if e],
            "peso": 1,
            "medio": {"tipo": "imagen", "src": src},
            "estado": "publicada",
            # `declara_animacion` y no `anima`: lo que el archivo codifica es
            # que TIENE keyframes, y eso lo puede ver quien lo lee sin
            # rasterizar. Que se MUEVA de forma perceptible es otra cosa y se
            # mide aparte contando cuadros distintos (`iconos_conjunto animar`,
            # y `tests/test_iconos_conjunto.py` exige que todo icono que declara
            # keyframes se mueva dentro de su propio ciclo). Son dos hechos
            # distintos y el contrato solo puede afirmar el que el archivo
            # codifica -- la regla que existe para hacer cumplir.
            "extra": ({"declara_animacion": True}
                      if c.get("declara_animacion") else {}),
        })
        vinculos.append({"de": id_icono, "a": id_concepto, "peso": 1.0,
                         "clase": "manual"})
    return {"piezas": piezas, "vinculos": vinculos}


def desde_campo(campo: dict) -> dict:
    """Las obras CURADAS del campo medido, al contrato.

    campo.json es la proyeccion de lo que MAK percibio de las obras reales del
    artista (la carpeta de material que se mando a curar), ya pasada por el
    filtro que el usuario configuro. Hasta ahora solo daba POSICIONES: si el
    micelio no estaba alcanzable (CI, maquina apagada), el archivo salia sin
    las obras -- un portafolio sin las obras del artista. Esta conversion las
    hace piezas de primera clase con lo que el campo si midio.

    `titulo` va None a proposito: el artista no titulo estas piezas y el
    percibido es texto de maquina -- va a `extra.percibido`, nunca como
    titulo (regla de la VOZ). `unir()` deduplica contra el micelio por id y
    la fuente mas rica completa los campos.
    """
    piezas = []
    for c in campo.get("piezas") or []:
        cid = c.get("id")
        if not cid:
            continue
        extra = {}
        for k in ("colores", "tipo", "estilo", "tilde", "trazo", "percibido"):
            if c.get(k):
                extra[k] = c[k]
        piezas.append({
            "id": cid,
            "titulo": None,
            "clase": "obra",
            "fecha": None,
            "resumen": None,
            "etiquetas": [t for t in ("curada", c.get("tipo")) if t],
            "peso": 1,
            "medio": ({"tipo": "imagen", "src": c["archivo"]}
                      if c.get("archivo") else {"tipo": "imagen"}),
            "estado": "publicada",
            "extra": extra,
        })
    return {"piezas": piezas, "vinculos": []}


def desde_laser(manifiesto: dict, campo: dict, existe=None) -> dict:
    """Las piezas laser/plotter derivadas del material, al contrato.

    `flujo laser lote` camina la carpeta de material y deriva un svg por
    imagen (rayado o campo de flujo, semilla del nombre). La clave de union
    con el campo curado es el MEDIA ID: campo.json trae
    `archivo: posts/<media_id>.mp4` y el material se llama `<media_id>.jpg`
    -- mismos digitos, misma obra. Una pieza cuyo stem no calza con ninguna
    obra curada entra igual (es material del artista) pero sin vinculo.
    Mismas reglas duras: svg ausente = pieza que no entra.
    """
    if existe is None:
        from pathlib import Path as _P
        raiz = _P(__file__).resolve().parents[2]
        existe = lambda src: (raiz / src).is_file()  # noqa: E731
    por_stem = {}
    for c in campo.get("piezas") or []:
        archivo = c.get("archivo") or ""
        stem = archivo.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if stem:
            por_stem[stem] = c["id"]
    piezas, vinculos = [], []
    for fila in manifiesto.get("piezas") or []:
        stem = fila.get("stem")
        src = fila.get("src")
        if not stem or not src or not existe(src):
            continue
        id_pieza = "laser-%s" % stem
        obra = por_stem.get(stem)
        piezas.append({
            "id": id_pieza,
            "titulo": stem,
            "clase": "pieza_grafica",
            "fecha": None,
            "resumen": None,
            "etiquetas": ["laser", fila.get("modo") or "flow", "plotter"],
            "peso": 1,
            "medio": {"tipo": "imagen", "src": src},
            "estado": "publicada",
            "extra": ({"derivada_de": obra, "semilla": fila.get("semilla")}
                      if obra else {"semilla": fila.get("semilla")}),
        })
        if obra:
            vinculos.append({"de": id_pieza, "a": obra, "peso": 1.0,
                             "clase": "manual"})
    return {"piezas": piezas, "vinculos": vinculos}


def desde_animadas(manifiesto: dict, existe=None) -> dict:
    """Las piezas animadas derivadas de las obras curadas, al contrato.

    El generador (`tools/gen_animadas_obras.py`) deriva UNA pieza por obra con
    el motor semantico, determinista desde el id. Aca vive la conversion por
    la misma razon que `desde_ensayo`: la pieza existe en ambos lados (el repo
    la versiona, la caja puede regenerarla) y dos conversiones divergen.

    Mismas reglas del esquema: el vinculo es `manual` (lo declara el
    manifiesto, nadie midio una distancia) y una pieza cuyo svg NO esta en
    disco no entra -- el contrato no afirma lo que no puede mostrarse.
    `existe` se inyecta en tests; por defecto pregunta al disco real.
    """
    if existe is None:
        from pathlib import Path as _P
        raiz = _P(__file__).resolve().parents[2]
        existe = lambda src: (raiz / src).is_file()  # noqa: E731
    piezas, vinculos = [], []
    for fila in manifiesto.get("piezas") or []:
        oid = fila.get("obra_id")
        src = fila.get("src")
        if not oid or not src or not existe(src):
            continue
        id_pieza = "animada-%s" % oid
        piezas.append({
            "id": id_pieza,
            "titulo": str(fila.get("titulo") or oid),
            "clase": "pieza_grafica",
            "fecha": None,
            "resumen": None,
            "etiquetas": ["animada", "generativa", "motor-semantico"],
            "peso": 1,
            "medio": {"tipo": "imagen", "src": src},
            "estado": "publicada",
            "extra": ({"declara_animacion": True, "derivada_de": oid}
                      if fila.get("declara_animacion")
                      else {"derivada_de": oid}),
        })
        vinculos.append({"de": id_pieza, "a": oid, "peso": 1.0,
                         "clase": "manual"})
    return {"piezas": piezas, "vinculos": vinculos}
