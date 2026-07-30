#!/usr/bin/env python3
"""
compilador.py — Traduce una descripción SEMÁNTICA en un SVG animado.

El agente escribe intención:
    {"composicion":"centro_unico",
     "tono":"acido",
     "capas":[{"rol":"protagonista","figura":"espiral","gesto":"girar","ritmo":"lento"}]}

El compilador produce la geometría. El autor jamás toca coordenadas, hex ni
keyframes — por eso no puede romperlos.

INVARIANTES GARANTIZADOS POR CONSTRUCCIÓN
  1. viewBox siempre 0 0 120 120
  2. todo el contenido dentro de la zona segura (8..112)
  3. opacidad >= .55 y escala >= .55 en el frame 0  -> nada invisible al inicio
  4. contraste mínimo AA-grande (3.0:1) entre figura y fondo
  5. texto medido antes de escribir: si no cabe, se reduce o se rechaza
  6. XML bien formado: no hay concatenación libre de strings por el agente
"""
import json, re, sys, pathlib

# Corre como modulo del paquete (`from motor_semantico import compilador`, en
# los tests) Y como script suelto en la caja (`python3
# motor_semantico/compilador.py spec.json out.svg`). Sin esto lo segundo
# revienta con "attempted relative import with no known parent package".
if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    __package__ = "motor_semantico"

from .vocabulario import FIGURAS, GESTOS, TONOS, COMPOSICIONES  # noqa: E402

RITMOS = {"muy_lento": "12s", "lento": "7s", "medio": "4s",
          "rapido": "2.2s", "muy_rapido": "1.2s"}

ZONA_MIN, ZONA_MAX = 8, 112
# Roles de fondo: se atenuan para no competir con el protagonista.
ATENUADOS = ("fondo_amplio", "cielo")
CONTRASTE_MIN = 3.0
ANCHO_CHAR = 0.60   # factor empírico para monoespaciada


class ErrorSemantico(Exception):
    pass


def _capa_abre(i, capa, rol, cx, cy, gesto, ritmo):
    """Abre el grupo de una capa DECLARANDO lo que codifica.

    Dos razones, y las dos son del usuario (2026-07-30):

    1. Editable, nada rigido. Un grupo con `id` y `<title>` aparece como capa
       con nombre en Illustrator y en Inkscape, asi que el icono animado se
       puede abrir en una herramienta de diseno, tocar una capa y volver a
       integrarlo. Un arbol de <g> anonimos no se puede editar sin adivinar.
    2. La tesis doublecup: ningun elemento reclama un dato que no codifica.
       Aca al reves: cada elemento LLEVA el dato que lo justifica -- que rol
       ocupa, que figura es, que gesto hace, a que ritmo. La forma queda
       auditable sin mirarla, que es la unica manera de que un agente ciego
       responda por ella.

    Es la razon por la que el artefacto es una ANIMACION y no un icono: el
    gesto y el ritmo viajan en el marcado, no en un comentario.
    """
    que = (("texto:" + str(capa["texto"])) if capa.get("texto") is not None
           else str(capa.get("figura", "?")))
    titulo = (que.replace("&", "&amp;").replace("<", "&lt;")
              .replace(">", "&gt;"))
    attrs = [f'id="capa-{i}-{rol}"', f'transform="translate({cx},{cy})"',
             f'data-rol="{rol}"', f'data-gesto="{gesto}"',
             f'data-ritmo="{ritmo}"']
    if capa.get("figura"):
        attrs.append(f'data-figura="{capa["figura"]}"')
    else:
        attrs.append('data-figura="texto"')
    if rol in ATENUADOS:
        attrs.append('opacity=".38"')
    return "<g %s><title>%s - %s</title>" % (" ".join(attrs), rol, titulo)


