#!/usr/bin/env python3
"""vigia.py -- the watch department: download, normalize, hash, diff, notify.

WHY IT IS NOT AN LLM (2026-07-30, user's doctrine MEMORIA_DIRECCION 2.3/2.4):
watching a page for new listings is a DIFF problem. download -> normalize ->
hash -> compare against the previous state -> notify only what is new. Zero
tokens, zero GPU, no model anywhere. Every earlier attempt to make a model
"read the page and tell me what changed" burned quota to re-derive something
sha256 already answers exactly.

Built in the style of cultura/mak_lenguaje -- the only department that never
failed: stdlib-only, deterministic, boring.

THE GOLDEN RULE (the line that decides whether this department serves):
a source that suddenly parses to ZERO items, or that goes N days without a
single new item, does NOT get silence. It gets an ERROR notification. Silence
is indistinguishable from "the site changed its HTML and we have been watching
a blank wall for three weeks" -- which is exactly how a watcher dies without
anybody noticing.

State lives in estado/ (gitignored): vistos.jsonl (append-only hashes) and
ultimo.json (per-source conditional-GET validators + counters).
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes.json")
ESTADO_DIR = os.path.join(BASE, "estado")
VISTOS = "vistos.jsonl"
ULTIMO = "ultimo.json"

# Reuse ntfy_publish from research_lib instead of a second implementation.
# Two search paths on purpose: the box runs the mirror at /home/mak/research,
# CI and this machine run the repo copy next door.
for _ruta in ("/home/mak/research",
              os.path.join(os.path.dirname(BASE), "mak_research")):
    if os.path.isdir(_ruta) and _ruta not in sys.path:
        sys.path.append(_ruta)
try:
    from research_lib import ntfy_publish
except ImportError:  # pragma: no cover - the mirror is always present in repo
    ntfy_publish = None

# Whoever moves state signs it. On 2026-07-30, 217 reports were moved into an
# archive/ and NOBODY could attribute it -- the expected outcome of loops,
# crons and SSH sessions sharing a filesystem without a log. Same dual path as
# research_lib: the box runs /home/mak/plataforma, CI runs the repo mirror.
for _ruta in ("/home/mak/plataforma",
              os.path.join(os.path.dirname(BASE), "mak_plataforma")):
    if os.path.isdir(_ruta) and _ruta not in sys.path:
        sys.path.append(_ruta)
try:
    from mutaciones import registrar as registrar_mutacion
except ImportError:  # pragma: no cover - the mirror is always present in repo
    registrar_mutacion = None

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Days without a single new item before the source is declared broken.
DIAS_SIN_NUEVOS = 4
# Flood rule (regla de la avalancha): a source with history whose parse is
# suddenly mostly-new is far more likely to have changed its URL shape than to
# have published half a site of genuine news. Both knobs are per-source
# overridable in fuentes.json (avalancha_minimo / avalancha_fraccion); 0
# disables the rule for that source.
AVALANCHA_MINIMO = 10
AVALANCHA_FRACCION = 0.5
# Retention of the vigia's own memory: vistos.jsonl is append-only and would
# grow forever. Over MAX_VISTOS records, entries older than DIAS_COMPACTAR
# days whose hash is no longer on any watched page MOVE to estado/archive/
# (the repo's retention policy: keep N, archive, never delete).
MAX_VISTOS = 5000
DIAS_COMPACTAR = 90
TIMEOUT = 30
MIN_CHARS_TITULO = 12
MIN_PALABRAS_TITULO = 3
MAX_CHARS_TITULO = 240
# Anchor text that is navigation, not a listing. Folded/lowercased compare.
NAVEGACION = {
    "inicio", "home", "contacto", "contact", "buscar", "search", "login",
    "ingresar", "registrarse", "sign in", "sign up", "menu", "siguiente",
    "anterior", "next", "previous", "leer mas", "read more", "ver mas",
    "ver todo", "more", "cookies", "privacidad", "privacy", "newsletter",
}

_ESPACIOS = re.compile(r"\s+")


def plegar(texto):
    """ASCII fold, lowercase. Only ever applied to MACHINE KEYS (hashes,
    filter matching). The title a human reads keeps its diacritics: see the
    machine/human cut in CLAUDE.md."""
    n = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in n if not unicodedata.combining(c)).lower()


def decodificar(crudo, headers):
    """Bytes -> text, without trusting the declared charset.

    Measured 2026-07-30 against the two real Chilean sources: both declare
    utf-8 and both send cp1252 bytes ("Enfermer\\xeda"). Decoding as declared
    with errors='replace' would turn 'Enfermeria' into a title full of U+FFFD
    -- a mangled diacritic in something a human reads, which this repo treats
    as a defect and not a style. Strict utf-8 first, cp1252 second: the strict
    attempt is what tells the two apart."""
    try:
        return crudo.decode("utf-8")
    except UnicodeDecodeError:
        pass
    declarado = ""
    ct = (headers.get("Content-Type") or "") if headers else ""
    m = re.search(r"charset=([\w-]+)", ct, re.I)
    if m:
        declarado = m.group(1).lower()
    for enc in (declarado, "cp1252", "latin-1"):
        if not enc or enc in ("utf-8", "utf8"):
            continue
        try:
            return crudo.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return crudo.decode("utf-8", "replace")


class ExtractorEnlaces(HTMLParser):
    """Selector-free extraction: a listing page is a list of links.

    No CSS selectors and no per-site rules on purpose -- a selector is a
    promise about someone else's HTML, and it is the first thing to rot. An
    <a href> whose visible text reads like a phrase is an item; navigation
    chrome is dropped by length and by a small stopword set."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self._href = None
        self._buf = []

    def _cerrar(self):
        """Flush the anchor being read, if any."""
        if self._href is None:
            return
        texto = _ESPACIOS.sub(" ", "".join(self._buf)).strip()
        self.items.append({"titulo": texto[:MAX_CHARS_TITULO],
                           "url": self._href})
        self._href = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        # Flush on OPEN, not only on close. HTMLParser does not infer closing
        # tags, so a single unclosed <a> anywhere in the page used to swallow
        # every anchor after it -- measured on resartis.org, where 40 open
        # calls parsed as 0 while the titles were plainly in the HTML. That is
        # exactly the silent-zero the golden rule is about, so the parser must
        # not be the one causing it.
        self._cerrar()
        href = dict(attrs).get("href")
        if href:
            self._href = href
            self._buf = []

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a":
            self._cerrar()

    def close(self):
        super().close()
        self._cerrar()


