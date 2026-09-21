#!/usr/bin/env python3
"""Convierte los flyers de RD ya percibidos en preguntas de investigacion.

La formula es del usuario (2026-07-26): "si tienes headliner y tienes fecha =
tienes productora potencialmente encontrable por research". Ese paso nunca se
construyo: desde el 2026-07-23 hay 132 flyers con fecha y productora/handle
esperando en ~/curatoria/fichas/fichas.jsonl, y nadie los mando a research.

El modo de cola solo prepara preguntas. El modo normal además entrega esas
preguntas al departamento Research, busca con consultas alternativas, cruza
fuentes y fija una decisión explícita. No deja productoras en estado
"candidata" después del despacho.

Salida: ~/curatoria/triangulacion.jsonl (una línea por pregunta) y
~/curatoria/triangulacion_resultado.jsonl (decisiones y evidencia). `--solo-cola`
es el único modo que evita la búsqueda.

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

# mak_forense is the shared provenance engine. Triangular owns the queue,
# but it must not silently discard the history of a ficha when the same file is
# perceived again: the engine marks that history and leaves the decision to a
# person.
try:
    from cultura.mak_forense.patrones import analizar as _analizar_procedencia
    from cultura.mak_forense.registro import Registro as _RegistroForense
except ImportError:  # pragma: no cover - only for a partial checkout
    _analizar_procedencia = None
    _RegistroForense = None

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
    """Nombres candidatos del cartel, desde OCR y reglas locales.

    La ruta heurística es determinista; sus candidatos nunca se tratan como
    confirmaciones y la cola conserva su procedencia.
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


def _headliner_evidence(texto):
    heuristic = _heuristic_headliners(texto)
    candidates = []
    sources = []
    for value in heuristic:
        if value.lower() not in {item.lower() for item in candidates}:
            candidates.append(value)
    if heuristic:
        sources.append({"kind": "ocr_heuristic", "status": "observed"})
    return {"candidatos": candidates[:5], "fuentes": sources, "external_enrichment": "retired"}



def _txt(v):
    """El modelo a veces devuelve lista donde el schema pide string."""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v if x).strip()
    return str(v or "").strip()


def _ficha_contenido(ficha: dict) -> tuple:
    """Contenido comparable de una ficha, sin campos de identidad temporal.

    fecha queda fuera a propósito: si la misma ficha aparece asociada a otra
    fecha, eso es justamente una señal que debe quedar visible en la historia,
    no una forma de esconder la repetición porque cambió un campo. Los campos
    volátiles de percepción tampoco participan.
    """
    evento = dict(ficha.get("datos_evento") or {})
    evento.pop("fecha", None)
    evento.pop("fecha_evento", None)
    return (
        str(ficha.get("categoria") or "").strip().lower(),
        json.dumps(evento, ensure_ascii=False, sort_keys=True, default=str),
        json.dumps(ficha.get("vision") or {}, ensure_ascii=False,
                   sort_keys=True, default=str),
        str(ficha.get("ocr_texto") or "").strip().lower(),
    )


