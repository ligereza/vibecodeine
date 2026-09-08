#!/usr/bin/env python3
"""
vocabulario.py — El léxico cerrado del sistema.

PRINCIPIO: un agente NO escribe geometría. Elige palabras de estas listas.
Cada primitiva fue verificada visualmente UNA vez por un humano (o por un
modelo con visión). A partir de ahí, cualquier combinación es segura.

Cada figura se dibuja en una caja unitaria de -1..1 centrada en el origen.
El compilador la escala y la ubica; el autor nunca toca coordenadas.
"""
import math

# -------------------------------------------------------------------------
#  FIGURAS — cada una devuelve SVG en caja unitaria (-1..1)
#  Firma: fn(p) -> str    donde p = dict de roles de color ya resueltos
# -------------------------------------------------------------------------

def _espiral(vueltas=3.2, r0=.04, r1=1.0, pasos=200):
    pts = []
    for i in range(pasos + 1):
        t = i / pasos
        a = t * vueltas * 2 * math.pi
        r = r0 + (r1 - r0) * t
        pts.append((r * math.cos(a), r * math.sin(a)))
    return "M%.4f,%.4f " % pts[0] + " ".join("L%.4f,%.4f" % q for q in pts[1:])


def espiral(p):
    """Recursión, trance, vórtice, difusión desde un centro."""
    return f'<path d="{_espiral()}" fill="none" stroke="{p["principal"]}" ' \
           f'stroke-width=".13" stroke-linecap="round"/>'

def anillo(p):
    """Ciclo, contención, comunidad cerrada, órbita."""
    return f'<circle r=".82" fill="none" stroke="{p["principal"]}" stroke-width=".16"/>'

def disco(p):
    """Masa, unidad, cuerpo pleno, el sol."""
    return f'<circle r=".82" fill="{p["principal"]}"/>'

def onda(p):
    """Propagación, sonido, resonancia, aviso."""
    s = ""
    for i, r in enumerate((.34, .58, .82)):
        s += f'<circle r="{r}" fill="none" stroke="{p["principal"]}" ' \
             f'stroke-width=".10" opacity="{1 - i * .22:.2f}"/>'
    return s

def rayos(p, n=12):
    """Revelación, irradiación, euforia, amanecer."""
    s = ""
    for i in range(n):
        a = i * 360 / n
        s += f'<path transform="rotate({a})" d="M0,0 L-.11,-1 L.11,-1 Z" ' \
             f'fill="{p["principal"]}"/>'
    return s

def muro(p, filas=5, cols=4):
    """Barrera, Estado, división, bloque."""
    s = ""
    h = 1.7 / filas
    for f in range(filas):
        y = -.85 + f * h
        off = (f % 2) * .12
        for c in range(cols + 1):
            x = -.9 + c * (1.8 / cols) + off
            if x > .88:
                continue
            w = min(1.8 / cols - .05, .88 - x)
            if w <= 0:
                continue
            s += f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" ' \
                 f'height="{h - .05:.3f}" fill="{p["principal"]}"/>'
    return s

def grieta(p):
    """Ruptura, fractura, quiebre del orden."""
    d = "M-.06,-1 L.10,-.62 L-.12,-.28 L.09,.06 L-.10,.42 L.08,.72 L-.04,1"
    return f'<path d="{d}" fill="none" stroke="{p["acento"]}" stroke-width=".14" ' \
           f'stroke-linejoin="round" stroke-linecap="round"/>'

def multitud(p, filas=4):
    """Colectivo, masa humana, asamblea, el número."""
    s = ""
    for f in range(filas):
        t = f / max(1, filas - 1)
        y = -.15 + t * .85
        r = .045 + t * .045
        n = 7 + f * 2
        for i in range(n):
            x = -.92 + (1.84 / max(1, n - 1)) * i + (.05 if f % 2 else 0)
            if abs(x) > .94:
                continue
            s += f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" ' \
                 f'fill="{p["principal"]}" opacity="{.55 + t * .45:.2f}"/>'
    return s

def figura(p):
    """El individuo, el cuerpo, la persona."""
    return (f'<circle cy="-.42" r=".30" fill="{p["principal"]}"/>'
            f'<path d="M-.42,1 V.05 a.42,.42 0 0 1 .84,0 V1 Z" fill="{p["principal"]}"/>')

def ojo(p):
    """Percepción, consciencia, estado alterado, vigilancia."""
    return (f'<path d="M-.95,0 a.95,.62 0 0 1 1.9,0 a.95,.62 0 0 1 -1.9,0 Z" '
            f'fill="{p["apoyo"]}" stroke="{p["principal"]}" stroke-width=".10"/>'
            f'<circle r=".34" fill="{p["acento"]}"/><circle r=".15" fill="{p["apoyo"]}"/>')