def _titulo_util(texto):
    if len(texto) < MIN_CHARS_TITULO:
        return False
    if len(texto.split()) < MIN_PALABRAS_TITULO:
        return False
    return plegar(texto) not in NAVEGACION


def extraer_html(texto, base_url):
    p = ExtractorEnlaces()
    try:
        p.feed(texto)
        p.close()
    except Exception:  # noqa: BLE001 - malformed HTML must not kill the run
        pass
    salida, vistos = [], set()
    for it in p.items:
        titulo = it["titulo"]
        if not _titulo_util(titulo):
            continue
        url = urllib.parse.urljoin(base_url, it["url"])
        if url.startswith(("javascript:", "mailto:", "#")):
            continue
        clave = (plegar(titulo), url)
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append({"titulo": titulo, "url": url})
    return salida


def extraer_json(texto, fuente, base_url):
    """Some listings are served as JSON (empleospublicos' typeahead endpoint
    is the real case). Same contract out: titulo + url."""
    try:
        datos = json.loads(texto)
    except ValueError:
        return []
    if isinstance(datos, dict):
        for clave in (fuente.get("json_lista"), "items", "results", "data"):
            if clave and isinstance(datos.get(clave), list):
                datos = datos[clave]
                break
        else:
            datos = [datos]
    if not isinstance(datos, list):
        return []
    campos_t = fuente.get("json_titulo") or ["titulo", "title", "Cargo"]
    campos_u = fuente.get("json_url") or ["url", "URL", "link"]
    salida, vistos = [], set()
    for fila in datos:
        if not isinstance(fila, dict):
            continue
        partes = [str(fila[c]).strip() for c in campos_t
                  if isinstance(fila.get(c), str) and fila.get(c).strip()]
        titulo = _ESPACIOS.sub(" ", " - ".join(partes))[:MAX_CHARS_TITULO]
        if not titulo:
            continue
        url = ""
        for c in campos_u:
            if isinstance(fila.get(c), str) and fila[c].strip():
                url = urllib.parse.urljoin(base_url, fila[c].strip())
                break
        clave = (plegar(titulo), url)
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append({"titulo": titulo, "url": url})
    return salida