def _procedencia_fichas(versiones: list[dict]) -> dict:
    """Resume la historia de una misma ficha usando mak_forense.

    La cola conserva solo la versión más reciente para investigar, pero la
    procedencia viaja con ella. Una segunda percepción nunca se convierte en
    un reemplazo silencioso: queda marcada y revisable.
    """
    ids = [str(f.get("id") or "") for f in versiones]
    fechas = sorted({
        _txt((f.get("datos_evento") or {}).get("fecha"))
        for f in versiones
        if _txt((f.get("datos_evento") or {}).get("fecha"))
    })
    base = {
        "motor": "mak_forense",
        "versiones_observadas": len(versiones),
        "ids": ids,
        "fechas_observadas": fechas,
        "revision_humana": "pendiente" if len(versiones) > 1 else "no_requerida",
        "hallazgos": [],
    }
    if _analizar_procedencia is None or _RegistroForense is None:
        base["revision_humana"] = "pendiente"
        base["limite"] = "motor mak_forense no disponible"
        return base

    registros = [
        _RegistroForense(
            id=str(f.get("id") or f"version-{i}"),
            grupo=str(f.get("fuente") or "sin_fuente") + ":" +
                  str(f.get("ruta_rel") or "sin_ruta"),
            orden=i,
            contenido=_ficha_contenido(f),
            fecha_declarada=_txt((f.get("datos_evento") or {}).get("fecha")) or None,
            etiqueta=str(f.get("ruta_rel") or ""),
        )
        for i, f in enumerate(versiones)
    ]
    analisis = _analizar_procedencia(
        registros,
        limites_extra=(
            "la historia de triangular solo compara percepciones del mismo "
            "archivo; no prueba que dos archivos distintos sean la misma fuente",
        ),
    )
    base["hallazgos"] = [
        {
            "patron": h.patron,
            "certeza": h.certeza,
            "registros": list(h.registros),
            "origen": h.origen,
            "evidencia": h.evidencia,
            "explicacion": h.explicacion,
        }
        for h in analisis.hallazgos
    ]
    if analisis.hallazgos:
        base["revision_humana"] = "pendiente"
    return base


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
    # El primer candidato SIN filtrar era el que entraba a la query, aunque
    # `_senal_suficiente` hubiera dejado pasar la fila gracias a OTRO candidato
    # legible. Medido sobre la cola real (200 preguntas): 83 queries llevaban
    # basura de OCR adelante -- "¡ S", "AND)", "SAB 01/AGOSTO - 2026". Es el
    # mismo filtro que ya se aplicaba dos funciones mas arriba.
    heads = [h for h in (row.get("headliners_candidatos") or [])
             if _candidato_legible(h)]
    partes = [p for p in (
        row.get("productora_declarada"),
        "productora evento",
        heads[0] if heads else None,
        venue,
        row.get("fecha"),
    ) if p]
    return " ".join(str(p).strip() for p in partes if str(p).strip())


def _queries_de(row: dict, source_gate=None) -> list[str]:
    """Build a bounded research set for one event, not one fragile query.

    Research must get several independent chances to see the event. The first
    query preserves the structured signal; the others deliberately vary venue,
    headliner, date and the source-domain hints. A search result is evidence,
    not a decision until all returned evidence is ranked below.
    """
    base = _query_de(row)
    if not base:
        return []
    variants = [base]
    venue = str(row.get("venue") or "").strip()
    date_value = str(row.get("fecha") or "").strip()
    heads = [h for h in (row.get("headliners_candidatos") or [])
             if _candidato_legible(h)]
    head = heads[0] if heads else ""
    if head and venue and date_value:
        variants.append(f'"{head}" "{venue}" "{date_value}"')
    if head and date_value:
        variants.append(f'"{head}" "{date_value}" evento Chile')
    if head and venue:
        variants.append(f'"{head}" "{venue}" entradas')
    if source_gate is not None and hasattr(source_gate, "sugerir_queries"):
        try:
            variants.extend(source_gate.sugerir_queries(base, SOURCE_DOMAIN))
        except Exception:  # pragma: no cover - optional research helper
            pass
    output = []
    seen = set()
    for query in variants:
        query = " ".join(str(query or "").split())
        if query and query not in seen:
            seen.add(query)
            output.append(query)
    return output[:6]


def _research_event(research_lib, source_gate, row: dict,
                    max_results: int = 5) -> dict:
    """Search through the Research department and return one evidence packet."""
    queries = _queries_de(row, source_gate)
    errors: list[str] = []
    merged = {}
    engines = []
    blind = []
    for query in queries:
        response = research_lib.web_search(
            query, max_results=max_results, errors=errors)
        engines.append(response.get("motor"))
        if response.get("ciego"):
            blind.append(response.get("motivo") or "research backend ciego")
        for result in response.get("results") or []:
            url = str(result.get("url") or "").strip()
            if url:
                existing = merged.setdefault(url, dict(result))
                existing["queries"] = sorted(set(existing.get("queries") or []) | {query})
    return {
        "queries": queries,
        "results": list(merged.values()),
        "engines": [e for e in engines if e],
        "errors": errors,
        "all_backends_blind": bool(queries) and len(blind) == len(queries),
        "blind_reasons": blind,
    }