def documento(p):
    """Ley, registro, archivo, norma escrita."""
    s = f'<rect x="-.72" y="-.95" width="1.44" height="1.9" fill="{p["apoyo"]}" ' \
        f'stroke="{p["principal"]}" stroke-width=".08"/>'
    for i in range(5):
        y = -.52 + i * .30
        w = 1.02 if i % 2 == 0 else .74
        s += f'<rect x="-.52" y="{y:.3f}" width="{w:.3f}" height=".09" ' \
             f'fill="{p["principal"]}" opacity=".55"/>'
    return s

def sello(p):
    """Autoridad, veredicto, clausura, marca oficial."""
    return (f'<circle r=".88" fill="none" stroke="{p["acento"]}" stroke-width=".15"/>'
            f'<circle r=".68" fill="none" stroke="{p["acento"]}" stroke-width=".05"/>'
            f'<rect x="-.62" y="-.11" width="1.24" height=".22" fill="{p["acento"]}"/>')

def maquina(p):
    """Aparato, instrumento, tecnología, caja negra."""
    s = f'<rect x="-.95" y="-.68" width="1.9" height="1.36" rx=".12" ' \
        f'fill="{p["apoyo"]}" stroke="{p["principal"]}" stroke-width=".07"/>'
    for i in range(4):
        x = -.62 + i * .41
        s += f'<circle cx="{x:.3f}" cy="-.26" r=".15" fill="{p["principal"]}"/>' \
             f'<rect x="{x - .02:.3f}" y="-.40" width=".04" height=".14" fill="{p["acento"]}"/>'
    for i in range(8):
        x = -.82 + i * .21
        s += f'<rect x="{x:.3f}" y=".22" width=".14" height=".22" rx=".03" ' \
             f'fill="{p["acento"]}" opacity="{.35 + (i % 3) * .3:.2f}"/>'
    return s

def bocina(p):
    """Emisión, sistema de sonido, voz amplificada."""
    return (f'<path d="M-.85,-.34 H-.34 L.20,-.88 V.88 L-.34,.34 H-.85 Z" '
            f'fill="{p["principal"]}"/>'
            f'<path d="M.42,-.42 a.55,.55 0 0 1 0,.84" fill="none" '
            f'stroke="{p["acento"]}" stroke-width=".12" stroke-linecap="round"/>'
            f'<path d="M.66,-.72 a.95,.95 0 0 1 0,1.44" fill="none" '
            f'stroke="{p["acento"]}" stroke-width=".12" stroke-linecap="round"/>')

def red(p):
    """Conexión, escena distribuida, nodos, contagio."""
    nodos = [(0, 0), (-.72, -.52), (.72, -.52), (-.72, .52), (.72, .52), (0, -.88), (0, .88)]
    s = ""
    for x, y in nodos[1:]:
        s += f'<line x1="0" y1="0" x2="{x}" y2="{y}" stroke="{p["principal"]}" ' \
             f'stroke-width=".055" opacity=".7"/>'
    for i, (x, y) in enumerate(nodos):
        r = .19 if i == 0 else .12
        s += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{p["acento"] if i == 0 else p["principal"]}"/>'
    return s

def arcos(p, n=4):
    """Espectro, diversidad, puente, arcoíris."""
    s = ""
    cols = [p["principal"], p["acento"], p["apoyo"], p["principal"]]
    for i in range(n):
        r = .92 - i * .21
        s += f'<path d="M{-r},.62 a{r},{r} 0 0 1 {2 * r},0" fill="none" ' \
             f'stroke="{cols[i % len(cols)]}" stroke-width=".17" stroke-linecap="round"/>'
    return s

def estrella(p):
    """Hito, marca, aparición, señal."""
    return f'<path d="M0,-1 L.26,-.26 L1,0 L.26,.26 L0,1 L-.26,.26 L-1,0 L-.26,-.26 Z" ' \
           f'fill="{p["principal"]}"/>'

def grilla(p, n=7):
    """Control, catastro, mapa del Estado, cuadrícula."""
    s = ""
    for i in range(n):
        v = -.9 + i * (1.8 / (n - 1))
        s += f'<line x1="{v:.3f}" y1="-.9" x2="{v:.3f}" y2=".9" stroke="{p["principal"]}" stroke-width=".035"/>' \
             f'<line x1="-.9" y1="{v:.3f}" x2=".9" y2="{v:.3f}" stroke="{p["principal"]}" stroke-width=".035"/>'
    return s

def corazon(p):
    """Afecto, amor, entrega, cuidado."""
    return f'<path d="M0,.86 C-.62,.38 -.95,.02 -.95,-.36 A.52,.52 0 0 1 0,-.60 ' \
           f'A.52,.52 0 0 1 .95,-.36 C.95,.02 .62,.38 0,.86 Z" fill="{p["principal"]}"/>'

