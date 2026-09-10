#!/usr/bin/env python3
"""Convierte los flyers de RD ya percibidos en preguntas de investigacion.

La formula es del usuario (2026-07-26): "si tienes headliner y tienes fecha =
tienes productora potencialmente encontrable por research". Ese paso nunca se
construyo: desde el 2026-07-23 hay 132 flyers con fecha y productora/handle
esperando en ~/curatoria/fichas/fichas.jsonl, y nadie los mando a research.

Esto NO investiga: arma la cola. Cada flyer con datos suficientes y productora
DESCONOCIDA se convierte en una pregunta concreta y verificable. Los que ya
traen productora se listan aparte como confirmables.

Salida: ~/curatoria/triangulacion.jsonl (una linea por pregunta) y un resumen
por pantalla. Nada se despacha solo; el despacho es una decision aparte.

Nota sobre el material viejo: las fichas del 2026-07-23 se hicieron con el
prompt unico, que NUNCA pedia headliners. Por eso aca el headliner se busca en
el texto OCR. Cuando el corpus se vuelva a percibir con PROMPT_RD -- que si los
pide -- esta cola va a ser mucho mas rica.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

FICHAS = os.path.expanduser("~/curatoria/fichas/fichas.jsonl")
SALIDA = os.path.expanduser("~/curatoria/triangulacion.jsonl")
DISPATCH_RESULTS_PATH = os.path.expanduser("~/curatoria/triangulacion_resultado.jsonl")

# Dominio de fuentes.py hecho a medida para esto mismo (ver
# cultura/mak_research/fuentes.py:152-156): "quien organizo, donde y cuando"
# en Chile, con Instagram/ticketeras/venues conocidos como primaria y medios
# genericos como secundaria.
SOURCE_DOMAIN = "cl_eventos"

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _sub in ("mak_research", "mak_curatoria"):
    _p = str(_REPO_ROOT / "cultura" / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

_RESEARCH_LIB = None
_SOURCE_GATE = None
_CATALOG_DB = None


def _research_lib_module():
    """cultura/mak_research/research_lib.py: busqueda web real (SearXNG ->
    Firecrawl -> Tavily, ver web_search()). None si no esta disponible --
    degrada al mismo aviso que cualquier otra dependencia opcional de este
    repo: la cola se arma igual, el despacho real simplemente no corre."""
    global _RESEARCH_LIB
    if _RESEARCH_LIB is None:
        try:
            import research_lib
            _RESEARCH_LIB = research_lib
        except ImportError:
            _RESEARCH_LIB = False
    return _RESEARCH_LIB or None


def _source_gate_module():
    """cultura/mak_research/fuentes.py: clasificador de fuentes primarias
    por dominio. Ya lo usa src/flujo/rd/database.py para productora_eventos
    (ver _event_source_gate) -- misma pieza, no una nueva."""
    global _SOURCE_GATE
    if _SOURCE_GATE is None:
        try:
            import fuentes
            _SOURCE_GATE = fuentes
        except ImportError:
            _SOURCE_GATE = False
    return _SOURCE_GATE or None


def _catalog_db_module():
    """cultura/mak_curatoria/extraccion_db.py: mismo catalogo (data/rd.db)
    y mismo fuzzy-match (mejor_match/clasificar_ratio) que usa el pipeline
    OCR->propuestas, para que un nombre encontrado por busqueda real se
    juzgue con la misma vara que uno leido de un flyer."""
    global _CATALOG_DB
    if _CATALOG_DB is None:
        try:
            import extraccion_db
            _CATALOG_DB = extraccion_db
        except ImportError:
            _CATALOG_DB = False
    return _CATALOG_DB or None

# Palabras que aparecen en flyers y no son nombres de artista.
RUIDO = {
    "presenta", "presents", "open", "air", "club", "party", "fiesta", "tickets",
    "entradas", "puerta", "lineup", "line", "up", "dj", "live", "set", "show",
    "reduciendo", "dano", "daño", "instagram", "www", "com", "cl", "hrs", "hs",
}


def posibles_headliners(texto):
    """Nombres candidatos del cartel, desde OCR y NER opcional.

    La ruta heuristica sigue siendo la base determinista. Azure Language solo
    agrega candidatos cuando sus credenciales estan presentes; el resultado
    nunca se trata como una confirmacion y la cola conserva la procedencia en
    ``headliners_fuentes``.
    """
    return _headliner_evidence(texto)["candidatos"]


def _heuristic_headliners(texto):
    """Candidatos que pueden obtenerse sin red ni credenciales."""
    if not texto:
        return []
    cands = []
    for linea in texto.splitlines():
        s = linea.strip()
        if not (3 <= len(s) <= 40):
            continue
        palabras = [p for p in re.split(r"[^\wÁÉÍÓÚÑáéíóúñ]+", s) if p]
        if not (1 <= len(palabras) <= 4):
            continue
        if any(p.lower() in RUIDO for p in palabras):
            continue
        if not any(c.isalpha() for c in s):
            continue
        # Un nombre de cartel suele ir en mayusculas o Capitalizado.
        if s.isupper() or all(p[:1].isupper() for p in palabras if p[:1].isalpha()):
            cands.append(s)
    vistos, salida = set(), []
    for c in cands:
        k = c.lower()
        if k not in vistos:
            vistos.add(k)
            salida.append(c)
    return salida[:5]


def _azure_language_ner(texto):
    """Read-only optional enrichment through Azure Language EntityRecognition.

    The integration uses the unified REST endpoint and the standard-library
    HTTP client so the offline curatoria path has no new mandatory dependency.
    Missing configuration, network failures and malformed responses degrade to
    an empty candidate list; they never erase the deterministic OCR result.
    """
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT", "").strip().rstrip("/")
    key = os.environ.get("AZURE_LANGUAGE_KEY", "").strip()
    if not endpoint or not key:
        return {"status": "not_configured", "candidates": []}
    if os.environ.get("MAK_AZURE_LANGUAGE_NER", "1").strip().lower() in {
        "0", "false", "no", "off",
    }:
        return {"status": "disabled", "candidates": []}
    if not texto or not str(texto).strip():
        return {"status": "empty_input", "candidates": []}

    # Some deployments expose the full route in the endpoint variable. Accept
    # both forms so the value copied from Azure does not need manual editing.
    if endpoint.endswith("/language/:analyze-text"):
        url_base = endpoint
    else:
        url_base = endpoint + "/language/:analyze-text"
    api_version = os.environ.get("AZURE_LANGUAGE_API_VERSION", "2026-05-01").strip()
    url = "%s?%s" % (url_base, urllib.parse.urlencode({"api-version": api_version}))
    body = {
        "kind": "EntityRecognition",
        "parameters": {
            "modelVersion": "latest",
            "overlapPolicy": {"policyKind": "matchLongest"},
        },
        "analysisInput": {
            "documents": [{"id": "ocr-1", "language": "es", "text": str(texto)[:5000]}],
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": key,
        },
        method="POST",
    )
    timeout = float(os.environ.get("AZURE_LANGUAGE_TIMEOUT", "8"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"status": "http_error", "code": int(exc.code), "candidates": []}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, TypeError):
        return {"status": "request_error", "candidates": []}

    documents = ((payload.get("results") or {}).get("documents") or [])
    entities = documents[0].get("entities") if documents else []
    candidates = []
    for entity in entities or []:
        if not isinstance(entity, dict):
            continue
        try:
            score = float(entity.get("confidenceScore", 0))
        except (TypeError, ValueError):
            score = 0
        category = str(entity.get("category") or "")
        text_value = str(entity.get("text") or "").strip()
        # Person and Organization are useful for artists and collectives. A
        # Product can be a stage name, but it is admitted only at a higher
        # confidence so generic flyer words do not flood the queue.
        threshold = 0.65 if category.lower() == "product" else 0.5
        if category.lower() not in {"person", "organization", "product"}:
            continue
        words = [word.lower() for word in re.findall(r"[\wÁÉÍÓÚÑáéíóúñ]+", text_value)]
        if (
            score < threshold
            or not (3 <= len(text_value) <= 40)
            or len(words) > 4
            or any(word in RUIDO for word in words)
            or not _candidato_legible(text_value)
        ):
            continue
        candidates.append(text_value)
    return {"status": "ok", "candidates": candidates[:10]}


def _headliner_evidence(texto):
    heuristic = _heuristic_headliners(texto)
    azure = _azure_language_ner(texto)
    candidates = []
    sources = []
    for value in heuristic:
        if value.lower() not in {item.lower() for item in candidates}:
            candidates.append(value)
    if heuristic:
        sources.append({"kind": "ocr_heuristic", "status": "observed"})
    for value in azure.get("candidates", []):
        if value.lower() not in {item.lower() for item in candidates}:
            candidates.append(value)
    if azure.get("status") == "ok" and azure.get("candidates"):
        sources.append({"kind": "azure_language_ner", "status": "candidate"})
    return {"candidatos": candidates[:5], "fuentes": sources, "azure": azure.get("status")}



def _txt(v):
    """El modelo a veces devuelve lista donde el schema pide string."""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v if x).strip()
    return str(v or "").strip()


# Venues/ciudades demasiado genericos como para ser una pista real: harian
# que toda fila "descubrir" sin venue especifico pareciera tener señal.
_VENUE_GENERICO = {"chile", "santiago", "santiago de chile", "region metropolitana"}


def _candidato_legible(s: str) -> bool:
    """True si `s` parece un nombre real, no un fragmento de OCR roto.

    Probado contra la cola real: "NES", "¡ S" y "7 So 1]" (fragmentos
    reales en ~/curatoria/triangulacion.jsonl) pasaban un chequeo de "3+
    letras seguidas" -- "NES" son exactamente 3 letras consecutivas.
    Exige una racha de 4+ letras Y que la mayoria de los caracteres no
    sean espacios/puntuacion/mojibake."""
    palabras = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{4,}", s or "")
    if not palabras:
        return False
    compacto = re.sub(r"\s+", "", s or "")
    letras = sum(1 for c in compacto if c.isalpha())
    return letras >= max(4, round(0.6 * len(compacto)))


def _senal_suficiente(row: dict) -> bool:
    """True si la fila tiene algo real para buscar (no solo la fecha).
    Con 200 preguntas reales en cola, buena parte trae basura de OCR --
    fragmentos de headliner, venue igual al pais -- y gastar una busqueda
    real en eso es puro ruido contra el buscador."""
    venue = (row.get("venue") or "").strip()
    if venue.lower() in _VENUE_GENERICO:
        venue = ""
    heads = [h for h in (row.get("headliners_candidatos") or [])
             if _candidato_legible(h)]
    prod = (row.get("productora_declarada") or "").strip()
    return bool(prod or venue or heads)


def _query_de(row: dict) -> str:
    """Query desde los campos ESTRUCTURADOS, no desde 'pregunta': pregunta
    ya trae prosa ('Responder con fuente') que solo le resta señal al
    buscador."""
    venue = (row.get("venue") or "").strip()
    if venue.lower() in _VENUE_GENERICO:
        venue = ""
    partes = [p for p in (
        row.get("productora_declarada"),
        "productora evento",
        (row.get("headliners_candidatos") or [None])[0],
        venue,
        row.get("fecha"),
    ) if p]
    return " ".join(str(p).strip() for p in partes if str(p).strip())


def _nombres_conocidos(catalogo: list[dict]) -> list[tuple[str, str]]:
    """(variante normalizada, canonico) por cada variante de cada
    productora ya conocida en data/rd.db -- para reconocer su aparicion
    literal en el texto de los resultados de busqueda."""
    edb = _catalog_db_module()
    pares = []
    for entry in catalogo:
        for variante in entry.get("variantes") or []:
            norm = edb.normalizar_texto(variante)
            if len(norm) >= 3:
                pares.append((norm, entry["canonico"]))
    return pares


def _known_names_in_text(texto: str, nombres_conocidos: list[tuple[str, str]]) -> set[str]:
    """Canonicos de data/rd.db cuya variante aparece como PALABRA(S) enteras
    en `texto` (con margen de espacios en ambos lados para no matchear
    'dam4' dentro de otra palabra mas larga)."""
    edb = _catalog_db_module()
    t = " " + edb.normalizar_texto(texto) + " "
    return {canonico for variante, canonico in nombres_conocidos
            if (" " + variante + " ") in t}


def despachar(filas: list[dict], catalogo: list[dict], limite: int | None = None) -> list[dict]:
    """El paso que el docstring del modulo llama "una decision aparte":
    busqueda real por fila + cruce contra data/rd.db (mismo catalogo y
    mismo fuzzy-match que el pipeline OCR) + fuentes.evaluar() (mismo gate
    de fuentes primarias que ya usa productora_eventos) para el nivel de
    confianza. Nunca escribe a data/rd.db ni a productora_eventos: cada
    fila queda con `despacho.revision_humana = "pendiente"`, el mismo
    principio de "nada se despacha solo" que el resto del pipeline RD.

    "Fuentes independientes" se mide como dominios DISTINTOS entre las
    fuentes primarias que respaldan un mismo candidato -- una sola pagina
    nunca alcanza para "confirmado", sin importar cuan bien matchee el
    nombre contra el catalogo.
    """
    research_lib = _research_lib_module()
    source_gate = _source_gate_module()
    if research_lib is None or source_gate is None:
        faltan = [n for n, m in (("research_lib", research_lib), ("fuentes", source_gate)) if m is None]
        return [dict(row, despacho={
            "estado": "sin_despacho",
            "motivo": "modulo(s) no disponible(s): " + ", ".join(faltan),
        }) for row in filas]

    nombres_conocidos = _nombres_conocidos(catalogo)
    edb = _catalog_db_module()
    results = []
    for i, row in enumerate(filas):
        if limite is not None and i >= limite:
            break
        if not _senal_suficiente(row):
            results.append(dict(row, despacho={
                "estado": "sin_senal",
                "motivo": "sin venue especifico, headliner legible ni productora declarada",
            }))
            continue

        query = _query_de(row)
        errores: list[str] = []
        busqueda = research_lib.web_search(query, max_results=5, errors=errores)
        if busqueda.get("ciego"):
            results.append(dict(row, despacho={
                "estado": "sin_busqueda",
                "query": query,
                "motivo": busqueda.get("motivo") or "ningun buscador disponible",
            }))
            continue

        urls = [r.get("url") for r in (busqueda.get("results") or []) if r.get("url")]
        gate = source_gate.evaluar(row.get("pregunta") or query, urls, SOURCE_DOMAIN)
        combined_text = "\n".join(
            "%s %s" % (r.get("title", ""), r.get("content", ""))
            for r in (busqueda.get("results") or [])
        )
        hallados = _known_names_in_text(combined_text, nombres_conocidos)

        canonico_declarado = None
        if row.get("productora_declarada"):
            canonico, ratio = edb.mejor_match(row["productora_declarada"], catalogo)
            if edb.clasificar_ratio(ratio) == "match":
                canonico_declarado = canonico

        primarias = gate["fuentes_primarias"]
        dominios_primarios = sorted({
            urlsplit(u).netloc.lower().removeprefix("www.") for u in primarias
        })

        if canonico_declarado and canonico_declarado in hallados and dominios_primarios:
            estado = "confirmado"
        elif hallados and len(dominios_primarios) >= 2:
            estado = "candidata_alta_confianza"
        elif hallados and len(dominios_primarios) == 1:
            estado = "candidata_media_confianza"
        elif hallados:
            estado = "candidata_sin_fuente_primaria"
        else:
            estado = "sin_hallazgo"

        results.append(dict(row, despacho={
            "estado": estado,
            "query": query,
            "productora_declarada_confirmada": canonico_declarado,
            "candidatos_conocidos_hallados": sorted(hallados),
            "fuentes_primarias": primarias,
            "fuentes_secundarias": gate["fuentes_secundarias"],
            "dominios_primarios_independientes": dominios_primarios,
            "revision_humana": "pendiente",
        }))
    return results


def _build_queue() -> list[dict]:
    con_fecha = con_prod = preguntas = 0
    filas = []
    ultimas = {}
    with open(FICHAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except Exception:
                continue
            clave = "%s:%s" % (f.get("fuente", ""), f.get("ruta_rel", ""))
            ultimas[clave] = f
    for f in ultimas.values():
        if f.get("fuente") != "rd":
            continue
        if f.get("categoria") not in ("flyer_evento", "foto_evento"):
            continue
        e = f.get("datos_evento") or {}
        fecha = _txt(e.get("fecha"))
        prod = _txt(e.get("productora"))
        venue = _txt(e.get("venue"))
        handles = e.get("handles") or []
        if isinstance(handles, str): handles = [handles]
        headliner_evidence = _headliner_evidence(f.get("ocr_texto") or "")
        heads = headliner_evidence["candidatos"]

        if fecha:
            con_fecha += 1
        if prod:
            con_prod += 1

        # Solo vale preguntar si hay fecha Y algo que identifique el evento.
        if not fecha or not (heads or handles or venue):
            continue
        if prod:
            estado = "confirmar"
            pregunta = (
                "Verificar si la productora '%s' organizo el evento del %s"
                % (prod, fecha)
                + (" en %s" % venue if venue else "")
                + (" con %s en el cartel" % ", ".join(heads[:3]) if heads else "")
                + ". Responder con fuente."
            )
        else:
            estado = "descubrir"
            pregunta = (
                "Que productora organizo el evento del %s" % fecha
                + (" en %s" % venue if venue else "")
                + (" con %s en el cartel" % ", ".join(heads[:3]) if heads else "")
                + (" (cuentas visibles: %s)" % ", ".join(handles[:3]) if handles else "")
                + "? Responder con la fuente que lo confirma."
            )
        preguntas += 1
        filas.append({
            "id_ficha": f.get("id"),
            "archivo": f.get("ruta_rel"),
            "estado": estado,
            "fecha": fecha,
            "venue": venue,
            "productora_declarada": prod,
            "handles": handles,
            "headliners_candidatos": heads,
            "headliners_fuentes": headliner_evidence["fuentes"],
            "pregunta": pregunta,
        })

    with open(SALIDA, "w", encoding="utf-8") as fh:
        for r in filas:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    descubrir = sum(1 for r in filas if r["estado"] == "descubrir")
    print("  flyers con fecha        :", con_fecha)
    print("  flyers con productora   :", con_prod)
    print("  PREGUNTAS armadas       :", preguntas)
    print("    a descubrir           :", descubrir)
    print("    a confirmar           :", preguntas - descubrir)
    print("  salida                  :", SALIDA)
    if filas:
        print()
        print("  ejemplo:", filas[0]["pregunta"][:150])
    return filas


def _read_queue() -> list[dict]:
    if not os.path.exists(SALIDA):
        return []
    filas = []
    with open(SALIDA, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            linea = linea.strip()
            if linea:
                filas.append(json.loads(linea))
    return filas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--despachar", action="store_true",
        help="Ademas de armar la cola, correr busqueda real por cada pregunta "
             "(SearXNG/Firecrawl/Tavily) y cruzarla contra data/rd.db + el gate "
             "de fuentes primarias. Nunca escribe a data/rd.db: solo deja "
             "%s para revision humana." % DISPATCH_RESULTS_PATH)
    ap.add_argument(
        "--solo-despacho", action="store_true",
        help="No reconstruye la cola desde fichas.jsonl: despacha la que ya "
             "esta en %s. Implica --despachar." % SALIDA)
    ap.add_argument(
        "--limite", type=int, default=25,
        help="Maximo de preguntas a despachar en esta corrida (default 25): "
             "cada una es una busqueda web real, no una operacion gratis.")
    args = ap.parse_args(argv)

    if args.solo_despacho:
        filas = _read_queue()
        print("  cola leida de disco     :", len(filas))
    else:
        filas = _build_queue()

    if not (args.despachar or args.solo_despacho):
        return

    edb = _catalog_db_module()
    if edb is None:
        print("\n  despacho: extraccion_db no disponible, no se puede cruzar "
              "contra data/rd.db -- abortado.")
        return
    catalogo = edb.cargar_catalogo_productoras()
    results = despachar(filas, catalogo, limite=args.limite)

    with open(DISPATCH_RESULTS_PATH, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    counts = {}
    for r in results:
        estado = r["despacho"]["estado"]
        counts[estado] = counts.get(estado, 0) + 1
    print("\n  DESPACHO (%d de %d preguntas, catalogo=%d productoras)"
          % (len(results), len(filas), len(catalogo)))
    for estado, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("    %-32s: %d" % (estado, n))
    print("  salida                  :", DISPATCH_RESULTS_PATH)
    print("  revision_humana         : pendiente en todas las filas "
          "(ninguna se escribe a data/rd.db automaticamente)")


if __name__ == "__main__":
    main()