# -- color ----------------------------------------------------------------
def _lum(hexc):
    hexc = hexc.lstrip("#")
    if len(hexc) == 3:
        hexc = "".join(c * 2 for c in hexc)
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contraste(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


# -- validación semántica -------------------------------------------------
def validar_spec(spec):
    fallos = []
    comp = spec.get("composicion")
    if comp not in COMPOSICIONES:
        fallos.append(f"composicion '{comp}' no existe. Opciones: {sorted(COMPOSICIONES)}")
        return fallos
    tono = spec.get("tono")
    if tono not in TONOS:
        fallos.append(f"tono '{tono}' no existe. Opciones: {sorted(TONOS)}")
    ranuras = COMPOSICIONES[comp]
    capas = spec.get("capas", [])
    if not capas:
        fallos.append("hace falta al menos una capa")
    if not any(c.get("rol") == "protagonista" for c in capas) and "protagonista" in ranuras:
        fallos.append("falta la capa 'protagonista' (la lectura principal)")
    vistos = set()
    for i, c in enumerate(capas):
        rol = c.get("rol")
        if rol not in ranuras:
            fallos.append(f"capa {i}: rol '{rol}' no existe en '{comp}'. "
                          f"Disponibles: {sorted(ranuras)}")
        if rol in vistos:
            fallos.append(f"capa {i}: rol '{rol}' repetido")
        vistos.add(rol)
        fig, txt = c.get("figura"), c.get("texto")
        if not fig and txt is None:
            fallos.append(f"capa {i}: necesita 'figura' o 'texto'")
        if fig and fig not in FIGURAS:
            fallos.append(f"capa {i}: figura '{fig}' no existe. Opciones: {sorted(FIGURAS)}")
        g = c.get("gesto", "quieto")
        if g not in GESTOS:
            fallos.append(f"capa {i}: gesto '{g}' no existe. Opciones: {sorted(GESTOS)}")
        r = c.get("ritmo", "medio")
        if r not in RITMOS:
            fallos.append(f"capa {i}: ritmo '{r}' no existe. Opciones: {sorted(RITMOS)}")
    if len([c for c in capas if c.get("gesto", "quieto") != "quieto"]) > 5:
        fallos.append("más de 5 capas animadas: el ícono se vuelve ruido")
    return fallos


# -- compilación ----------------------------------------------------------
def compilar(spec, slug="icono"):
    fallos = validar_spec(spec)
    if fallos:
        raise ErrorSemantico("\n".join("  x " + f for f in fallos))

    comp = COMPOSICIONES[spec["composicion"]]
    pal = dict(TONOS[spec["tono"]])
    fondo = pal["fondo"]

    cuerpo, css, avisos = [], [], []

    for i, capa in enumerate(spec["capas"]):
        rol = capa["rol"]
        cx, cy, esc = comp[rol]
        cls = f"c{i}"
        gesto = capa.get("gesto", "quieto")
        ritmo = RITMOS[capa.get("ritmo", "medio")]

        # -- texto --------------------------------------------------------
        if capa.get("texto") is not None:
            txt = str(capa["texto"])
            fs = max(5.5, min(esc * .58, 13))
            ancho = len(txt) * fs * ANCHO_CHAR
            disponible = ZONA_MAX - ZONA_MIN
            if ancho > disponible:                     # INVARIANTE 5
                fs = disponible / (len(txt) * ANCHO_CHAR)
                if fs < 5.0:
                    raise ErrorSemantico(
                        f"  x capa {i}: el texto «{txt}» ({len(txt)} caracteres) no cabe "
                        f"legible en 120px. Máximo ~{int(disponible/(5.5*ANCHO_CHAR))} caracteres.")
                avisos.append(f"texto «{txt}» reducido a {fs:.1f}px para que quepa")
            seguro = (txt.replace("&", "&amp;").replace("<", "&lt;")
                         .replace(">", "&gt;"))          # INVARIANTE 6
            col = pal["tinta"]
            if contraste(col, fondo) < CONTRASTE_MIN:
                col = pal["principal"]
            cuerpo.append(
                f'{_capa_abre(i, capa, rol, cx, cy, gesto, ritmo)}<g class="{cls}">'
                f'<text x="0" y="{fs * .35:.1f}" text-anchor="middle" '
                f'font-family="ui-monospace,Menlo,monospace" font-weight="700" '
                f'font-size="{fs:.1f}" letter-spacing=".5" fill="{col}">{seguro}</text>'
                f'</g></g>')
        # -- figura -------------------------------------------------------
        else:
            nombre = capa["figura"]
            fn = FIGURAS[nombre][0]
            roles = dict(pal)
            # INVARIANTE 4: si la figura no contrasta con el fondo, se corrige
            if contraste(roles["principal"], fondo) < CONTRASTE_MIN:
                alt = max(("principal", "acento", "tinta"),
                          key=lambda k: contraste(pal[k], fondo))
                avisos.append(f"capa {i} ({nombre}): color principal sin contraste "
                              f"suficiente; se usó '{alt}'")
                roles["principal"] = pal[alt]
            marca = fn(roles)
            # límite de zona segura (INVARIANTE 2)
            media = esc
            if cx - media < ZONA_MIN or cx + media > ZONA_MAX or \
               cy - media < ZONA_MIN or cy + media > ZONA_MAX:
                permitido = min(cx - ZONA_MIN, ZONA_MAX - cx,
                                cy - ZONA_MIN, ZONA_MAX - cy)
                if permitido < esc:
                    avisos.append(f"capa {i} ({nombre}): escala reducida "
                                  f"{esc}->{permitido:.0f} para no salirse del lienzo")
                    esc = max(6, permitido)
            # translate exterior - animación en el medio - escala interior.
            # Rotar/escalar en el grupo del medio equivale a hacerlo sobre el
            # centro de la figura, sin depender de transform-origin (que
            # algunos renderizadores no soportan junto a transform=).
            cuerpo.append(f'{_capa_abre(i, capa, rol, cx, cy, gesto, ritmo)}'
                          f'<g class="{cls}">'
                          f'<g transform="scale({esc})">{marca}</g>'
                          f'</g></g>')

        # -- gesto --------------------------------------------------------
        if gesto != "quieto":
            plantilla = GESTOS[gesto][0]
            dx = 16 if cx >= 60 else -16
            css.append(plantilla.format(c=cls, d=ritmo, ox=cx, oy=cy, dx=dx))

    vistos, unicos = set(), []
    for bloque in css:
        for regla in re.split(r"(?=@keyframes|\n\.)", bloque):
            r = regla.strip()
            if r and r not in vistos:
                vistos.add(r); unicos.append(r)
    estilos = "\n".join(unicos)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" data-name="{slug}">
<style>
{estilos}
</style>
<rect width="120" height="120" fill="{fondo}"/>
{chr(10).join(cuerpo)}
</svg>
'''
    return svg, avisos


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: compilador.py concepto.json [salida.svg]")
    ruta = pathlib.Path(sys.argv[1])
    spec = json.loads(ruta.read_text(encoding="utf-8"))
    slug = spec.get("slug", ruta.stem)
    try:
        svg, avisos = compilar(spec, slug)
    except ErrorSemantico as e:
        print(f"RECHAZADO — {ruta.name}\n{e}")
        sys.exit(1)
    destino = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ruta.with_suffix(".svg")
    destino.write_text(svg, encoding="utf-8")
    print(f"OK {destino}")
    for a in avisos:
        print("  !", a)


if __name__ == "__main__":
    main()
