#!/usr/bin/env python3
"""extraccion_db.py -- CURATORIA de MAK: fichas de percepcion -> candidatos DB.

Consolida fichas.jsonl (schema de percepcion.py: fuente, ruta_rel, tipo,
categoria, ocr_texto, vision{descripcion,estilo,colores,tipo_obra},
datos_evento{productora,venue,fecha,handles}, calidad_senal, error) en
candidatos de productora/venue para data/productoras y knowledge/venues,
con 3 reglas obligatorias (evidencia real, no negociables):

1. Colapso de secuencias: fichas del mismo directorio cuyo nombre es
   numerico correlativo (0001.png..0NNN.png) o difiere solo en sufijo
   numerico = UNA obra. Representante = mejor calidad_senal (alta>media>
   baja); se conserva miembros_n. Evidencia: un video frame-dump inflaba
   una productora x200.
2. Fuzzy-match (difflib, texto normalizado: lower/sin tildes/sin
   puntuacion) contra data/productoras/*.json y knowledge/productoras|
   venues/*.yaml -- ratio>=0.82 = canonico, 0.70-0.82 = dudoso, <0.70 =
   "nuevo?". Jamas se manda texto literal a la DB.
3. Separacion: solo categoria flyer_evento/foto_evento aporta
   datos_evento; material_rd/ficha_sustancia/logo NUNCA generan
   candidato productora/venue. Valores basura (<3 caracteres
   alfanumericos, glitches tipo "e)") se descartan.

    python3 extraccion_db.py FICHAS.jsonl --outdir DIR
        [--catalogo-productoras RUTA] [--catalogo-venues RUTA]

Salidas en --outdir:
- candidatos_db.jsonl: una linea por obra colapsada.
- INFORME_CANDIDATOS.md: resumen ejecutivo ASCII.
- propuestas/*.md: borrador por productora NUEVA con >=2 obras.

Este script NUNCA escribe en data/ ni knowledge/: son solo catalogos de
lectura para el fuzzy-match. stdlib puro; PyYAML es opcional (si no
esta instalado, los catalogos .yaml simplemente se saltean, igual que
PIL es opcional en percepcion.py).
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path, PurePosixPath

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

RATIO_CANONICO = 0.82
RATIO_DUDOSO_MIN = 0.70

CATEGORIAS_CON_EVENTO = ("flyer_evento", "foto_evento")

MIN_ALFANUM_VALIDO = 3
MIN_OBRAS_PROPUESTA = 2

RANK_CALIDAD = {"alta": 3, "media": 2, "baja": 1}

CAMPOS_CANDIDATO_JSONL = (
    "obra_id", "ruta_rel", "miembros_n", "productora_cruda",
    "productora_canonica", "match_ratio", "venue_crudo", "venue_canonico",
    "fecha_cruda", "handles", "categoria", "calidad_senal",
)


# ---------------------------------------------------------------------------
# Normalizacion / basura / ascii
# ---------------------------------------------------------------------------

def normalizar_texto(texto: str) -> str:
    """lower + sin tildes + sin puntuacion, colapsando espacios. Base
    comun para todo fuzzy-match (nunca se compara texto crudo)."""
    if not texto:
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    return texto


def a_ascii(valor) -> str:
    """Fuerza cualquier valor a ASCII puro (repo ASCII-only) para volcar
    en .md/.jsonl de texto libre: quita acentos, descarta lo que quede
    no-ascii. Usar SOLO para texto mostrado en markdown -- candidatos_db
    ya sale ascii-safe via json.dumps(ensure_ascii=True)."""
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    return texto.encode("ascii", "ignore").decode("ascii")


def es_basura(valor: str) -> bool:
    """Descarta valores con menos de MIN_ALFANUM_VALIDO caracteres
    alfanumericos (glitches tipo "e)", strings vacios, solo simbolos)."""
    if not valor:
        return True
    alfanum = sum(1 for c in valor if c.isalnum())
    return alfanum < MIN_ALFANUM_VALIDO


def a_texto(valor) -> str:
    """Normaliza str|list|otro a texto plano (gemma3 devuelve listas a veces)."""
    if isinstance(valor, list):
        valor = "; ".join(str(x).strip() for x in valor if str(x).strip())
    return str(valor or "").strip()


def valor_limpio(valor) -> str:
    """Valor crudo tal cual si no es basura; "" si lo es o esta vacio."""
    valor = a_texto(valor)
    return "" if es_basura(valor) else valor


# ---------------------------------------------------------------------------
# Carga de fichas
# ---------------------------------------------------------------------------

def cargar_fichas(ruta) -> list[dict]:
    """Lee fichas.jsonl, una ficha (dict) por linea. Tolerante: lineas
    vacias/JSON invalido/no-objeto se saltean sin tumbar la carga."""
    fichas: list[dict] = []
    with Path(ruta).open("r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                registro = json.loads(linea)
            except json.JSONDecodeError:
                continue
            if isinstance(registro, dict):
                fichas.append(registro)
    return fichas


def separar_fichas(fichas: list[dict]) -> tuple[list[dict], list[dict]]:
    """(sin_error, con_error). Fichas con error != null se apartan aca
    mismo, antes del colapso: no aportan candidato (regla 3)."""
    con_error = [f for f in fichas if f.get("error")]
    sin_error = [f for f in fichas if not f.get("error")]
    return sin_error, con_error


# ---------------------------------------------------------------------------
# Regla 1: colapso de secuencias
# ---------------------------------------------------------------------------

_RE_SUFIJO_NUM = re.compile(r"^(.*?)(\d+)$")


def clave_secuencia(ficha: dict) -> tuple:
    """Clave de agrupacion: (fuente, directorio, base-sin-sufijo-numerico,
    extension). "0001.png" y "0002.png" en el mismo directorio comparten
    base "" -> misma obra. "flyer_01.png"/"flyer_02.png" comparten base
    "flyer_" -> misma obra. Nombres sin sufijo numerico (base = nombre
    completo) solo colapsan con un homonimo exacto en el mismo dir."""
    ruta_rel = ficha.get("ruta_rel", "") or ""
    p = PurePosixPath(ruta_rel)
    directorio = str(p.parent)
    stem = p.stem
    ext = p.suffix.lower()
    m = _RE_SUFIJO_NUM.match(stem)
    base = m.group(1) if m else stem
    return (ficha.get("fuente", ""), directorio, base, ext)


def _rango_calidad(ficha: dict) -> int:
    return RANK_CALIDAD.get(ficha.get("calidad_senal"), 0)


def colapsar_secuencias(fichas: list[dict]) -> list[dict]:
    """Agrupa `fichas` (ya sin error) por clave_secuencia() en obras.

    Cada obra: {"obra_id", "miembros_n", "representante" (la ficha de
    mejor calidad_senal del grupo), "miembros" (lista completa)}. Orden
    de entrada estable (por ruta_rel) para que el desempate de
    representante sea determinista."""
    fichas_ordenadas = sorted(fichas, key=lambda f: f.get("ruta_rel", "") or "")
    grupos: dict[tuple, list[dict]] = {}
    orden_claves: list[tuple] = []
    for ficha in fichas_ordenadas:
        clave = clave_secuencia(ficha)
        if clave not in grupos:
            grupos[clave] = []
            orden_claves.append(clave)
        grupos[clave].append(ficha)

    obras: list[dict] = []
    for clave in orden_claves:
        miembros = grupos[clave]
        representante = max(miembros, key=_rango_calidad)
        obra_id = "obra_" + hashlib.sha1(
            "|".join(str(c) for c in clave).encode("utf-8")
        ).hexdigest()[:10]
        obras.append({
            "obra_id": obra_id,
            "miembros_n": len(miembros),
            "representante": representante,
            "miembros": miembros,
        })
    return obras


# ---------------------------------------------------------------------------
# Regla 2: catalogos (data/productoras, knowledge/productoras, knowledge/venues)
# ---------------------------------------------------------------------------

def _extraer_entrada(datos: dict) -> tuple[str, list[str]]:
    """De un dict de catalogo (json de data/productoras o yaml de
    knowledge/productoras|venues) extrae (nombre_canonico, variantes)."""
    nombre = (datos.get("name") or "").strip()
    variantes = [nombre] if nombre else []

    for alias in (datos.get("aliases") or []):
        if isinstance(alias, str) and alias.strip():
            variantes.append(alias.strip())

    instagram = datos.get("instagram")
    if isinstance(instagram, str) and instagram.strip():
        variantes.append(instagram.strip())
    elif isinstance(instagram, dict):
        handle = instagram.get("handle")
        if isinstance(handle, str) and handle.strip():
            variantes.append(handle.strip())

    return nombre, variantes


def _cargar_entradas_dir(directorio) -> list[dict]:
    """Lee *.json y *.yaml/*.yml de `directorio` (si existe). Cada
    archivo con "name" no vacio se vuelve una entrada de catalogo
    {"canonico": str, "variantes": [str, ...]}. Tolerante: directorio
    ausente/vacio, PyYAML no instalado, o un archivo puntual invalido
    -- se saltea, nunca tumba la carga."""
    entradas: list[dict] = []
    directorio = Path(directorio) if directorio else None
    if directorio is None or not directorio.is_dir():
        return entradas

    for archivo in sorted(directorio.glob("*.json")):
        try:
            datos = json.loads(archivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(datos, dict):
            continue
        nombre, variantes = _extraer_entrada(datos)
        if nombre and variantes:
            entradas.append({"canonico": nombre, "variantes": variantes})

    if yaml is not None:
        for patron in ("*.yaml", "*.yml"):
            for archivo in sorted(directorio.glob(patron)):
                try:
                    datos = yaml.safe_load(archivo.read_text(encoding="utf-8"))
                except (OSError, yaml.YAMLError):
                    continue
                if not isinstance(datos, dict):
                    continue
                nombre, variantes = _extraer_entrada(datos)
                if nombre and variantes:
                    entradas.append({"canonico": nombre, "variantes": variantes})

    return entradas


def _repo_root() -> Path:
    # cultura/mak_curatoria/extraccion_db.py -> parents[2] == raiz del repo.
    return Path(__file__).resolve().parents[2]


def cargar_catalogo_productoras(ruta_override=None) -> list[dict]:
    """Default: data/productoras/*.json + knowledge/productoras/*.yaml
    (raiz del repo). Con --catalogo-productoras: escanea SOLO ese
    directorio (json+yaml). Sin catalogos -> [] -> todo cae a "nuevo?"."""
    if ruta_override:
        return _cargar_entradas_dir(ruta_override)
    raiz = _repo_root()
    entradas = _cargar_entradas_dir(raiz / "data" / "productoras")
    entradas.extend(_cargar_entradas_dir(raiz / "knowledge" / "productoras"))
    return entradas


def cargar_catalogo_venues(ruta_override=None) -> list[dict]:
    """Default: knowledge/venues/*.yaml (raiz del repo). Con
    --catalogo-venues: escanea SOLO ese directorio (json+yaml)."""
    if ruta_override:
        return _cargar_entradas_dir(ruta_override)
    raiz = _repo_root()
    return _cargar_entradas_dir(raiz / "knowledge" / "venues")


def mejor_match(crudo: str, catalogo: list[dict]) -> tuple:
    """(canonico|None, ratio) del mejor match de `crudo` (normalizado)
    contra las variantes normalizadas del catalogo. (None, 0.0) si
    `crudo` esta vacio o el catalogo esta vacio."""
    crudo_norm = normalizar_texto(crudo)
    if not crudo_norm or not catalogo:
        return None, 0.0

    mejor_canonico = None
    mejor_ratio = 0.0
    for entrada in catalogo:
        for variante in entrada["variantes"]:
            variante_norm = normalizar_texto(variante)
            if not variante_norm:
                continue
            ratio = SequenceMatcher(None, crudo_norm, variante_norm).ratio()
            if ratio > mejor_ratio:
                mejor_ratio = ratio
                mejor_canonico = entrada["canonico"]
    return mejor_canonico, round(mejor_ratio, 3)


def clasificar_ratio(ratio: float) -> str:
    """match (>=0.82) | dudoso (0.70-0.82) | nuevo (<0.70)."""
    if ratio >= RATIO_CANONICO:
        return "match"
    if ratio >= RATIO_DUDOSO_MIN:
        return "dudoso"
    return "nuevo"


# ---------------------------------------------------------------------------
# Regla 3: separacion categoria -> datos_evento, construccion del candidato
# ---------------------------------------------------------------------------

def construir_candidato(obra: dict, catalogo_productoras: list[dict],
                         catalogo_venues: list[dict]) -> dict:
    """Candidato completo (uso interno, incluye venue_match_ratio para
    clasificar venues en el informe -- ese campo NO se escribe en
    candidatos_db.jsonl, ver CAMPOS_CANDIDATO_JSONL)."""
    rep = obra["representante"]
    categoria = rep.get("categoria") or ""
    datos_evento = rep.get("datos_evento") or {}

    if categoria in CATEGORIAS_CON_EVENTO:
        productora_cruda = valor_limpio(datos_evento.get("productora", ""))
        venue_crudo = valor_limpio(datos_evento.get("venue", ""))
        fecha_cruda = a_texto(datos_evento.get("fecha"))
        handles = [
            h.strip() for h in (datos_evento.get("handles") or [])
            if isinstance(h, str) and h.strip()
        ]
    else:
        # material_rd / ficha_sustancia / logo / otro: NUNCA aportan
        # datos_evento, aunque vision haya rellenado algo (regla 3).
        productora_cruda = ""
        venue_crudo = ""
        fecha_cruda = ""
        handles = []

    productora_canonica, ratio_prod = mejor_match(productora_cruda, catalogo_productoras)
    venue_canonico, ratio_venue = mejor_match(venue_crudo, catalogo_venues)

    return {
        "obra_id": obra["obra_id"],
        "ruta_rel": rep.get("ruta_rel", ""),
        "miembros_n": obra["miembros_n"],
        "productora_cruda": productora_cruda,
        "productora_canonica": (
            productora_canonica if clasificar_ratio(ratio_prod) == "match" else None
        ),
        "match_ratio": ratio_prod,
        "venue_crudo": venue_crudo,
        "venue_canonico": (
            venue_canonico if clasificar_ratio(ratio_venue) == "match" else None
        ),
        "venue_match_ratio": ratio_venue,
        "fecha_cruda": fecha_cruda,
        "handles": handles,
        "categoria": categoria,
        "calidad_senal": rep.get("calidad_senal", "") or "",
    }


def candidato_a_jsonl_dict(candidato: dict) -> dict:
    """Subconjunto exacto de campos que va a candidatos_db.jsonl."""
    return {campo: candidato.get(campo) for campo in CAMPOS_CANDIDATO_JSONL}


def escribir_candidatos_jsonl(ruta, candidatos: list[dict]) -> None:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="ascii") as f:
        for candidato in candidatos:
            linea = json.dumps(candidato_a_jsonl_dict(candidato), ensure_ascii=True)
            f.write(linea + "\n")


# ---------------------------------------------------------------------------
# Agrupacion de "nuevo?" entre si (variantes tipo Sundek/sundeck)
# ---------------------------------------------------------------------------

def agrupar_nuevos_por_productora(candidatos_nuevos: list[dict]) -> list[dict]:
    """candidatos_nuevos: candidatos cuya productora_cruda no matcheo
    catalogo (clasificacion "nuevo"). Clustering greedy determinista:
    se procesan ordenados por texto normalizado; cada crudo se suma al
    primer cluster cuyo representante matchea >=RATIO_CANONICO contra
    el, si no arranca cluster propio. Cada cluster: {"variantes": [str,
    ...] (orden de aparicion, con repetidos), "obras": [candidato, ...]}."""
    ordenados = sorted(
        candidatos_nuevos, key=lambda c: normalizar_texto(c["productora_cruda"])
    )
    clusters: list[dict] = []
    for candidato in ordenados:
        crudo = candidato["productora_cruda"]
        crudo_norm = normalizar_texto(crudo)
        destino = None
        for cluster in clusters:
            ratio = SequenceMatcher(None, crudo_norm, cluster["_rep_norm"]).ratio()
            if ratio >= RATIO_CANONICO:
                destino = cluster
                break
        if destino is None:
            destino = {"_rep_norm": crudo_norm, "variantes": [], "obras": []}
            clusters.append(destino)
        destino["variantes"].append(crudo)
        destino["obras"].append(candidato)
    for cluster in clusters:
        del cluster["_rep_norm"]
    return clusters


# ---------------------------------------------------------------------------
# Informe (INFORME_CANDIDATOS.md)
# ---------------------------------------------------------------------------

def _md(valor) -> str:
    return a_ascii(valor)


def _tabla_conteo(titulo: str, conteo: Counter) -> list[str]:
    lineas = ["### %s" % titulo, ""]
    if not conteo:
        lineas.append("(sin datos)")
        lineas.append("")
        return lineas
    lineas.append("| nombre | obras |")
    lineas.append("|---|---:|")
    for nombre, cantidad in sorted(conteo.items(), key=lambda kv: (-kv[1], kv[0] or "")):
        lineas.append("| %s | %d |" % (_md(nombre), cantidad))
    lineas.append("")
    return lineas


def generar_informe(fichas_todas: list[dict], sin_error: list[dict],
                     con_error: list[dict], obras: list[dict],
                     candidatos: list[dict], clusters_nuevos: list[dict]) -> str:
    total_fichas = len(fichas_todas)
    total_sin_error = len(sin_error)
    total_obras = len(obras)
    total_error = len(con_error)

    por_categoria = Counter(c.get("categoria") or "(sin_categoria)" for c in candidatos)

    match_prod: Counter = Counter()
    dudoso_prod: list[dict] = []
    match_venue: Counter = Counter()
    dudoso_venue: list[dict] = []

    for c in candidatos:
        if c["productora_cruda"]:
            cat_prod = clasificar_ratio(c["match_ratio"])
            if cat_prod == "match":
                match_prod[c["productora_canonica"]] += 1
            elif cat_prod == "dudoso":
                dudoso_prod.append(c)
        if c["venue_crudo"]:
            cat_venue = clasificar_ratio(c["venue_match_ratio"])
            if cat_venue == "match":
                match_venue[c["venue_canonico"]] += 1
            elif cat_venue == "dudoso":
                dudoso_venue.append(c)

    lineas = [
        "# Informe de candidatos -- extraccion DB curatoria",
        "",
        "## Totales",
        "",
        "- Fichas totales (fuente rd): %d" % total_fichas,
        "- Fichas con error (apartadas, no aportan): %d" % total_error,
        "- Fichas validas (sin error): %d" % total_sin_error,
        "- Obras tras colapso de secuencias: %d" % total_obras,
        "",
        "## Obras por categoria",
        "",
        "| categoria | obras |",
        "|---|---:|",
    ]
    for categoria, cantidad in sorted(por_categoria.items(), key=lambda kv: (-kv[1], kv[0])):
        lineas.append("| %s | %d |" % (_md(categoria), cantidad))
    lineas.append("")

    lineas.append("## MATCH-CANONICO")
    lineas.append("")
    lineas.extend(_tabla_conteo("Productoras", match_prod))
    lineas.extend(_tabla_conteo("Venues", match_venue))

    lineas.append("## DUDOSOS (ratio 0.70-0.82)")
    lineas.append("")
    lineas.append("### Productoras")
    lineas.append("")
    if dudoso_prod:
        for c in dudoso_prod:
            lineas.append("- %s -> %s (ratio %.2f) [obra %s]" % (
                _md(c["productora_cruda"]), _md(c["productora_canonica"]),
                c["match_ratio"], c["obra_id"]))
    else:
        lineas.append("(sin dudosos)")
    lineas.append("")
    lineas.append("### Venues")
    lineas.append("")
    if dudoso_venue:
        for c in dudoso_venue:
            lineas.append("- %s -> %s (ratio %.2f) [obra %s]" % (
                _md(c["venue_crudo"]), _md(c["venue_canonico"]),
                c["venue_match_ratio"], c["obra_id"]))
    else:
        lineas.append("(sin dudosos)")
    lineas.append("")

    lineas.append("## NUEVO? (productoras candidatas, agrupadas por similitud)")
    lineas.append("")
    if clusters_nuevos:
        for cluster in sorted(clusters_nuevos, key=lambda cl: (-len(cl["obras"]), cl["variantes"][0])):
            variantes_unicas = sorted(set(cluster["variantes"]))
            lineas.append("- %s (obras: %d) -- variantes: %s" % (
                _md(cluster["variantes"][0]), len(cluster["obras"]),
                ", ".join(_md(v) for v in variantes_unicas)))
    else:
        lineas.append("(sin candidatos nuevos)")
    lineas.append("")

    lineas.append("## Fichas con error")
    lineas.append("")
    if con_error:
        for f in con_error:
            lineas.append("- [%s] %s -- %s" % (
                _md(f.get("fuente", "?")), _md(f.get("ruta_rel", "?")),
                _md(f.get("error", "?"))))
    else:
        lineas.append("(sin errores)")
    lineas.append("")

    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Propuestas (propuestas/*.md) -- solo productoras nuevas, >=2 obras
# ---------------------------------------------------------------------------

def _slug(texto: str) -> str:
    norm = normalizar_texto(texto).replace(" ", "_")
    return norm or "sin_nombre"


def escribir_propuestas(dir_propuestas, clusters_nuevos: list[dict]) -> list[Path]:
    """Un .md por cluster de productora NUEVA con >=2 obras. NUNCA
    escribe en data/ ni knowledge/ -- son borradores para PR humano."""
    dir_propuestas = Path(dir_propuestas)
    escritos: list[Path] = []

    for cluster in clusters_nuevos:
        if len(cluster["obras"]) < MIN_OBRAS_PROPUESTA:
            continue

        dir_propuestas.mkdir(parents=True, exist_ok=True)
        nombre = cluster["variantes"][0]
        slug = _slug(nombre)
        variantes_unicas = sorted(set(cluster["variantes"]))

        lineas = [
            "# Propuesta de productora nueva: %s" % _md(nombre),
            "",
            "Variantes vistas: %s" % ", ".join(_md(v) for v in variantes_unicas),
            "",
            "## Obras fuente",
            "",
        ]
        for c in cluster["obras"]:
            handles = ", ".join(c["handles"]) if c["handles"] else "(sin handles)"
            fecha = c["fecha_cruda"] or "(sin fecha)"
            lineas.append("- obra %s -- %s -- fecha: %s -- handles: %s" % (
                c["obra_id"], _md(c["ruta_rel"]), _md(fecha), _md(handles)))
        lineas.append("")
        lineas.append(
            "(Borrador generado por extraccion_db.py -- convertir en entrada de "
            "data/productoras/%s.json via PR humano, NO escribir directo.)" % slug
        )
        lineas.append("")

        ruta = dir_propuestas / ("%s.md" % slug)
        ruta.write_text("\n".join(lineas), encoding="ascii")
        escritos.append(ruta)

    return escritos


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def procesar(ruta_fichas, outdir, catalogo_productoras_ruta=None,
             catalogo_venues_ruta=None) -> dict:
    """Corre el pipeline completo y devuelve un resumen (usado por main()
    y por los tests). Escribe candidatos_db.jsonl, INFORME_CANDIDATOS.md
    y propuestas/*.md en `outdir`."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    fichas = cargar_fichas(ruta_fichas)
    sin_error, con_error = separar_fichas(fichas)

    catalogo_productoras = cargar_catalogo_productoras(catalogo_productoras_ruta)
    catalogo_venues = cargar_catalogo_venues(catalogo_venues_ruta)

    obras = colapsar_secuencias(sin_error)
    candidatos = [
        construir_candidato(obra, catalogo_productoras, catalogo_venues)
        for obra in obras
    ]

    escribir_candidatos_jsonl(outdir / "candidatos_db.jsonl", candidatos)

    nuevo_prod_candidatos = [
        c for c in candidatos
        if c["productora_cruda"] and clasificar_ratio(c["match_ratio"]) == "nuevo"
    ]
    clusters_nuevos = agrupar_nuevos_por_productora(nuevo_prod_candidatos)

    informe = generar_informe(fichas, sin_error, con_error, obras, candidatos, clusters_nuevos)
    (outdir / "INFORME_CANDIDATOS.md").write_text(informe, encoding="ascii")

    propuestas_escritas = escribir_propuestas(outdir / "propuestas", clusters_nuevos)

    return {
        "total_fichas": len(fichas),
        "total_error": len(con_error),
        "total_obras": len(obras),
        "candidatos": candidatos,
        "clusters_nuevos": clusters_nuevos,
        "propuestas": propuestas_escritas,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Fichas de percepcion (curatoria MAK) -> candidatos DB "
                    "(productoras/venues), con colapso de secuencias y fuzzy-match.",
    )
    parser.add_argument("fichas", help="ruta a fichas.jsonl (schema de percepcion.py)")
    parser.add_argument("--outdir", required=True, help="directorio de salida")
    parser.add_argument(
        "--catalogo-productoras", dest="catalogo_productoras", default=None,
        help="directorio con catalogo de productoras (json/yaml); "
             "default data/productoras + knowledge/productoras",
    )
    parser.add_argument(
        "--catalogo-venues", dest="catalogo_venues", default=None,
        help="directorio con catalogo de venues (json/yaml); default knowledge/venues",
    )
    args = parser.parse_args(argv)

    ruta_fichas = Path(args.fichas)
    if not ruta_fichas.is_file():
        print("ERROR: no existe %s" % ruta_fichas, file=sys.stderr)
        return 2

    try:
        resumen = procesar(
            ruta_fichas, args.outdir,
            catalogo_productoras_ruta=args.catalogo_productoras,
            catalogo_venues_ruta=args.catalogo_venues,
        )
    except OSError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    print(
        "candidatos: %d obras (de %d fichas, %d con error apartadas) -- "
        "nuevos agrupados: %d, propuestas escritas: %d -- salida en %s" % (
            resumen["total_obras"], resumen["total_fichas"], resumen["total_error"],
            len(resumen["clusters_nuevos"]), len(resumen["propuestas"]), args.outdir,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