def _local(tag):
    """Namespace-free element name: '{http://...Atom}entry' -> 'entry'.
    Feeds ship under half a dozen namespace spellings; the LOCAL name is the
    part that does not rot."""
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def extraer_feed(texto, base_url):
    """RSS 2.0 / Atom, stdlib only. A feed is already a machine listing: every
    <item>/<entry> IS an item by contract, so the HTML heuristics (title
    length, navigation stopwords) do not apply here -- dropping a real entry
    because its title is short would be the parser causing the silent zero the
    golden rule exists to catch. Same contract out: titulo + url."""
    try:
        # Re-encode: ET refuses a str that carries its own encoding
        # declaration ('<?xml version="1.0" encoding="utf-8"?>'), and every
        # real feed carries one. The bytes were already decoded honestly by
        # decodificar(), so utf-8 here is lossless.
        raiz = ET.fromstring(texto.encode("utf-8"))
    except (ET.ParseError, ValueError):
        return []
    salida, vistos = [], set()
    for el in raiz.iter():
        if _local(el.tag) not in ("item", "entry"):
            continue
        titulo, url, url_alterna = "", "", ""
        for hijo in el:
            nombre = _local(hijo.tag)
            if nombre == "title" and not titulo:
                titulo = _ESPACIOS.sub(" ", (hijo.text or "").strip())
                titulo = titulo[:MAX_CHARS_TITULO]
            elif nombre == "link":
                # RSS puts the URL in the text; Atom in href, where
                # rel="alternate" (or no rel) is the human-facing page.
                href = (hijo.get("href") or "").strip()
                rel = (hijo.get("rel") or "alternate").lower()
                if href and rel == "alternate" and not url:
                    url = href
                elif href and not url_alterna:
                    url_alterna = href
                elif not href and hijo.text and hijo.text.strip() and not url:
                    url = hijo.text.strip()
        if not titulo:
            continue
        destino = url or url_alterna
        if destino:
            destino = urllib.parse.urljoin(base_url, destino)
        clave = (plegar(titulo), destino)
        if clave in vistos:
            continue
        vistos.add(clave)
        salida.append({"titulo": titulo, "url": destino})
    return salida


def extraer(texto, fuente, base_url):
    formato = (fuente.get("formato") or "html").lower()
    if formato == "json":
        return extraer_json(texto, fuente, base_url)
    if formato in ("rss", "atom"):
        return extraer_feed(texto, base_url)
    return extraer_html(texto, base_url)


def filtrar(items, palabras, url_contiene=None):
    """Empty filters keep everything. Title matching is accent-insensitive
    because the same listing writes 'Enfermeria' and 'Enfermeria' on different
    days.

    url_contiene is the sharper of the two on real listing pages: a site keeps
    its permalink shape ('/open-call/', '/opportunity/') long after it
    restyles the markup, so it separates listings from site chrome without a
    single CSS selector."""
    salida = list(items)
    if url_contiene:
        patrones = [p for p in url_contiene if p]
        salida = [it for it in salida
                  if any(p in it.get("url", "") for p in patrones)]
    if palabras:
        claves = [plegar(p) for p in palabras if p]
        salida = [it for it in salida
                  if any(k in plegar(it["titulo"]) for k in claves)]
    return salida


def hash_item(fuente_id, item):
    """Stable machine key. Folded title + url: a site that re-cases or
    re-accents its own listing must not resurface it as new."""
    crudo = "%s|%s|%s" % (fuente_id, plegar(item["titulo"]).strip(),
                          item.get("url", ""))
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:16]


def cabeceras_condicionales(estado_fuente):
    """Conditional GET. Cheap for us, polite to them, and the 304 path is what
    keeps an hourly cron from looking like a scraper."""
    h = {"User-Agent": UA, "Accept-Language": "es-CL,es;q=0.9,en;q=0.8"}
    if estado_fuente.get("etag"):
        h["If-None-Match"] = estado_fuente["etag"]
    if estado_fuente.get("last_modified"):
        h["If-Modified-Since"] = estado_fuente["last_modified"]
    return h


