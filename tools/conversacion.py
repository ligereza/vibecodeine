#!/usr/bin/env python3
"""conversacion.py -- lee el mes de conversacion como corpus, no como historial.

Tercer hermano de `arqueologia.py` (que lee el historial de git) y de
`esfuerzo.py` (que lee el costo de producir un informe como medicion del
tema). Mismo molde, tercer corpus: las transcripciones de las sesiones.

Nadie las escribio para ser leidas asi. Se acumularon solas, fechadas, en
`~/.claude/projects/<proyecto>/*.jsonl`, y contienen lo unico que el repo
NO tiene: lo que el usuario decidio, ordeno, corrigio y tuvo que repetir.
Por eso se puede leer hacia atras sobre todo lo ya acumulado, sin
instrumentar nada.

Las dos reglas heredadas de sus hermanos, por las mismas razones:

  1. NINGUNA lista blanca escrita a mano decide que se lee. Los tipos de
     registro y los bloques de contenido se DESCUBREN en el corpus; lo que
     el extractor ve y no sabe leer aparece EN VOZ ALTA en la seccion
     "no entendidos" en vez de perderse en silencio.

  2. NINGUN valor por defecto. Si un dato no vino, queda ausente y se
     cuenta como ausente. Rellenarlo con algo plausible volveria la falta
     indistinguible de una medicion real.

Y la tercera, que es la que hace que valga la pena:

  3. La salida NO es el bruto. Un tema del que se hablo mucho ocupa muchos
     turnos y eso no dice nada. Sale el RESIDUO: lo observado menos lo
     esperado para su tamano. La anomalia es el hallazgo.

El instrumento central es MECANICO y no cuesta un token: un tema que el
usuario tuvo que volver a explicar en SESIONES DISTINTAS es un tema que
nadie anoto. La repeticion entre sesiones -- no dentro de una -- es la
firma de una decision perdida.

Uso:
    py tools/conversacion.py estratos [--raiz ...] [--salida turnos.jsonl]
    py tools/conversacion.py medir    --turnos turnos.jsonl [--salida CONVERSACION.md]
    py tools/conversacion.py lotes    --turnos turnos.jsonl --destino lotes/ [--ventana 95000]
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

# Bloques de contenido que SI son habla humana o del asistente. Todo lo
# demas (tool_use, tool_result, thinking, imagenes) se cuenta aparte: es el
# repo pegado de vuelta, no conversacion. Medido: 39,2 MB de 47 MB utiles.
BLOQUES_TEXTO = {"text"}

# Que turno lo escribio un humano NO se adivina por el texto: el registro
# ya lo trae en `origin.kind`. La primera version de este modulo lo decidia
# por una lista de prefijos escrita a mano, y esa lista dejo de coincidir
# con la realidad -- los resumenes de compactacion y los prompts de skill
# no empiezan por ninguno de ellos, entraron como habla del usuario y se
# comieron los primeros 30 puestos de la medicion. Es la misma forma de
# defecto que el repo ya vio siete veces. El campo se lee, no se infiere.
CLASE_HUMANA = "human"

# `promptSource` distingue COMO llego ese turno humano (tecleado, por SDK,
# encolado, sugerencia aceptada). No filtra: se guarda para poder contar.
# Un turno con `origin.kind` ausente no se asume humano ni sintetico: se
# cuenta aparte, porque no saberlo es un dato y rellenarlo seria inventarlo.

PALABRAS_VACIAS = {
    "que", "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "es",
    "por", "con", "no", "se", "lo", "para", "del", "al", "me", "te", "si",
    "mas", "pero", "como", "esta", "este", "eso", "esa", "ese", "ya", "hay",
    "the", "to", "of", "and", "in", "is", "it", "for", "on", "with", "you",
}


# --------------------------------------------------------------------- lectura

def _texto_de(contenido: Any, no_entendidos: collections.Counter) -> tuple[str, int]:
    """Devuelve (texto humano, bloques no-texto). Regla 1: lo que no
    entiende lo CUENTA, no lo tira."""
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
    """`humano`, `harness` o `sin_declarar`. Lo dice el registro, no el texto."""
    origen = d.get("origin")
    if not isinstance(origen, dict):
        return "sin_declarar" if origen is None else "harness"
    kind = origen.get("kind")
    if kind is None:
        return "sin_declarar"
    return "humano" if kind == CLASE_HUMANA else "harness"


def leer_turnos(raices: list[Path]) -> tuple[list[dict], collections.Counter,
                                             collections.Counter, list[str]]:
    """Recorre los .jsonl y devuelve turnos con su INDICE de origen.

    El indice (archivo, linea) es lo que permite sacar la cita textual
    despues sin pedirsela a ningun modelo: una cita parafraseada deja de
    ser la cita."""
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
    """El instrumento central, y no cuesta un token.

    Un n-grama que el usuario escribe en VARIAS SESIONES DISTINTAS es algo
    que tuvo que volver a explicar porque nadie lo anoto. Repetirlo dentro
    de una sesion es normal -- se esta hablando del tema. Repetirlo en
    sesiones separadas por dias es la firma de una decision perdida.

    Se devuelve el RESIDUO, no el bruto (regla 3): un n-grama de un tema
    del que se hablo mucho aparece mucho, y eso no dice nada. Se compara
    contra cuantas sesiones tocaron alguna de sus palabras."""
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
        # Esperado: si el tema se toca en S sesiones, sus palabras tambien.
        # Un grama que sobrevive ENTERO en casi todas esas sesiones es una
        # formula que el usuario repite, no un tema del que se habla.
        alcance = min(len(por_palabra[p]) for p in g)
        if alcance < len(sesiones):        # no deberia pasar; si pasa, no puntua
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
    """Cuanto costo cada sesion, leido como medicion de la sesion.

    Herencia directa de `esfuerzo.py`: un tema que necesito muchos turnos
    del usuario POR turno del asistente no fue mas caro, fue peor
    entendido. El residuo se calcula contra la mediana del corpus."""
    por_sesion: dict[str, list[dict]] = collections.defaultdict(list)
    for t in turnos:
        if t["sesion"]:
            por_sesion[t["sesion"]].append(t)

    filas = []
    for sid, ts in por_sesion.items():
        humanos = [t for t in ts if t["clase"] == "humano"]
        asist = [t for t in ts if t["rol"] == "assistant"]
        # Una sesion de un turno da insistencia 1.00 y puntua alto por ruido:
        # con un solo par no hay proporcion que medir. El minimo no descarta
        # la sesion, la deja fuera del RANKING, que es cosa distinta.
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
            # Sin escala no se puntua: fabricar una para mostrar un numero
            # es el defecto que este modulo evita.
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
    """Corta el corpus en lotes que ENTRAN en la ventana del modelo.

    La estimacion es chars/3.4 (espanol, mas denso que ingles). No se
    apura al limite: el tope existe para que ningun turno se recorte a la
    mitad, porque un turno cortado se clasifica mal y nadie se entera."""
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
    """Un turno por bloque, NUMERADO. El numero es el unico dato que el
    modelo tiene que devolver, y es lo que permite recuperar la cita
    textual de la transcripcion sin pedirsela a el."""
    out = []
    for t in lote:
        txt = t["texto"]
        if len(txt) > tope_chars:
            # Se declara el corte. Un recorte callado es un dato falso.
            txt = txt[:tope_chars] + "\n[...CORTADO %d chars...]" % (len(txt) - tope_chars)
        out.append("[%04d] %s" % (t["n"], txt))
    return "\n\n".join(out)


# -------------------------------------------------------------------- watsonx

# No se le piden CITAS al modelo. Se le piden NUMEROS de turno, y la cita
# sale de la transcripcion por indice. Una decision parafraseada deja de
# ser la decision -- que es justo el problema que este modulo arregla. Ese
# es tambien el motivo de que el tope de tokens deje de ser un recorte
# callado: la salida son numeros y etiquetas de seis palabras.
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


def _wx_token(key: str) -> str:
    import urllib.parse
    import urllib.request
    cuerpo = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": key,
    }).encode()
    req = urllib.request.Request(
        "https://iam.cloud.ibm.com/identity/token", data=cuerpo,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json",
                 "User-Agent": "flujo-conversacion/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))["access_token"]


def _wx_chat(base, tok, proyecto, modelo, system, user, max_tok, timeout=600):
    import urllib.request
    payload = {
        "model_id": modelo, "project_id": proyecto,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_tokens": max_tok, "temperature": 0,
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/ml/v1/text/chat?version=2024-10-08",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json",
                 "User-Agent": "flujo-conversacion/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _json_de(txt: str) -> dict | None:
    """Saca el objeto JSON de una respuesta que pudo venir con adornos.
    Devuelve None si no hay: un fallo de formato se CUENTA, no se rellena
    con una lista vacia que despues parece una lectura sin hallazgos."""
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

    cl = sub.add_parser("clasificar", help="manda los lotes a watsonx y junta los numeros")
    cl.add_argument("--turnos", default="turnos.jsonl")
    cl.add_argument("--capa", choices=sorted(PROMPTS), required=True)
    cl.add_argument("--modelo", default="meta-llama/llama-3-3-70b-instruct")
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
        import os
        import time
        import urllib.error

        for c_env in ([Path(a.env)] if a.env else
                      [Path.home() / ".mak" / "research.env",
                       Path.home() / "n8n-local" / "research.env"]):
            if c_env.is_file():
                for ln in c_env.read_text(encoding="utf-8").splitlines():
                    ln = ln.strip()
                    if ln and not ln.startswith("#") and "=" in ln:
                        k, v = ln.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
                break
        key = os.environ.get("WATSONX_API_KEY", "").strip()
        proy = os.environ.get("WATSONX_PROJECT_ID", "").strip()
        base = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        if not key or not proy:
            print("falta WATSONX_API_KEY / WATSONX_PROJECT_ID", file=sys.stderr)
            return 2

        turnos = _cargar(Path(a.turnos))
        rol_pedido = "user" if a.capa == "usuario" else "assistant"
        sel = [t for t in turnos
               if (t["clase"] == "humano" if a.capa == "usuario"
                   else t["rol"] == rol_pedido)]
        system, user = PROMPTS[a.capa]
        crudo = Path(a.crudo) if a.crudo else None
        if crudo:
            crudo.mkdir(parents=True, exist_ok=True)

        tok, t_tok = _wx_token(key), time.time()
        todos, fallos, uso_in, uso_out = [], [], 0, 0
        partes = list(lotes(sel, a.ventana, solo_usuario=False))
        print("%d turnos -> %d lotes (modelo %s)" % (len(sel), len(partes), a.modelo))

        for idx, lote in partes:
            if idx < a.desde:
                continue
            if time.time() - t_tok > 3000:          # el bearer vence a la hora
                tok, t_tok = _wx_token(key), time.time()
            texto = user + render_lote(lote)
            t0 = time.time()
            d = None
            for intento in range(4):
                try:
                    d = _wx_chat(base, tok, proy, a.modelo, system, texto, a.max_salida)
                    break
                except urllib.error.HTTPError as e:
                    cuerpo = ""
                    try:
                        cuerpo = e.read().decode("utf-8", "replace")[:200]
                    except Exception:
                        pass
                    if e.code in (429, 500, 502, 503, 504) and intento < 3:
                        time.sleep(5 * (intento + 1))
                        continue
                    if e.code == 401 and intento < 3:
                        tok, t_tok = _wx_token(key), time.time()
                        continue
                    fallos.append({"lote": idx, "error": "HTTP %d %s" % (e.code, cuerpo)})
                    break
                except Exception as e:                # noqa: BLE001 - se reporta
                    if intento < 3:
                        time.sleep(5 * (intento + 1))
                        continue
                    fallos.append({"lote": idx, "error": "%s: %s" % (type(e).__name__, e)})
                    break
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
                # Un fallo de formato se CUENTA. Rellenarlo con una lista
                # vacia lo volveria indistinguible de un lote sin hallazgos.
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
            "capa": a.capa, "modelo": a.modelo, "turnos": len(sel),
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
