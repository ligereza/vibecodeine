"""conversacion.py -- reads a month of sessions as a corpus, not as history.

Third sibling of `arqueologia.py` (which reads git history) and `esfuerzo.py`
(which reads the cost of producing a report as a measurement of the topic).
Same mould, third corpus: the session transcripts.

Nobody wrote them to be read this way. They piled up on their own, dated, under
`~/.claude/projects/<project>/*.jsonl`, and they hold the one thing the repo
does NOT have: what the user decided, ordered, corrected and had to repeat.
That is why they can be read backwards over everything already accumulated,
with nothing instrumented in advance.

The two rules inherited from its siblings, for the same reasons:

  1. NO hand-written allowlist decides what gets read. Record types and content
     blocks are DISCOVERED in the corpus; whatever the extractor sees and
     cannot read is reported OUT LOUD in the "not understood" section instead
     of vanishing silently.

  2. NO default values. If a datum did not arrive it stays absent and is
     counted as absent. Filling it with something plausible would make the gap
     indistinguishable from a real measurement.

And the third one, which is what makes this worth running:

  3. The output is NOT the raw figure. A topic that was discussed a lot takes
     up many turns and that says nothing. What comes out is the RESIDUAL:
     observed minus expected for its size. The anomaly is the finding.

The central instrument is MECHANICAL and costs zero tokens: a topic the user
had to explain again in DIFFERENT SESSIONS is a topic nobody wrote down.
Repetition across sessions -- not within one -- is the signature of a lost
decision.

Usage:
    py tools/conversacion.py estratos [--raiz ...] [--salida turnos.jsonl]
    py tools/conversacion.py medir    --turnos turnos.jsonl [--salida CONVERSACION.md]
    py tools/conversacion.py lotes    --turnos turnos.jsonl --destino lotes/ [--ventana 95000]
    py tools/conversacion.py clasificar --turnos turnos.jsonl --capa usuario --salida m.json
    py tools/conversacion.py citar    --turnos turnos.jsonl --marcados marcados.json

Stdlib-only, Python 3.11.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterator

# Content blocks that ARE human or assistant speech. Everything else
# (tool_use, tool_result, thinking, images) is counted apart: it is the repo
# pasted back, not conversation. Measured: 39.2 MB out of 47 MB.
BLOQUES_TEXTO = {"text"}

# Which turn a human wrote is NOT guessed from the text: the record already
# carries it in `origin.kind`. The first version of this module decided it
# with a hand-written list of prefixes, and that list stopped matching
# reality -- compaction summaries and skill prompts begin with none of them,
# entered as user speech and ate the top 30 places of the measurement. Same
# defect shape this repo has already seen seven times. The field is read,
# never inferred.
CLASE_HUMANA = "human"

# `promptSource` says HOW that human turn arrived (typed, via SDK, queued,
# suggestion accepted). It does not filter: it is kept so it can be counted.
# A turn with no `origin.kind` is assumed neither human nor synthetic: it is
# counted apart, because not knowing is a datum and filling it would invent
# one.

PALABRAS_VACIAS = {
    "que", "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "es",
    "por", "con", "no", "se", "lo", "para", "del", "al", "me", "te", "si",
    "mas", "pero", "como", "esta", "este", "eso", "esa", "ese", "ya", "hay",
    "the", "to", "of", "and", "in", "is", "it", "for", "on", "with", "you",
}


# --------------------------------------------------------------------- lectura

def _texto_de(contenido: Any, no_entendidos: collections.Counter) -> tuple[str, int]:
    """Returns (human text, non-text blocks). Rule 1: what it does not
    understand gets COUNTED, not dropped."""
    if isinstance(contenido, str):
        return contenido, 0
    if not isinstance(contenido, list):
        no_entendidos["contenido:" + type(contenido).__name__] += 1
        return "", 0
    partes, otros = [], 0
    for b in contenido:
        if not isinstance(b, dict):
            no_entendidos["bloque:" + type(b).__name__] += 1
            continue
        t = b.get("type")
        if t in BLOQUES_TEXTO:
            v = b.get("text")
            if isinstance(v, str):
                partes.append(v)
            else:
                no_entendidos["text-sin-str"] += 1
        else:
            otros += 1
            no_entendidos["bloque:" + str(t)] += 1
    return "\n".join(partes), otros


def _clase_de(d: dict) -> str:
    """`humano`, `harness` or `sin_declarar`. The record says so, not the text."""
    origen = d.get("origin")
    if not isinstance(origen, dict):
        return "sin_declarar" if origen is None else "harness"
    kind = origen.get("kind")
    if kind is None:
        return "sin_declarar"
    return "humano" if kind == CLASE_HUMANA else "harness"


def leer_turnos(raices: list[Path]) -> tuple[list[dict], collections.Counter,
                                             collections.Counter, list[str]]:
    """Walks the .jsonl files and returns turns with their SOURCE INDEX.

    The index (file, line) is what makes the verbatim quote recoverable
    later without asking any model for it: a paraphrased quote stops being
    the quote."""
    turnos: list[dict] = []
    tipos: collections.Counter = collections.Counter()
    no_entendidos: collections.Counter = collections.Counter()
    avisos: list[str] = []
    n = 0

    archivos: list[Path] = []
    for r in raices:
        if not r.is_dir():
            avisos.append("raiz ausente: %s" % r)
            continue
        archivos += sorted(r.glob("*.jsonl"))
    if not archivos:
        return turnos, tipos, no_entendidos, avisos

    for ruta in archivos:
        try:
            fh = ruta.open(encoding="utf-8", errors="replace")
        except OSError as e:
            avisos.append("ilegible: %s (%s)" % (ruta.name, str(e)[:60]))
            continue
        with fh:
            for i, linea in enumerate(fh, 1):
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    d = json.loads(linea)
                except ValueError:
                    no_entendidos["linea-no-json"] += 1
                    continue
                if not isinstance(d, dict):
                    no_entendidos["linea-no-objeto"] += 1
                    continue
                tipo = d.get("type")
                tipos[str(tipo)] += 1
                if tipo not in ("user", "assistant"):
                    continue
                msg = d.get("message")
                if not isinstance(msg, dict):
                    no_entendidos["mensaje-no-objeto"] += 1
                    continue
                texto, otros = _texto_de(msg.get("content"), no_entendidos)
                texto = texto.strip()
                if not texto:
                    continue
                clase = _clase_de(d) if tipo == "user" else "asistente"
                n += 1
                turnos.append({
                    "n": n,
                    "rol": tipo,
                    "clase": clase,
                    "via": d.get("promptSource"),      # ausente = ausente
                    "ts": d.get("timestamp"),
                    "sesion": d.get("sessionId"),
                    "rama": d.get("gitBranch"),
                    "archivo": ruta.name,
                    "linea": i,
                    "chars": len(texto),
                    "bloques_no_texto": otros,
                    "sintetico": clase != "humano" and tipo == "user",
                    "texto": texto,
                })
    return turnos, tipos, no_entendidos, avisos


# --------------------------------------------------------------------- medicion

def normalizar(txt: str) -> list[str]:
    t = unicodedata.normalize("NFKD", txt.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return [p for p in re.findall(r"[a-z0-9]+", t)
            if len(p) > 2 and p not in PALABRAS_VACIAS]


def repeticion_entre_sesiones(turnos: list[dict], grado: int = 3,
                              minimo_sesiones: int = 3) -> list[dict]:
    """The central instrument, and it costs zero tokens.

    An n-gram the user writes across SEVERAL DIFFERENT SESSIONS is something
    they had to explain again because nobody wrote it down. Repeating it
    inside one session is normal -- that is talking about the topic.
    Repeating it in sessions days apart is the signature of a lost decision.

    What comes back is the RESIDUAL, not the raw count (rule 3): an n-gram
    from a much-discussed topic appears often, and that says nothing. It is
    compared against how many sessions touched any of its words."""
    por_grama: dict[tuple, set] = collections.defaultdict(set)
    por_palabra: dict[str, set] = collections.defaultdict(set)
    ejemplo: dict[tuple, int] = {}

    for t in turnos:
        if t["clase"] != "humano" or not t["sesion"]:
            continue
        pal = normalizar(t["texto"])
        for p in set(pal):
            por_palabra[p].add(t["sesion"])
        for i in range(len(pal) - grado + 1):
            g = tuple(pal[i:i + grado])
            por_grama[g].add(t["sesion"])
            ejemplo.setdefault(g, t["n"])

    filas = []
    for g, sesiones in por_grama.items():
        if len(sesiones) < minimo_sesiones:
            continue
        # Expected: if the topic comes up in S sessions, so do its words. A
        # gram surviving WHOLE across nearly all of them is a formula the
        # user repeats, not a topic being discussed.
        alcance = min(len(por_palabra[p]) for p in g)
        if alcance < len(sesiones):        # should not happen; if it does, no score
            continue
        filas.append({
            "grama": " ".join(g),
            "sesiones": len(sesiones),
            "alcance": alcance,
            "residuo": round(len(sesiones) / alcance, 4),
            "turno_ejemplo": ejemplo[g],
        })
    filas.sort(key=lambda f: (-f["sesiones"], -f["residuo"]))
    return filas


def coste_por_sesion(turnos: list[dict], minimo_turnos: int = 8) -> list[dict]:
    """What each session cost, read as a measurement of the session.

    Straight from `esfuerzo.py`: a topic that needed many user turns PER
    assistant turn was not more expensive, it was worse understood. The
    residual is computed against the median of the corpus."""
    por_sesion: dict[str, list[dict]] = collections.defaultdict(list)
    for t in turnos:
        if t["sesion"]:
            por_sesion[t["sesion"]].append(t)

    filas = []
    for sid, ts in por_sesion.items():
        humanos = [t for t in ts if t["clase"] == "humano"]
        asist = [t for t in ts if t["rol"] == "assistant"]
        # A one-turn session gives insistence 1.00 and scores high on noise:
        # with a single pair there is no ratio to measure. The minimum does
        # not discard the session, it keeps it out of the RANKING.
        if len(humanos) < minimo_turnos or len(asist) < minimo_turnos:
            continue
        fechas = sorted(t["ts"] for t in ts if t["ts"])
        filas.append({
            "sesion": sid,
            "turnos_humanos": len(humanos),
            "turnos_asistente": len(asist),
            "chars_humanos": sum(t["chars"] for t in humanos),
            "insistencia": round(len(humanos) / len(asist), 4),
            "desde": fechas[0][:16] if fechas else None,
            "hasta": fechas[-1][:16] if fechas else None,
            "rama": next((t["rama"] for t in ts if t.get("rama")), None),
        })

    ins = [f["insistencia"] for f in filas]
    if len(ins) >= 3:
        med = statistics.median(ins)
        desv = [abs(x - med) for x in ins]
        mad = statistics.median(desv) or (sum(desv) / len(desv))
        for f in filas:
            # No scale, no score: fabricating one just to show a number is
            # the defect this module exists to avoid.
            f["residuo"] = (round((f["insistencia"] - med) / (1.4826 * mad), 3)
                            if mad > 0 else None)
    else:
        for f in filas:
            f["residuo"] = None
    filas.sort(key=lambda f: -(f["residuo"] if f["residuo"] is not None else -99))
    return filas


# ----------------------------------------------------------------------- lotes

def lotes(turnos: list[dict], ventana_tokens: int, solo_usuario: bool
          ) -> Iterator[tuple[int, list[dict]]]:
    """Cuts the corpus into batches that FIT the model window.

    The estimate is chars/3.4 (Spanish, denser than English). It does not
    crowd the limit: the cap exists so no turn is sliced in half, because a
    truncated turn is misclassified and nobody finds out."""
    seleccion = [t for t in turnos
                 if not t["sintetico"] and (t["rol"] == "user" or not solo_usuario)]
    lote: list[dict] = []
    acum = 0
    idx = 1
    for t in seleccion:
        cost = t["chars"] / 3.4 + 12          # 12 = el encabezado "[NNNN] "
        if lote and acum + cost > ventana_tokens:
            yield idx, lote
            idx, lote, acum = idx + 1, [], 0
        lote.append(t)
        acum += cost
    if lote:
        yield idx, lote


def render_lote(lote: list[dict], tope_chars: int = 4000) -> str:
    """One turn per block, NUMBERED. The number is the only datum the model
    has to return, and it is what makes the verbatim quote recoverable from
    the transcript without asking the model for it."""
    out = []
    for t in lote:
        txt = t["texto"]
        if len(txt) > tope_chars:
            # The cut is declared. A silent truncation is a false datum.
            txt = txt[:tope_chars] + "\n[...CORTADO %d chars...]" % (len(txt) - tope_chars)
        out.append("[%04d] %s" % (t["n"], txt))
    return "\n\n".join(out)


# -------------------------------------------------------------------- classifier transport

# The model is NOT asked for QUOTES. It is asked for turn NUMBERS, and the
# quote comes from the transcript by index. A paraphrased decision stops
# being the decision -- which is exactly the problem this module fixes. It
# is also why the token cap stops being a silent truncation: the output is
# numbers and six-word labels.
PROMPTS = {
    "usuario": (
        "Sos un clasificador de turnos de conversacion. Recibis turnos "
        "NUMERADOS de una persona hablando con asistentes de IA sobre su "
        "repositorio. Devolves SOLO un objeto JSON, sin explicaciones ni "
        "markdown.",
        "Clasifica cada turno. NO copies ni cites el texto: ya lo tengo. "
        "Devolve el NUMERO del turno y una etiqueta.\n\n"
        '{"marcados": [{"n": 1234, "tipo": "decision|orden|correccion|queja", '
        '"sobre": "de que trata, MAXIMO 6 palabras"}]}\n\n'
        "REGLAS:\n"
        "- `decision`: elige entre opciones, define como debe ser algo, "
        "cierra un debate.\n"
        "- `orden`: pide que se haga algo concreto.\n"
        "- `correccion`: le dice al asistente que se equivoco.\n"
        "- `queja`: repite algo con fastidio, o reclama que no se hizo.\n"
        "- Un turno que no es ninguna de las cuatro NO se incluye. Una lista "
        "corta y cierta vale mas que una larga e inflada.\n"
        "- `sobre` es una ETIQUETA para agrupar despues, no un resumen.\n"
        "- Si dudas entre incluir y no incluir, no incluyas.\n\n"
        "TURNOS:\n"
    ),
    "asistente": (
        "Sos un clasificador de turnos de un asistente de IA. Devolves SOLO "
        "un objeto JSON, sin explicaciones ni markdown.",
        "Estos son turnos NUMERADOS de un asistente hablandole a su usuario. "
        "Busco lo que PROMETIO y pudo no haberse hecho. NO copies el texto.\n\n"
        '{"marcados": [{"n": 1234, "tipo": "promesa|pendiente|afirmacion", '
        '"sobre": "que cosa, MAXIMO 6 palabras", '
        '"objeto": "el archivo, comando o ruta nombrado, o null"}]}\n\n'
        "REGLAS:\n"
        "- `promesa`: dice que VA a hacer algo (\"voy a\", \"ahora escribo\", "
        "\"queda pendiente\").\n"
        "- `pendiente`: declara algo sin terminar, bloqueado o dejado para "
        "despues.\n"
        "- `afirmacion`: declara algo HECHO o funcionando (\"listo\", "
        "\"queda verde\", \"ya corre\").\n"
        "- `objeto` es literal: el nombre de archivo, comando o ruta que el "
        "turno nombra. Si no nombra ninguno, null. NO lo inventes ni lo "
        "deduzcas: sin objeto no se puede verificar despues, y eso es un "
        "dato, no un problema.\n"
        "- Un turno que no es ninguna de las tres NO se incluye.\n"
        "- Si dudas entre incluir y no incluir, no incluyas.\n\n"
        "TURNOS:\n"
    ),
}


def _json_de(txt: str) -> dict | None:
    """Pulls the JSON object out of a response that may arrive decorated.
    Returns None when there is none: a format failure is COUNTED, never
    filled with an empty list that later reads as a run with no findings."""
    t = txt.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-z]*\n|\n```$", "", t).strip()
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        d = json.loads(t[i:j + 1])
    except ValueError:
        return None
    return d if isinstance(d, dict) else None


# ----------------------------------------------------------------------- salida

def informe(turnos, tipos, no_entendidos, avisos, gramas, sesiones, top) -> str:
    humanos = [t for t in turnos if t["clase"] == "humano"]
    harness = [t for t in turnos if t["clase"] == "harness"]
    sin_decl = [t for t in turnos if t["clase"] == "sin_declarar"]
    asist = [t for t in turnos if t["rol"] == "assistant"]
    vias = collections.Counter(t["via"] for t in humanos)

    L = ["# Conversacion -- el mes de sesiones leido como corpus", "",
         "Generado por `conversacion.py`, tercer hermano de `arqueologia.py` y "
         "`esfuerzo.py`. Nadie escribio estas transcripciones para ser leidas "
         "asi; por eso se pueden leer hacia atras sobre todo lo ya acumulado.",
         ""]

    L += ["## Alcance", "",
          "- turnos con texto: **%d**" % len(turnos),
          "- escritos por un humano (`origin.kind`, no inferido del texto): "
          "**%d** (%.1f MB) -- %s" % (
              len(humanos), sum(t["chars"] for t in humanos) / 1e6,
              ", ".join("%s %d" % (k, v) for k, v in vias.most_common())),
          "- inyectados por el harness: **%d** (contados, no borrados)" % len(harness),
          "- sin origen declarado: **%d** (no se asumen humanos ni harness)"
          % len(sin_decl),
          "- del asistente: **%d** (%.1f MB)" % (
              len(asist), sum(t["chars"] for t in asist) / 1e6),
          "- sesiones distintas: **%d**" % len({t["sesion"] for t in turnos if t["sesion"]}),
          ""]

    fechas = sorted(t["ts"] for t in turnos if t["ts"])
    if fechas:
        L += ["- rango: **%s** -> **%s**" % (fechas[0][:10], fechas[-1][:10]), ""]
    else:
        L += ["- rango: **ausente** (ningun turno trajo timestamp)", ""]

    L += ["## Tipos de registro vistos", "",
          "Descubiertos en el corpus, no listados a mano.", "",
          "| veces | tipo |", "|---:|---|"]
    for t, n in tipos.most_common():
        L.append("| %d | `%s` |" % (n, t))
    L.append("")

    L += ["## Lo que se vio y NO se supo leer", "",
          "Regla 1 del modulo: aparece en voz alta en vez de perderse. La "
          "mayor parte es el repo pegado de vuelta -- no es conversacion, y "
          "por eso no entra al corpus.", ""]
    if no_entendidos:
        for k, n in no_entendidos.most_common(20):
            L.append("- `%s` -- %d veces" % (k, n))
    else:
        L.append("- nada: todos los bloques se entendieron.")
    L.append("")

    L += ["## Lo que tuviste que repetir en sesiones DISTINTAS", "",
          "El instrumento central, y no costo un token. Repetir algo dentro "
          "de una sesion es hablar del tema; repetirlo en sesiones separadas "
          "por dias es la firma de algo que nadie anoto. `sesiones` es en "
          "cuantas aparece la frase entera; `alcance`, en cuantas aparece su "
          "palabra menos comun. Un residuo cercano a 1 quiere decir que "
          "cuando el tema sale, sale con estas MISMAS palabras: es una "
          "formula que estas repitiendo, no un tema del que se conversa.", ""]
    if gramas:
        L += ["| sesiones | alcance | residuo | turno | frase |",
              "|---:|---:|---:|---:|---|"]
        for g in gramas[:top]:
            L.append("| %d | %d | %.2f | %d | %s |" % (
                g["sesiones"], g["alcance"], g["residuo"], g["turno_ejemplo"],
                g["grama"]))
    else:
        L.append("- nada supero el minimo de sesiones.")
    L.append("")

    L += ["## Sesiones que mas insistencia costaron", "",
          "Herencia de `esfuerzo.py`: turnos humanos por turno de asistente. "
          "Una sesion con residuo alto no fue mas larga -- fue peor "
          "entendida, y lo que se hablo ahi es candidato a quedar escrito.",
          "", "| residuo | insist. | humanos | asist. | desde | rama |",
          "|---:|---:|---:|---:|---|---|"]
    for f in sesiones[:top]:
        L.append("| %s | %.2f | %d | %d | %s | %s |" % (
            ("%+.2f" % f["residuo"]) if f["residuo"] is not None else "n/d",
            f["insistencia"], f["turnos_humanos"], f["turnos_asistente"],
            f["desde"] or "n/d", (f["rama"] or "n/d")[:28]))
    L.append("")

    if avisos:
        L += ["## Avisos de lectura", ""] + ["- %s" % a for a in avisos[:20]] + [""]
    return "\n".join(L)


# ------------------------------------------------------------------------ main

def _cargar(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("estratos", help="extrae los turnos con su indice de origen")
    e.add_argument("--raiz", action="append", default=None,
                   help="carpeta con *.jsonl; repetible. Por defecto, el "
                        "proyecto y sus worktrees bajo ~/.claude/projects/")
    e.add_argument("--proyecto", default="C--IA-flujo")
    e.add_argument("--salida", default="turnos.jsonl")

    m = sub.add_parser("medir", help="mide el corpus sin gastar un token")
    m.add_argument("--turnos", default="turnos.jsonl")
    m.add_argument("--salida", default="CONVERSACION.md")
    m.add_argument("--top", type=int, default=30)
    m.add_argument("--grado", type=int, default=3)
    m.add_argument("--min-sesiones", type=int, default=3)
    m.add_argument("--json", dest="json_out", default=None)

    lo = sub.add_parser("lotes", help="corta el corpus en lotes que entran en la ventana")
    lo.add_argument("--turnos", default="turnos.jsonl")
    lo.add_argument("--destino", required=True)
    lo.add_argument("--ventana", type=int, default=95000)
    lo.add_argument("--todos-los-roles", action="store_true")

    cl = sub.add_parser("clasificar", help="clasifica lotes con la cadena activa y junta los numeros")
    cl.add_argument("--turnos", default="turnos.jsonl")
    cl.add_argument("--capa", choices=sorted(PROMPTS), required=True)
    cl.add_argument("--orden", default="cerebras,groq,ollama",
                    help="CSV de proveedores activos: remoto primero, Ollama como respaldo")
    cl.add_argument("--ventana", type=int, default=95000)
    cl.add_argument("--max-salida", type=int, default=8000)
    cl.add_argument("--env", default=None)
    cl.add_argument("--salida", required=True)
    cl.add_argument("--crudo", default=None, help="carpeta donde dejar la respuesta literal")
    cl.add_argument("--desde", type=int, default=1, help="primer lote a correr")

    c = sub.add_parser("citar", help="saca la cita TEXTUAL por numero de turno")
    c.add_argument("--turnos", default="turnos.jsonl")
    c.add_argument("--marcados", required=True)
    c.add_argument("--salida", default="CITAS.md")

    a = ap.parse_args()

    if a.cmd == "estratos":
        if a.raiz:
            raices = [Path(r).expanduser() for r in a.raiz]
        else:
            base = Path.home() / ".claude" / "projects"
            raices = sorted(p for p in base.glob(a.proyecto + "*") if p.is_dir())
        turnos, tipos, no_ent, avisos = leer_turnos(raices)
        if not turnos:
            print("sin turnos legibles en: %s" % ", ".join(str(r) for r in raices),
                  file=sys.stderr)
            for x in avisos[:10]:
                print("  ", x, file=sys.stderr)
            return 1
        with Path(a.salida).open("w", encoding="utf-8") as fh:
            for t in turnos:
                fh.write(json.dumps(t, ensure_ascii=False) + "\n")
        meta = Path(a.salida).with_suffix(".meta.json")
        meta.write_text(json.dumps(
            {"tipos": dict(tipos), "no_entendidos": dict(no_ent),
             "avisos": avisos, "raices": [str(r) for r in raices]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        hum = sum(1 for t in turnos if t["rol"] == "user" and not t["sintetico"])
        print("-> %s (%d turnos, %d humanos)\n-> %s" % (a.salida, len(turnos), hum, meta))
        return 0

    if a.cmd == "medir":
        turnos = _cargar(Path(a.turnos))
        meta_p = Path(a.turnos).with_suffix(".meta.json")
        meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.is_file() else {}
        gramas = repeticion_entre_sesiones(turnos, a.grado, a.min_sesiones)
        sesiones = coste_por_sesion(turnos)
        txt = informe(turnos, collections.Counter(meta.get("tipos", {})),
                      collections.Counter(meta.get("no_entendidos", {})),
                      meta.get("avisos", []), gramas, sesiones, a.top)
        Path(a.salida).write_text(txt, encoding="utf-8")
        print("-> %s (%d turnos, %d frases repetidas, %d sesiones)" % (
            a.salida, len(turnos), len(gramas), len(sesiones)))
        if a.json_out:
            Path(a.json_out).write_text(json.dumps(
                {"gramas": gramas, "sesiones": sesiones}, ensure_ascii=False,
                indent=1), encoding="utf-8")
            print("-> %s" % a.json_out)
        return 0

    if a.cmd == "lotes":
        turnos = _cargar(Path(a.turnos))
        dest = Path(a.destino)
        dest.mkdir(parents=True, exist_ok=True)
        n = 0
        for idx, lote in lotes(turnos, a.ventana, not a.todos_los_roles):
            (dest / ("lote_%03d.txt" % idx)).write_text(render_lote(lote),
                                                        encoding="utf-8")
            n = idx
        print("-> %s (%d lotes, ventana %d tokens)" % (dest, n, a.ventana))
        return 0

    if a.cmd == "clasificar":
        import time

        from cultura.mak_research.research_lib import LLM, load_env as load_research_env

        for c_env in ([Path(a.env)] if a.env else
                      [Path.home() / "research" / "research.env"]):
            if c_env.is_file():
                load_research_env(str(c_env))
                break
        orden = [p.strip() for p in a.orden.split(",") if p.strip()]
        llm = LLM(",".join(orden))

        turnos = _cargar(Path(a.turnos))
        rol_pedido = "user" if a.capa == "usuario" else "assistant"
        sel = [t for t in turnos
               if (t["clase"] == "humano" if a.capa == "usuario"
                   else t["rol"] == rol_pedido)]
        system, user = PROMPTS[a.capa]
        crudo = Path(a.crudo) if a.crudo else None
        if crudo:
            crudo.mkdir(parents=True, exist_ok=True)

        todos, fallos, uso_in, uso_out = [], [], 0, 0
        partes = list(lotes(sel, a.ventana, solo_usuario=False))
        print("%d turnos -> %d lotes (orden %s)" % (len(sel), len(partes), a.orden))

        for idx, lote in partes:
            if idx < a.desde:
                continue
            texto = user + render_lote(lote)
            t0 = time.time()
            d = None
            try:
                resp, proveedor = llm.call(system, texto, max_tok=a.max_salida,
                                           order=orden)
                d = {"provider": proveedor,
                     "choices": [{"message": {"content": resp}}]}
            except Exception as e:                # noqa: BLE001 - reported
                fallos.append({"lote": idx, "error": "%s: %s" % (type(e).__name__, e)})
            if d is None:
                print("  lote %d: FALLO" % idx)
                continue
            u = d.get("usage") or {}
            uso_in += u.get("prompt_tokens", 0)
            uso_out += u.get("completion_tokens", 0)
            resp = (d.get("choices", [{}])[0].get("message", {}).get("content") or "")
            if crudo:
                (crudo / ("%s_%03d.txt" % (a.capa, idx))).write_text(resp, encoding="utf-8")
            obj = _json_de(resp)
            if obj is None:
                # A format failure is COUNTED. Filling it with an empty list
                # would make it indistinguishable from a batch with no hits.
                fallos.append({"lote": idx, "error": "respuesta sin JSON legible"})
                print("  lote %d: sin JSON (%d chars)" % (idx, len(resp)))
                continue
            marc = [m for m in obj.get("marcados", []) if isinstance(m, dict)]
            validos = {t["n"] for t in lote}
            dentro = [m for m in marc if m.get("n") in validos]
            todos += dentro
            print("  lote %d/%d: %d marcados (%d fuera de rango) %.0fs" % (
                idx, len(partes), len(dentro), len(marc) - len(dentro), time.time() - t0))

        p_in, p_out = 0.7526, 0.7526
        Path(a.salida).write_text(json.dumps({
            "capa": a.capa, "orden": a.orden, "proveedores": llm.stats,
            "turnos": len(sel),
            "lotes": len(partes), "marcados": todos, "fallos": fallos,
            "uso": {"entrada": uso_in, "salida": uso_out,
                    "usd_aprox": round(uso_in / 1e6 * p_in + uso_out / 1e6 * p_out, 4)},
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print("-> %s\n   %d marcados, %d lotes fallidos, %d+%d tokens (~$%.3f)" % (
            a.salida, len(todos), len(fallos), uso_in, uso_out,
            uso_in / 1e6 * p_in + uso_out / 1e6 * p_out))
        return 0

    if a.cmd == "citar":
        turnos = {t["n"]: t for t in _cargar(Path(a.turnos))}
        datos = json.loads(Path(a.marcados).read_text(encoding="utf-8"))
        marcados = datos.get("marcados", datos if isinstance(datos, list) else [])
        L = ["# Citas -- textuales por construccion", "",
             "El modelo devolvio NUMEROS de turno. La cita sale de la "
             "transcripcion por indice, no de su memoria: no hay nada que "
             "verificar despues.", ""]
        faltan = 0
        for mk in marcados:
            n = mk.get("n")
            t = turnos.get(n)
            if t is None:
                faltan += 1
                continue
            L += ["## [%04d] %s -- %s" % (n, mk.get("tipo", "n/d"),
                                          mk.get("sobre", "n/d")),
                  "", "*%s * `%s:%d`*" % (t["ts"] or "sin fecha", t["archivo"],
                                          t["linea"]), "",
                  "> " + t["texto"].replace("\n", "\n> "), ""]
        if faltan:
            L += ["---", "", "**%d numeros marcados no existen en el corpus** "
                  "(el modelo los invento o se desalineo el lote)." % faltan, ""]
        Path(a.salida).write_text("\n".join(L), encoding="utf-8")
        print("-> %s (%d citas, %d numeros invalidos)" % (
            a.salida, len(marcados) - faltan, faltan))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