def descargar(url, estado_fuente, abrir=None):
    """-> (codigo, texto, headers). 304 gives (304, "", headers)."""
    abrir = abrir or urllib.request.urlopen
    req = urllib.request.Request(
        url, headers=cabeceras_condicionales(estado_fuente))
    try:
        resp = abrir(req, timeout=TIMEOUT)
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return 304, "", getattr(e, "headers", {}) or {}
        raise
    with resp:
        headers = resp.headers
        return getattr(resp, "status", 200) or 200, \
            decodificar(resp.read(), headers), headers


# ---------------------------------------------------------------- estado

def _p(estado_dir, nombre):
    return os.path.join(estado_dir, nombre)


def cargar_vistos(estado_dir):
    vistos = set()
    try:
        with open(_p(estado_dir, VISTOS), encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    vistos.add(json.loads(linea)["h"])
                except (ValueError, KeyError):
                    continue
    except OSError:
        pass
    return vistos


def anotar_vistos(estado_dir, registros):
    os.makedirs(estado_dir, exist_ok=True)
    with open(_p(estado_dir, VISTOS), "a", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def cargar_ultimo(estado_dir):
    try:
        with open(_p(estado_dir, ULTIMO), encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def guardar_ultimo(estado_dir, datos):
    os.makedirs(estado_dir, exist_ok=True)
    tmp = _p(estado_dir, ULTIMO) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, _p(estado_dir, ULTIMO))


def hashes_vigentes(ultimo):
    """Union of every source's last full parse: the hashes the diff still
    NEEDS. Anything outside this set and older than the cutoff is memory of
    listings that already left the pages."""
    v = set()
    for est in (ultimo or {}).values():
        if isinstance(est, dict):
            v.update(h for h in est.get("hashes") or []
                     if isinstance(h, str))
    return v


def compactar_vistos(estado_dir, ahora=None, ultimo=None,
                     dias=DIAS_COMPACTAR, max_registros=MAX_VISTOS):
    """Retention of the vigia's own memory: keep what the diff still needs,
    MOVE the rest to estado/archive/, never delete -- the same policy
    retencion.py decided for the research reports (keep N, archive/, no rm).

    A record is archived only when it is older than `dias` AND its hash is no
    longer on any watched page, so an archived hash cannot resurface by
    itself. If a site re-lists an archived item months later, that re-listing
    notifies again -- accepted on purpose: a call that reopens IS news.

    Order of writes is crash-safe by construction: the archive copy lands
    first, the trimmed vistos.jsonl replaces the old one after (os.replace,
    atomic). A crash in between leaves a duplicate, never a loss.

    Whoever moves state signs it (mutaciones.registrar): on 2026-07-30, 217
    files moved into an archive/ and nobody could say who did it. The action
    was right; the silence was not.

    Returns a summary dict; {"archivados": 0} means nothing moved."""
    ahora = time.time() if ahora is None else ahora
    ruta = _p(estado_dir, VISTOS)
    try:
        with open(ruta, encoding="utf-8") as f:
            lineas = [ln.rstrip("\n") for ln in f if ln.strip()]
    except OSError:
        return {"total": 0, "archivados": 0, "quedan": 0, "archivo": ""}
    resumen = {"total": len(lineas), "archivados": 0,
               "quedan": len(lineas), "archivo": ""}
    if len(lineas) <= max_registros:
        return resumen

    ultimo = cargar_ultimo(estado_dir) if ultimo is None else ultimo
    vigentes = hashes_vigentes(ultimo)
    corte = ahora - dias * 86400.0
    mantener, archivar = [], []
    for linea in lineas:
        try:
            reg = json.loads(linea)
        except ValueError:
            # A malformed line is somebody's data we cannot date: it stays.
            mantener.append(linea)
            continue
        ts = reg.get("ts")
        es_viejo = isinstance(ts, (int, float)) and float(ts) < corte
        if es_viejo and reg.get("h") not in vigentes:
            archivar.append(linea)
        else:
            mantener.append(linea)
    if not archivar:
        return resumen

    arch_dir = os.path.join(estado_dir, "archive")
    os.makedirs(arch_dir, exist_ok=True)
    destino = os.path.join(
        arch_dir, "vistos_%s.jsonl" % time.strftime("%Y%m%d",
                                                    time.gmtime(ahora)))
    with open(destino, "a", encoding="utf-8") as f:
        for linea in archivar:
            f.write(linea + "\n")
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for linea in mantener:
            f.write(linea + "\n")
    os.replace(tmp, ruta)

    if registrar_mutacion is not None:
        try:
            registrar_mutacion(
                "vigia_compactar",
                "%d registros -> %s (quedan %d, dias=%d)"
                % (len(archivar), destino, len(mantener), dias),
                origen=__file__)
        except Exception:  # noqa: BLE001 - signing must never break the move
            pass
    resumen.update(archivados=len(archivar), quedan=len(mantener),
                   archivo=destino)
    return resumen


# ------------------------------------------------------------ regla de oro

def regla_de_oro(previo, n_items, n_nuevos, ahora, dias=DIAS_SIN_NUEVOS):
    """The line that decides whether this department serves.

    Returns an error string, or "" when the source looks healthy.

    Two ways a watcher dies quietly, and both must SCREAM:
      a) the page still answers 200 but now parses to ZERO items where it used
         to parse many -- the markup changed under us and we are watching a
         blank wall;
      b) no new item for `dias` days -- either the listing froze or our filter
         stopped matching. Both are worth a human look.
    """
    antes = int(previo.get("n_items") or 0)
    if n_items == 0 and antes > 0:
        return ("parsea 0 items y antes daba %d: el HTML cambio o la fuente "
                "murio" % antes)
    if n_nuevos > 0 or n_items == 0:
        return ""
    ultimo_nuevo = previo.get("ultimo_nuevo_ts")
    if ultimo_nuevo is None:
        # No clock started yet: we do not know how long the silence has been.
        # `is None` and not a truth test -- a timestamp of 0.0 is falsy, and
        # treating it as "never" is how a stale source stays quiet forever.
        return ""
    transcurridos = (ahora - float(ultimo_nuevo)) / 86400.0
    if transcurridos >= dias:
        return ("sin ningun item nuevo en %.1f dias (umbral %d): revisar el "
                "filtro o la fuente" % (transcurridos, dias))
    return ""


def regla_de_avalancha(previo, n_items, n_nuevos, minimo=AVALANCHA_MINIMO,
                       fraccion=AVALANCHA_FRACCION):
    """The flood side of the golden rule. Silence is one way a watcher lies;
    a flood is the other: when a site changes its permalink shape, every item
    re-hashes and the diff reports the WHOLE page as new. 299 'new' items on
    two phones is spam that drowns real news and teaches everyone to ignore
    the topic -- the same defect the golden rule exists for, mirrored.

    Returns an alert string when a source WITH HISTORY parses mostly-new
    (>= minimo items and >= fraccion of the parse), else "". The first run of
    a source has no history and is legitimately all-new: never a flood.

    The caller suppresses per-item notification for a flooded source but still
    RECORDS the hashes, so after the one alert the following runs are quiet.
    """
    if minimo <= 0 or fraccion <= 0:
        return ""
    if int(previo.get("n_items") or 0) <= 0:
        return ""
    if n_items <= 0 or n_nuevos < minimo:
        return ""
    if n_nuevos / float(n_items) < fraccion:
        return ""
    return ("%d de %d ítems aparecen nuevos de golpe (umbral %d y %d%%): "
            "probable cambio en la forma de las URLs; quedan registrados "
            "sin notificar uno a uno"
            % (n_nuevos, n_items, minimo, int(fraccion * 100)))


# ------------------------------------------------------------------ corrida

def cargar_fuentes(path=FUENTES):
    with open(path, encoding="utf-8") as f:
        datos = json.load(f)
    fuentes = datos.get("fuentes", datos) if isinstance(datos, dict) else datos
    return [f for f in fuentes if f.get("activa", True)]


def revisar_fuente(fuente, previo, vistos, ahora, abrir=None, dias=DIAS_SIN_NUEVOS):
    """One source, one dict out. Never raises: a source that fails must not
    take the other ones down with it (measured everywhere else in this repo --
    one 403 killing a whole run is how a watch stops silently)."""
    fid = fuente["id"]
    res = {"id": fid, "nombre": fuente.get("nombre", fid),
           "tipo": fuente.get("tipo", "general"), "codigo": 0,
           "n_items": 0, "nuevos": [], "error": "", "alerta": ""}
    try:
        codigo, texto, headers = descargar(fuente["url"], previo, abrir=abrir)
    except Exception as e:  # noqa: BLE001 - reported, never fatal
        res["error"] = "%s: %s" % (type(e).__name__, e)
        res["estado"] = dict(previo, ultima_corrida_ts=ahora,
                             ultimo_error=res["error"])
        return res

    res["codigo"] = codigo
    nuevo_estado = dict(previo)
    nuevo_estado["ultima_corrida_ts"] = ahora
    nuevo_estado.pop("ultimo_error", None)

    if codigo == 304:
        # Not modified: nothing new by definition, and NOT a golden-rule
        # failure -- the server just told us the page is unchanged.
        res["n_items"] = int(previo.get("n_items") or 0)
        res["estado"] = nuevo_estado
        return res

    etag = headers.get("ETag") if headers else None
    lm = headers.get("Last-Modified") if headers else None
    if etag:
        nuevo_estado["etag"] = etag
    if lm:
        nuevo_estado["last_modified"] = lm

    items = filtrar(extraer(texto, fuente, fuente["url"]),
                    fuente.get("palabras_filtro"),
                    fuente.get("url_contiene"))
    res["n_items"] = len(items)
    nuevos = []
    for it in items:
        h = hash_item(fid, it)
        if h in vistos:
            continue
        vistos.add(h)
        nuevos.append({"h": h, "fuente": fid, "titulo": it["titulo"],
                       "url": it.get("url", ""), "ts": int(ahora)})
    res["nuevos"] = nuevos
    if items:
        # The full current parse, hashed. This is what compaction consults so
        # a hash still visible on the page is NEVER archived (it would
        # resurface as "new"). On a zero parse the previous set is kept: the
        # golden rule already screams there, and archiving the page's real
        # hashes during a breakage would double-notify after the fix.
        nuevo_estado["hashes"] = [hash_item(fid, it) for it in items]
    oro = regla_de_oro(previo, len(items), len(nuevos), ahora, dias)
    avalancha = "" if oro else regla_de_avalancha(
        previo, len(items), len(nuevos),
        minimo=fuente.get("avalancha_minimo", AVALANCHA_MINIMO),
        fraccion=fuente.get("avalancha_fraccion", AVALANCHA_FRACCION))
    if avalancha:
        # One high-priority alert instead of a page of per-item lines. The
        # hashes are still recorded by the caller, so the flood alerts once
        # and the runs after it are quiet.
        res["suprimido"] = len(nuevos)
    res["alerta"] = oro or avalancha
    nuevo_estado["n_items"] = len(items)
    if nuevos:
        nuevo_estado["ultimo_nuevo_ts"] = ahora
    elif not previo.get("ultimo_nuevo_ts") and items:
        # First healthy run with nothing new to us yet: start the clock, or
        # rule (b) can never fire.
        nuevo_estado["ultimo_nuevo_ts"] = ahora
    res["estado"] = nuevo_estado
    return res


def _mensaje(resultados, cabeza):
    lineas = []
    for r in resultados:
        if r.get("suprimido"):
            # Flooded source: its alert already tells the story; listing the
            # items one by one is the spam the flood rule exists to stop.
            continue
        if r["nuevos"]:
            lineas.append("* %s (%d):" % (r["nombre"], len(r["nuevos"])))
            for n in r["nuevos"][:12]:
                lineas.append("  - %s" % n["titulo"])
                if n["url"]:
                    lineas.append("    %s" % n["url"])
            if len(r["nuevos"]) > 12:
                lineas.append("  ... y %d mas" % (len(r["nuevos"]) - 12))
    return cabeza + "\n" + "\n".join(lineas) if lineas else ""


def _mensaje_alerta(resultados):
    lineas = []
    for r in resultados:
        if r["alerta"]:
            lineas.append("! %s: %s" % (r["nombre"], r["alerta"]))
        elif r["error"]:
            lineas.append("? %s: no se pudo leer -- %s" % (r["nombre"],
                                                           r["error"]))
    return "\n".join(lineas)


def correr(fuentes=None, estado_dir=ESTADO_DIR, abrir=None, notificar=True,
           ahora=None, dias=DIAS_SIN_NUEVOS, max_vistos=MAX_VISTOS):
    ahora = time.time() if ahora is None else ahora
    fuentes = cargar_fuentes() if fuentes is None else fuentes
    ultimo = cargar_ultimo(estado_dir)
    vistos = cargar_vistos(estado_dir)

    resultados = []
    for fuente in fuentes:
        r = revisar_fuente(fuente, ultimo.get(fuente["id"], {}), vistos,
                           ahora, abrir=abrir, dias=dias)
        ultimo[fuente["id"]] = r.pop("estado")
        resultados.append(r)

    registros = [n for r in resultados for n in r["nuevos"]]
    if registros:
        anotar_vistos(estado_dir, registros)
    guardar_ultimo(estado_dir, ultimo)

    # Housekeeping INSIDE the existing hourly run -- not a new loop, not a new
    # cron. It only acts when the file crosses the cap, and it signs the move.
    if max_vistos is not None:
        compactar_vistos(estado_dir, ahora=ahora, ultimo=ultimo,
                         max_registros=max_vistos)

    if notificar:
        _notificar(resultados)
    return resultados


def _cargar_contexto_artista():
    ruta = os.environ.get("MAK_ARTIST_CONTEXT", "")
    if not ruta:
        ruta = os.path.expanduser("~/plataforma/artist_context.json")
    try:
        with open(ruta, encoding="utf-8") as fh:
            datos = json.load(fh)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def priorizar_oportunidades(items, contexto=None):
    """Order listings by artist fit without claiming eligibility or truth."""
    contexto = contexto or {}
    direction = contexto.get("direction", {})
    desired_terms = [plegar(str(value)) for value in
                     direction.get("opportunities", []) if str(value).strip()]
    ranked = []
    for index, item in enumerate(items):
        title = str(item.get("titulo") or "")
        source = plegar(str(item.get("fuente") or ""))
        text = plegar(title + " " + source)
        nursing_lane = any(word in text for word in (
            "enfermer", "tens", "hospital", "salud", "residencia familiar"))
        score = 0
        reasons = []
        practice_words = (
                "fondart", "fondo de cultura", "fondos de cultura",
                "res artis", "open call", "convocatoria", "artist", "artista",
                "beca")
        if (any(word in text for word in practice_words) or
                (not nursing_lane and any(word in text for word in
                                          ("residencia", "residencias")))):
            score += 5
            reasons.append("practice_or_funding")
        if any(word in text for word in ("musica", "music", "lanzamiento",
                                         "diseno", "design", "comision")):
            score += 3
            reasons.append("design_or_music")
        if nursing_lane:
            reasons.append("private_nursing_lane")
            if "residencia familiar" in text:
                score += 1
        desired_hits = [term for term in desired_terms if term and term in text]
        if desired_hits:
            score += 2
            reasons.append("artist_context:%s" % ",".join(desired_hits[:2]))
        if str(item.get("url") or "").startswith(("http://", "https://")):
            score += 1
            reasons.append("has_source_url")
        ranked.append((score, index, dict(item), reasons))
    ranked.sort(key=lambda value: (-value[0], value[1]))
    output = []
    for score, _, item, reasons in ranked:
        item["priority_score"] = score
        item["priority_reasons"] = reasons or ["needs_manual_fit"]
        output.append(item)
    return output


def encolar_oportunidades(resultados, ledger_path, max_per_source=8,
                          contexto=None):
    """Send ranked listings to the shared review queue, never to an LLM."""
    for ruta in ("/home/mak/plataforma",
                 os.path.join(os.path.dirname(BASE), "mak_plataforma")):
        if os.path.isdir(ruta) and ruta not in sys.path:
            sys.path.insert(0, ruta)
    try:
        from ledger import opportunity_from_vigia
    except Exception as exc:  # noqa: BLE001 - watcher must remain observable
        return {"queued": 0, "duplicates": 0,
                "errors": ["ledger_unavailable:%s" % type(exc).__name__]}
    queued = duplicates = deferred = 0
    queued_by_source = {}
    errors = []
    contexto = _cargar_contexto_artista() if contexto is None else contexto
    for resultado in resultados:
        source_items = priorizar_oportunidades(
            [dict(item, fuente=resultado.get("id", ""))
             for item in resultado.get("nuevos", [])], contexto)
        for item in source_items:
            source_id = str(resultado.get("id", ""))
            if queued_by_source.get(source_id, 0) >= max(1, int(max_per_source)):
                deferred += 1
                continue
            ok, item_errors, row = opportunity_from_vigia(
                item, source="vigia:%s" % resultado.get("id", ""),
                path=ledger_path)
            if not ok:
                errors.extend(item_errors)
            elif row is None:
                duplicates += 1
            else:
                queued += 1
                queued_by_source[source_id] = queued_by_source.get(source_id, 0) + 1
    return {"queued": queued, "duplicates": duplicates, "deferred": deferred,
            "errors": errors}


def _notificar(resultados):
    """Batched per run, never per item: this lands on two phones and the
    budget is a few notifications a day, not one per listing."""
    if ntfy_publish is None:
        return
    enfermeria = [r for r in resultados if r["tipo"] == "enfermeria"]
    resto = [r for r in resultados if r["tipo"] != "enfermeria"]
    destinos = [
        (os.environ.get("VIGIA_NTFY_TOPIC_ENFERMERIA", ""), enfermeria,
         "Vigia: enfermeria"),
        (os.environ.get("VIGIA_NTFY_TOPIC", ""), resto, "Vigia"),
    ]
    for topic, grupo, cabeza in destinos:
        if not topic or not grupo:
            continue
        cuerpo = _mensaje(grupo, cabeza)
        if cuerpo:
            ntfy_publish(topic, cuerpo, title=cabeza)
        alerta = _mensaje_alerta(grupo)
        if alerta:
            # The golden rule is louder than the results on purpose.
            ntfy_publish(topic, alerta, title=cabeza + " ROTO",
                         priority="high")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--estado", default=ESTADO_DIR)
    ap.add_argument("--fuentes", default=FUENTES)
    ap.add_argument("--dias", type=int, default=DIAS_SIN_NUEVOS,
                    help="dias sin items nuevos antes de declarar la fuente rota")
    ap.add_argument("--sin-notificar", action="store_true")
    ap.add_argument("--solo", default="", help="id de una fuente")
    ap.add_argument("--ledger-oportunidades", default="",
                    help="shared ledger path for new human-review opportunities")
    ap.add_argument("--max-oportunidades-fuente", type=int, default=8,
                    help="maximo de nuevas oportunidades por fuente y corrida")
    ap.add_argument("--max-vistos", type=int, default=MAX_VISTOS,
                    help="registros en vistos.jsonl antes de compactar")
    ap.add_argument("--compactar", action="store_true",
                    help="compacta el estado ahora (sin revisar fuentes) y sale")
    args = ap.parse_args(argv)

    if args.compactar:
        c = compactar_vistos(args.estado, max_registros=0)
        print("compactado: %d de %d registros -> %s (quedan %d)"
              % (c["archivados"], c["total"], c["archivo"] or "-",
                 c["quedan"]))
        return 0

    fuentes = cargar_fuentes(args.fuentes)
    if args.solo:
        fuentes = [f for f in fuentes if f["id"] == args.solo]
    res = correr(fuentes=fuentes, estado_dir=args.estado,
                 notificar=not args.sin_notificar, dias=args.dias,
                 max_vistos=args.max_vistos)
    roto = 0
    for r in res:
        marca = "!" if (r["alerta"] or r["error"]) else " "
        roto += 1 if (r["alerta"] or r["error"]) else 0
        print("%s %-28s http=%-3s items=%-4d nuevos=%-3d %s"
              % (marca, r["id"], r["codigo"], r["n_items"], len(r["nuevos"]),
                 r["alerta"] or r["error"]))
    if args.ledger_oportunidades:
        print(json.dumps(encolar_oportunidades(
            res, args.ledger_oportunidades,
            max_per_source=args.max_oportunidades_fuente), ensure_ascii=False))
    return 1 if roto else 0


if __name__ == "__main__":
    sys.exit(main())