def _rank_known_names(text: str, names: set[str], catalogo: list[dict]) -> list[str]:
    """Choose a deterministic catalog name instead of returning candidates."""
    scores = []
    lowered = (text or "").casefold()
    for name in names:
        score = lowered.count(str(name).casefold())
        entry = next((e for e in catalogo if e.get("canonico") == name), {})
        score += len(entry.get("variantes") or []) / 1000
        scores.append((score, str(name)))
    return [name for _, name in sorted(scores, key=lambda item: (-item[0], item[1].casefold()))]


def _decision(row: dict, evidence: dict, catalogo: list[dict], source_gate) -> dict:
    """Make the Research result explicit; never leak a candidate-only state."""
    results = evidence["results"]
    urls = [r.get("url") for r in results if r.get("url")]
    if hasattr(source_gate, "evaluar"):
        gate = source_gate.evaluar(
            row.get("pregunta") or _query_de(row), urls, SOURCE_DOMAIN)
    else:
        # A partial checkout/test double must not crash the adjudicator. It
        # can still decide from the returned results, but cannot call a URL
        # primary without the Research source gate.
        gate = {
            "fuentes_primarias": [],
            "fuentes_secundarias": urls,
        }
    combined_text = "\n".join(
        "%s %s" % (r.get("title", ""), r.get("content", ""))
        for r in results
    )
    known_names = _known_names_in_text(combined_text, _nombres_conocidos(catalogo))
    ranked = _rank_known_names(combined_text, known_names, catalogo)
    declared = None
    edb = _catalog_db_module()
    if row.get("productora_declarada") and edb is not None:
        canonico, ratio = edb.mejor_match(row["productora_declarada"], catalogo)
        if edb.clasificar_ratio(ratio) == "match":
            declared = canonico
    selected = declared or (ranked[0] if ranked else None)
    domains = sorted({urlsplit(u).netloc.lower().removeprefix("www.")
                      for u in gate["fuentes_primarias"]})
    if evidence["all_backends_blind"]:
        status = "bloqueado_tecnico"
        decision_type = "research_unavailable"
        rationale = "Research agotó sus backends sin poder consultar la web."
    elif selected:
        status = "decidido"
        decision_type = "confirmed_primary" if gate["fuentes_primarias"] else "decided_secondary"
        rationale = ("El catálogo y las fuentes consultadas convergen en la entidad "
                     f"{selected}; la decisión queda trazada por URLs y dominios.")
    elif results:
        status = "decidido"
        decision_type = "decided_no_catalog_match"
        rationale = "Research consultó resultados, pero ninguno coincide con el catálogo MAK; se decide no asociar una productora existente."
    else:
        status = "decidido_sin_hallazgo"
        decision_type = "searched_no_match"
        rationale = "Research ejecutó todas las consultas previstas y no encontró una entidad asociable."
    return {
        "status": status,
        "type": decision_type,
        "selected_canonical": selected,
        "declared_match": declared,
        "alternatives": ranked[1:],
        "rationale": rationale,
        "source_tier": "primary" if gate["fuentes_primarias"] else ("secondary" if results else "none"),
        "primary_sources": gate["fuentes_primarias"],
        "secondary_sources": gate["fuentes_secundarias"],
        "independent_primary_domains": domains,
        "queries": evidence["queries"],
        "research_engines": evidence["engines"],
        "research_errors": evidence["errors"],
        "research_blind_reasons": evidence.get("blind_reasons") or [],
        "audit": "non_blocking_human_audit",
    }


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
    """Search, adjudicate and record one explicit decision per event.

    Research owns discovery; MAK owns the deterministic adjudication policy.
    The function never writes the RD database, but it no longer leaves a
    searched row as ``candidate`` or bare ``unknown``. A backend outage is a
    technical block; a completed search yields a decision, including an
    explicit no-match decision.
    """
    research_lib = _research_lib_module()
    source_gate = _source_gate_module()
    if research_lib is None or source_gate is None:
        faltan = [n for n, m in (("research_lib", research_lib), ("fuentes", source_gate)) if m is None]
        return [dict(row, despacho={
            "estado": "bloqueado_tecnico",
            "motivo": "modulo(s) no disponible(s): " + ", ".join(faltan),
            "decision": "Research no está disponible; no se inventa una asociación.",
        }) for row in filas]

    results = []
    for i, row in enumerate(filas):
        if limite is not None and i >= limite:
            break
        if not _senal_suficiente(row):
            results.append(dict(row, despacho={
                "estado": "decidido_sin_senal",
                "motivo": "no hay señal estructurada suficiente para identificar una entidad",
                "decision": {
                    "status": "decidido_sin_senal",
                    "type": "no_identifiable_event_signal",
                    "selected_canonical": None,
                    "rationale": "MAK decide no asociar una productora sin fecha y señal de evento utilizables.",
                    "audit": "non_blocking_human_audit",
                },
            }))
            continue

        evidence = _research_event(research_lib, source_gate, row, max_results=5)
        decision = _decision(row, evidence, catalogo, source_gate)
        results.append(dict(row, despacho={
            "estado": decision["status"],
            "motivo": "; ".join(
                decision.get("research_errors") or
                decision.get("research_blind_reasons") or []
            ),
            "decision": decision,
        }))
    return results