def vinilo(p):
    """Disco, cultura del DJ, el registro sonoro."""
    s = f'<circle r=".92" fill="{p["principal"]}"/>'
    for r in (.72, .58, .44):
        s += f'<circle r="{r}" fill="none" stroke="{p["apoyo"]}" stroke-width=".03" opacity=".5"/>'
    s += f'<circle r=".22" fill="{p["acento"]}"/><circle r=".05" fill="{p["apoyo"]}"/>'
    return s

def puerta(p):
    """Umbral, acceso, entrada al espacio, el club."""
    return (f'<path d="M-.78,.92 V-.10 a.78,.78 0 0 1 1.56,0 V.92 Z" fill="none" '
            f'stroke="{p["principal"]}" stroke-width=".14"/>'
            f'<path d="M-.30,.92 V.18 a.30,.30 0 0 1 .60,0 V.92 Z" fill="{p["acento"]}"/>')

def horizonte(p):
    """Campo abierto, paisaje, afueras, el lugar remoto."""
    return (f'<path d="M-1,.9 C-.6,.35 -.3,.62 0,.42 C.35,.2 .65,.55 1,.32 V1 H-1 Z" '
            f'fill="{p["principal"]}"/>'
            f'<path d="M-1,1 H1" stroke="{p["acento"]}" stroke-width=".06"/>')


FIGURAS = {
    "espiral": (espiral, "recursión, trance, vórtice, difusión"),
    "anillo": (anillo, "ciclo, contención, comunidad cerrada"),
    "disco": (disco, "masa, unidad, cuerpo pleno, sol"),
    "onda": (onda, "propagación, sonido, resonancia"),
    "rayos": (rayos, "revelación, irradiación, euforia"),
    "muro": (muro, "barrera, Estado, división"),
    "grieta": (grieta, "ruptura, fractura, quiebre"),
    "multitud": (multitud, "colectivo, masa humana, el número"),
    "figura": (figura, "el individuo, el cuerpo"),
    "ojo": (ojo, "percepción, consciencia alterada"),
    "documento": (documento, "ley, registro, norma escrita"),
    "sello": (sello, "autoridad, veredicto, clausura"),
    "maquina": (maquina, "aparato, instrumento, tecnología"),
    "bocina": (bocina, "emisión, sound system, voz amplificada"),
    "red": (red, "conexión, escena distribuida, contagio"),
    "arcos": (arcos, "espectro, diversidad, puente"),
    "estrella": (estrella, "hito, marca, aparición"),
    "grilla": (grilla, "control, catastro, mapa del Estado"),
    "corazon": (corazon, "afecto, amor, cuidado"),
    "vinilo": (vinilo, "disco, cultura del DJ"),
    "puerta": (puerta, "umbral, acceso, el club"),
    "horizonte": (horizonte, "campo abierto, afueras, lo remoto"),
}

# -------------------------------------------------------------------------
#  GESTOS — animaciones. Todas garantizan visibilidad en el frame 0.
#  (css_template, descripción). {c}=clase  {d}=duración
# -------------------------------------------------------------------------
GESTOS = {
    "latir": (""".{c}{{animation:k_latir {d} ease-in-out infinite}}
@keyframes k_latir{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.09)}}}}""",
        "pulso vital, corazón, insistencia"),

    "girar": (""".{c}{{animation:k_girar {d} linear infinite}}
@keyframes k_girar{{to{{transform:rotate(360deg)}}}}""",
        "rotación continua, máquina, hipnosis"),

    "girar_inverso": (""".{c}{{animation:k_girari {d} linear infinite}}
@keyframes k_girari{{to{{transform:rotate(-360deg)}}}}""",
        "contrarrotación, engranaje opuesto"),

    "emanar": (""".{c}{{animation:k_emanar {d} ease-out infinite}}
@keyframes k_emanar{{0%{{transform:scale(.72);opacity:1}}100%{{transform:scale(1.35);opacity:0}}}}""",
        "expansión hacia afuera, difusión, sonido"),

    "oscilar": (""".{c}{{animation:k_oscilar {d} ease-in-out infinite}}
@keyframes k_oscilar{{0%,100%{{transform:rotate(-6deg)}}50%{{transform:rotate(6deg)}}}}""",
        "vaivén, duda, danza suave"),

    "saltar": (""".{c}{{animation:k_saltar {d} ease-in-out infinite}}
@keyframes k_saltar{{0%,100%{{transform:translateY(0)}}45%{{transform:translateY(-4px)}}}}""",
        "rebote, baile, energía"),

    "derivar": (""".{c}{{animation:k_derivar {d} ease-in-out infinite}}
@keyframes k_derivar{{0%,100%{{transform:translateY(2px)}}50%{{transform:translateY(-3px)}}}}""",
        "flotación lenta, ingravidez"),

    "aparecer_ciclico": (""".{c}{{animation:k_aparecer {d} ease-in-out infinite}}
@keyframes k_aparecer{{0%,55%{{opacity:1;transform:scale(1)}}80%{{opacity:.12;transform:scale(1.1)}}100%{{opacity:1;transform:scale(1)}}}}""",
        "presencia intermitente, TAZ, lo efímero"),

    "desplazar_fuera": (""".{c}{{animation:k_desplazar {d} ease-in-out infinite}}
@keyframes k_desplazar{{0%,18%{{transform:translateX(0)}}62%,100%{{transform:translateX({dx}px)}}}}""",
        "apertura, quiebre en dos, exilio"),

    "temblar": (""".{c}{{animation:k_temblar {d} steps(1) infinite}}
@keyframes k_temblar{{0%,88%{{transform:translate(0,0)}}91%{{transform:translate(-2px,1px)}}
94%{{transform:translate(2px,-1px)}}97%{{transform:translate(-1px,0)}}}}""",
        "glitch, inestabilidad, señal fallando"),

    "respirar": (""".{c}{{animation:k_respirar {d} ease-in-out infinite}}
@keyframes k_respirar{{0%,100%{{opacity:.72}}50%{{opacity:1}}}}""",
        "brillo suave, latencia, permanencia"),

    "quieto": ("", "sin movimiento, base estable"),
}

