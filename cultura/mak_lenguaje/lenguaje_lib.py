#!/usr/bin/env python3
"""lenguaje_lib.py -- el idioma como senal cultural (proyecto Tilde de flujo).

Las marcas del espanol (tildes, enies, signos de apertura) son payload
cultural de baja entropia; su perdida es degradacion del canal. Este
modulo la MIDE, detecta sospechosas, y construye el lexico vivo del corpus.
Stdlib-only.
"""
import json
import os
import re
import time
import unicodedata

BASE = "/home/mak/lenguaje"
DICCIONARIO = os.path.join(BASE, "diccionarios", "es.txt")
LEXICO_DIR = os.path.join(BASE, "lexico")

_TILDES = set("áéíóúÁÉÍÓÚ")
_PALABRA_RE = re.compile(r"[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]{2,}")
_INTERROG = ("que", "como", "cuando", "donde", "quien", "cual", "cuanto")

STOPWORDS = set("""a al algo ante antes aqui asi aun bajo bien cada casi como
con contra cual cuando de del desde donde dos el ella ellas ellos en entre
era eran es esa esas ese eso esos esta estaba estan estas este esto estos fue
fueron ha habia han hasta hay la las le les lo los mas me mi mientras muy nada
ni no nos nosotros o os otra otras otro otros para pero poco por porque que
quien se segun ser si sin sobre solo son su sus tal tambien tan tanto te tiene
tienen toda todas todo todos tras tu un una unas uno unos y ya yo les esta
""".split())


def medir_senal(texto):
    """Metricas de senal cultural. Puntaje 0-100: parte de 100 y descuenta
    12 puntos por cada palabra sospechosa por cada 100 palabras (proxy
    honesto de senal destruida), con piso 0. Si el texto casi no usa
    vocabulario tildable, el puntaje no castiga (ratio esperado bajo)."""
    palabras = _PALABRA_RE.findall(texto)
    total = len(palabras)
    tildes = sum(1 for c in texto if c in _TILDES)
    enies = texto.count("ñ") + texto.count("Ñ")
    aperturas = texto.count("¿") + texto.count("¡")

    sospechosas = []
    for w in palabras:
        lw = w.lower()
        if lw.endswith("cion") and lw + "?" not in ("",):
            sospechosas.append(w)   # -cion sin tilde: casi siempre -ción
    # "ano/anos" tras numero o "hace": anio degradado
    for m in re.finditer(r"(\d+|hace)\s+(anos?|ano)\b", texto, re.I):
        sospechosas.append(m.group(0))
    # interrogativa sin tilde con signo de pregunta en la frase
    for m in re.finditer(r"\b(%s)\b[^.?!\n]{0,60}\?" % "|".join(_INTERROG),
                         texto, re.I):
        sospechosas.append(m.group(1))

    puntaje = 100.0
    if total > 0:
        puntaje -= 12.0 * (len(sospechosas) / max(1.0, total / 100.0))
    puntaje = max(0, min(100, round(puntaje)))
    return {
        "total_palabras": total,
        "tildes": tildes,
        "enies": enies,
        "aperturas": aperturas,
        "ratio_tilde": round(tildes / total, 4) if total else 0.0,
        "sospechosas": sospechosas[:25],
        "n_sospechosas": len(sospechosas),
        "puntaje": puntaje,
    }


def medir_archivo(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return medir_senal(f.read())


def cargar_diccionario():
    """Set de palabras del diccionario plano (una por linea, NFC lower)."""
    try:
        with open(DICCIONARIO, encoding="utf-8", errors="replace") as f:
            return {unicodedata.normalize("NFC", w.strip().lower())
                    for w in f if w.strip()}
    except OSError:
        return set()


def desconocidas(texto, dic):
    """Palabras del texto ausentes del diccionario (revision basica)."""
    if not dic:
        return []
    vistas, out = set(), []
    for w in _PALABRA_RE.findall(texto):
        lw = unicodedata.normalize("NFC", w.lower())
        if lw not in dic and lw not in vistas and len(lw) > 3:
            vistas.add(lw)
            out.append(w)
    return out[:60]


def construir_lexicon(dirs, out_dir=LEXICO_DIR, top=200):
    """Vocabulario VIVO del corpus: frecuencias de terminos de los .md."""
    freq = {}
    archivos = 0
    for d in dirs:
        try:
            nombres = os.listdir(d)
        except OSError:
            continue
        for n in nombres:
            if not n.endswith(".md"):
                continue
            archivos += 1
            try:
                with open(os.path.join(d, n), encoding="utf-8",
                          errors="replace") as f:
                    texto = f.read()
            except OSError:
                continue
            for w in _PALABRA_RE.findall(texto):
                lw = w.lower()
                if lw in STOPWORDS or len(lw) < 4:
                    continue
                freq[lw] = freq.get(lw, 0) + 1
    ranking = sorted(freq.items(), key=lambda kv: -kv[1])[:top]
    os.makedirs(out_dir, exist_ok=True)
    fecha = time.strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(out_dir, "lexicon.md"), "w", encoding="utf-8") as f:
        f.write("# Léxico vivo del organismo MAK\n\n")
        f.write("%s · %d archivos · %d términos únicos\n\n"
                % (fecha, archivos, len(freq)))
        for w, c in ranking:
            f.write("- %s (%d)\n" % (w, c))
    with open(os.path.join(out_dir, "lexicon.json"), "w",
              encoding="utf-8") as f:
        json.dump({"fecha": fecha, "archivos": archivos,
                   "terminos": dict(ranking)}, f, ensure_ascii=False, indent=1)
    return {"archivos": archivos, "unicos": len(freq), "top": len(ranking)}