def _build_queue() -> list[dict]:
    con_fecha = con_prod = preguntas = 0
    filas = []
    historiales = {}
    with open(FICHAS, encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except Exception:
                continue
            clave = "%s:%s" % (f.get("fuente", ""), f.get("ruta_rel", ""))
            historiales.setdefault(clave, []).append(f)
    for versiones in historiales.values():
        f = versiones[-1]
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
            "procedencia": _procedencia_fichas(versiones),
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
        help="Alias explicito del despacho Research; la ruta normal ya "
             "investiga y decide automáticamente.")
    ap.add_argument(
        "--solo-cola", action="store_true",
        help="Solo reconstruye la cola y no consulta Research (modo offline).")
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

    if args.solo_cola:
        return

    # La decisión Research es el comportamiento normal. `--despachar` se
    # conserva como alias legible y `--solo-cola` es la única salida explícita.

    edb = _catalog_db_module()
    if edb is None:
        print("\n  despacho: extraccion_db no disponible, no se puede cruzar "
              "contra data/rd.db -- abortado.")
        return
    catalogo = edb.cargar_catalogo_productoras()
    results = despachar(filas, catalogo, limite=args.limite)

    # `--limite 25` despacha 25 de 200, y el modo "w" con solo esas 25 borraba
    # lo despachado en las corridas anteriores. Cada busqueda es una llamada
    # real a un buscador: perderla obliga a pagarla de nuevo. Se conserva lo
    # previo y la corrida de hoy pisa solo SU ficha.
    previos = {}
    if os.path.exists(DISPATCH_RESULTS_PATH):
        with open(DISPATCH_RESULTS_PATH, encoding="utf-8", errors="replace") as fh:
            for linea in fh:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    fila = json.loads(linea)
                except ValueError:
                    continue
                previos[fila.get("id_ficha") or fila.get("archivo")] = fila
    for r in results:
        previos[r.get("id_ficha") or r.get("archivo")] = r
    with open(DISPATCH_RESULTS_PATH, "w", encoding="utf-8") as fh:
        for r in previos.values():
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
    print("  decision_policy         : cada fila recibe decisión explícita; "
          "auditoría humana posterior no bloqueante; data/rd.db no se escribe")


if __name__ == "__main__":
    main()