# -------------------------------------------------------------------------
#  TONOS — paletas verificadas. Contraste comprobado por el compilador.
# -------------------------------------------------------------------------
TONOS = {
    "acido":      {"fondo": "#12120a", "principal": "#d7ff2e", "acento": "#ff2e7e",
                   "apoyo": "#1e2410", "tinta": "#f4ffd9"},
    "subterraneo":{"fondo": "#0d0d18", "principal": "#f2f2f5", "acento": "#ff3b30",
                   "apoyo": "#22222e", "tinta": "#f2f2f5"},
    "vitral":     {"fondo": "#150c22", "principal": "#ffb02e", "acento": "#2ee6ff",
                   "apoyo": "#2a1740", "tinta": "#ffeccc"},
    "blueprint":  {"fondo": "#061826", "principal": "#2ee6ff", "acento": "#d7ff2e",
                   "apoyo": "#0d2c42", "tinta": "#cdefff"},
    "documento":  {"fondo": "#e9e5da", "principal": "#1a1a20", "acento": "#c0392b",
                   "apoyo": "#fbf9f3", "tinta": "#1a1a20"},
    "papel":      {"fondo": "#f4f1e8", "principal": "#1f2430", "acento": "#ff6b2c",
                   "apoyo": "#ffffff", "tinta": "#1f2430"},
    "atardecer":  {"fondo": "#2b1055", "principal": "#ffe259", "acento": "#ff5f6d",
                   "apoyo": "#4a1c6e", "tinta": "#ffeccc"},
    "concreto":   {"fondo": "#15151a", "principal": "#8d8d9c", "acento": "#ff3b30",
                   "apoyo": "#26262e", "tinta": "#e6e6ee"},
    "campo":      {"fondo": "#0b1030", "principal": "#8fe0b0", "acento": "#d7ff2e",
                   "apoyo": "#132a1c", "tinta": "#e8fff2"},
}

# -------------------------------------------------------------------------
#  COMPOSICIONES — dónde va cada rol. El autor NUNCA da coordenadas.
#  rol -> (cx, cy, escala)   en el lienzo 120x120
# -------------------------------------------------------------------------
COMPOSICIONES = {
    "centro_unico": {
        "protagonista": (60, 58, 40),
        "marca":        (60, 104, 12),
        "base":         (60, 96, 46),
    },
    "centro_y_satelites": {
        "protagonista": (60, 56, 30),
        "satelite_1":   (24, 30, 13), "satelite_2": (96, 30, 13),
        "satelite_3":   (24, 86, 13), "satelite_4": (96, 86, 13),
        "marca":        (60, 110, 10),
    },
    "protagonista_y_flancos": {
        "protagonista": (60, 54, 34),
        "flanco_izq":   (18, 60, 15), "flanco_der": (102, 60, 15),
        "base":         (60, 98, 44),
    },
    "horizonte": {
        "cielo":        (60, 38, 30),
        "protagonista": (60, 42, 20),
        "base":         (60, 84, 34),
        "marca":        (60, 112, 10),
    },
    "confrontacion": {
        "lado_izq":     (27, 58, 19), "lado_der": (93, 58, 19),
        "protagonista": (60, 58, 22),
        "base":         (60, 104, 46),
    },
    "capas": {
        "fondo_amplio": (60, 56, 46),
        "protagonista": (60, 56, 30),
        "detalle":      (60, 56, 12),
        "marca":        (60, 110, 10),
    },
}

ROLES = sorted({r for c in COMPOSICIONES.values() for r in c})
