#!/usr/bin/env python3
"""
rasterizador.py — SVG a PNG, con dos backends y sin matar al interprete.

Por que existe: el critico perceptual y el exportador necesitan pixeles, y la
maquina no siempre tiene el mismo rasterizador. Medido el 2026-07-30:

  - Windows del usuario: `import cairosvg` levanta OSError (falta
    libcairo-2.dll). Es el mismo hueco por el que el resto del repo exporta
    con Edge headless (`tools/svg/svg_to_pdf.py`).
  - Caja MAK (Linux): cairosvg puede estar o no; Edge probablemente no.

Asi que ninguno de los dos se asume. `backend_disponible()` dice cual hay y
`rasterizar()` levanta `RasterizadorNoDisponibleError` si no hay ninguno --
nunca `sys.exit()` (la version original del critico salia del interprete al
importarse, lo que lo volvia inimportable y por lo tanto no testeable) y nunca
un `except: pass` que devuelva un PNG en blanco.

AVISO MEDIDO, no lo toques a la ligera: cairosvg BLANQUEA un elemento cuando
un `transform-origin` de CSS se junta con un `transform=` como atributo. El
navegador lo dibuja bien. El compilador ya esquiva eso con grupos anidados
(translate exterior / clase animada / scale interior), pero si algun dia los
dos backends discrepan, el navegador es el destino real y gana el navegador:
un QA que discrepa del destino produce falsos negativos catastroficos.

USO:
    py -m motor_semantico.rasterizador entrada.svg salida.png [tam]
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

TAM = 256

# Navegadores: los mismos candidatos de Edge que tools/svg/svg_to_pdf.py, mas
# Chrome/Chromium, que es lo que hay en un runner de Linux y en la caja. Se
# prueba por ejecucion, no por existencia.
NAVEGADOR_CANDS = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


# Las banderas del navegador NO se eligen por sistema operativo: se PRUEBAN.
# Tres vueltas de matriz roja el 2026-07-30 ensenaron por que.
#
#   --no-sandbox            Linux/CI: imprescindible (contenedor sin user
#                           namespaces). Windows: VENENO -- devuelve un PNG
#                           valido y EN BLANCO de 291 bytes donde el icono rinde
#                           3673, y nadie lo nota hasta que todos los cuadros
#                           salen iguales y el guardian acusa al archivo.
#   --disable-dev-shm-usage inofensiva en los dos (3673 B con y sin ella).
#   --virtual-time-budget   no captura antes de que la pagina pinte.
#
# Elegirlas por `os.name` parecia suficiente y no lo era: en ubuntu el
# navegador arrancaba, animaba una sonda de 8x8 y dibujaba las piezas reales en
# blanco igual. Un perfil que sirve en una maquina puede estar ciego en otra, y
# eso no se deduce -- se mide. Asi que se prueban en orden y gana el primero que
# DIBUJA Y MUEVE una pieza representativa. El primero de la lista es el que ya
# funcionaba en Windows, para no arriesgar lo que estaba sano.
# Solo se abre un HTML local generado aca, nunca contenido remoto.
_BASE = ["--disable-gpu", "--no-first-run"]
_PERFILES = [
    ["--headless=new", "--disable-dev-shm-usage"],
    ["--headless=new", "--disable-dev-shm-usage", "--no-sandbox"],
    ["--headless=new", "--disable-dev-shm-usage", "--no-sandbox",
     "--virtual-time-budget=1000"],
    ["--headless", "--disable-dev-shm-usage", "--no-sandbox"],
]
# Nada de `--headless=old`: Chromium 141 contesta "Old Headless mode has been
# removed from the Chrome binary". Serian entradas muertas que solo alargan
# cada sondeo.

# LA CAUSA, medida en Linux con Chromium 141 el 2026-07-30 variando SOLO el
# tamano (mismo icono, mismas banderas): 8 px -> 119 B y 2 colores, 96 px ->
# 291 B y 2 colores, 110 px -> 617 B, 120 px -> 962 B, 256 px -> 9081 B. Y la
# prueba que lo aisla: con --window-size=256 el MISMO render a 8 px da 985 B y
# 47 colores.
#
# El headless nuevo impone una ventana minima (~100 px). Pedir
# --window-size=96,96 recorta la ventana al minimo pero captura al tamano
# pedido, desde un viewport que nunca pinto: de ahi el PNG valido y VACIO. En
# Windows el minimo es otro, y por eso ahi el mismo icono daba 3673 B.
#
# La ventana no es el tamano de salida: es el lienzo. Se pide grande y se
# RECORTA -- nunca se reescala, porque no se resamplea lo que se va a medir.
VENTANA_MIN = 256


class RasterizadorNoDisponibleError(RuntimeError):
    """No hay backend de rasterizado en esta maquina."""


class BackendNoAnimaError(RasterizadorNoDisponibleError):
    """Hay con que rasterizar, pero no con que MEDIR movimiento.

    Existe porque el 2026-07-30 la matriz de CI se puso roja acusando a los 16
    iconos de estar quietos: en ubuntu el backend era cairosvg, que rasteriza
    perfecto y NO ejecuta animaciones CSS. Los cuadros salian identicos, y el
    llamador leia ese 1 como "el archivo miente" cuando decia "no lo medi".

    Un instrumento incapaz tiene que decir que no puede, nunca devolver un
    numero que se parece a un veredicto. Es la misma leccion que
    `_navegador_funciona()` -- existir no es funcionar -- un nivel mas adentro:
    funcionar para una cosa no es funcionar para la otra.
    """


class BackendNoDibujaError(BackendNoAnimaError):
    """Pasa la sonda y no dibuja ESTA pieza: devuelve un cuadro liso.

    Medido en ubuntu el 2026-07-30: un navegador que animaba la sonda entregaba
    los iconos reales en 291 bytes -- un PNG valido y vacio, donde Windows daba
    3673. Todos los cuadros salian iguales entre si y el guardian lo leia como
    "el archivo afirma un movimiento que no ocurre". Un lienzo liso no es una
    medicion del icono: es una medicion del vacio.
    """


def _adelantar(svg_txt, avance_ms):
    """Adelanta TODAS las animaciones del SVG con un delay negativo.

    Se hace con una regla global inyectada en el propio documento y no
    reescribiendo cada declaracion. La version anterior reemplazaba la palabra
    `infinite` por `infinite;animation-delay:-Xms`, y eso rompia toda regla con
    la forma `animation: nombre 11s ease-in-out infinite alternate`: el
    `alternate` quedaba colgando despues del delay y el navegador DESCARTABA la
    declaracion entera. Resultado medido el 2026-07-30: un icono que si se
    animaba salia con los cuatro cuadros identicos y el test lo acusaba de
    afirmar un movimiento inexistente. El defecto era del instrumento.

    `!important` y `*` porque el objetivo es medir, no respetar cascada.
    """
    regla = "<style>*{animation-delay:-%dms !important}</style>" % avance_ms
    i = svg_txt.find(">", svg_txt.find("<svg"))
    if i < 0:
        return svg_txt
    return svg_txt[:i + 1] + regla + svg_txt[i + 1:]


def _cairosvg():
    """El modulo cairosvg si es usable, o None. OJO: no basta con ImportError
    -- cairosvg encuentra el paquete y revienta con OSError al no encontrar la
    DLL de cairo, que es exactamente lo que pasa en el Windows del usuario."""
    try:
        import cairosvg
        return cairosvg
    except Exception:
        return None


def _binarios():
    """TODOS los navegadores presentes, en orden de preferencia.

    Devolver solo el primero fue el ultimo disfraz del mismo error: en el
    runner de ubuntu el primero es /usr/bin/microsoft-edge, medido como
    incapaz, y /usr/bin/google-chrome no se probaba nunca -- 17 guardias
    saltados por un binario mal elegido, no por una plataforma incapaz.
    Existir no es funcionar, tambien para el binario.

    En Windows Edge va primero, que es lo que ya estaba sano.
    """
    orden = list(NAVEGADOR_CANDS)
    hallados = [c for c in orden if os.path.exists(c)]
    for nombre in ("google-chrome", "chromium"):
        ruta = shutil.which(nombre)
        if ruta and ruta not in hallados:
            hallados.append(ruta)
    return hallados


def _edge():
    """El primer navegador presente, o None. Conserva el nombre historico
    porque es el punto que los tests intervienen para fingir su ausencia."""
    hallados = _binarios()
    return hallados[0] if hallados else None


_navegador = _edge  # nombre honesto; ya no es necesariamente Edge

_SONDA = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'>" \
         "<rect width='8' height='8' fill='#f00'/></svg>"

# Sonda de ANIMACION. Fue un cuadrado de 8x8 y ese tamano la volvio inutil: en
# ubuntu la pasaba un navegador que dibujaba las piezas reales EN BLANCO. Una
# sonda que no se parece al trabajo no prueba nada sobre el trabajo.
# Ahora tiene lo que tiene un icono -- varias formas, varios colores, un
# translate y un cambio de color a lo largo de 1000 ms -- y se mide a 96 px,
# el tamano al que se juzga de verdad.
_SONDA_ANIMA = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<style>@keyframes p{from{fill:#0a0a0a}to{fill:#f0f0f0}}"
    "@keyframes m{from{transform:translateX(-18px)}"
    "to{transform:translateX(18px)}}"
    ".a{animation:p 1000ms linear infinite}"
    ".b{animation:m 1000ms linear infinite}</style>"
    "<rect width='100' height='100' fill='#3355cc'/>"
    "<circle class='a' cx='50' cy='34' r='22' fill='#0a0a0a'/>"
    "<rect class='b' x='30' y='68' width='40' height='14' fill='#ee2244'/>"
    "</svg>")
_TAM_SONDA = 96

#  identidad del backend -> si rasteriza / si anima. Indexado por identidad y
#  no un solo booleano a proposito: asi el resultado no sobrevive a que cambie
#  el binario encontrado (un test que finge "no hay navegador" tiene que ver
#  "no hay navegador", no la sonda vieja).
_SONDEADOS = {}
_ANIMADORES = {}


def _edge_funciona():
    """Si el navegador que encontramos DE VERDAD produce un PNG. Se sondea una
    vez por binario y se recuerda.

    Existir no es funcionar, y medirlo costo un CI rojo (2026-07-30): el runner
    de ubuntu TIENE `/usr/bin/microsoft-edge` y no rasteriza. Con la deteccion
    por existencia, `backend_disponible()` decia "edge", los tests no se
    saltaban y el fallo aparecia en medio de un analisis en vez de al
    preguntar. Un backend que existe y no sirve es peor que uno ausente:
    convierte una capacidad faltante en un error tardio.
    """
    binario = _edge()
    if not binario:
        return False
    if binario not in _SONDEADOS:
        try:
            # Cualquier motivo -- binario roto, sin sandbox, sin HOME -- cuenta
            # como "no sirve". No se distingue porque no cambia la decision: no
            # hay con que rasterizar.
            _SONDEADOS[binario] = _elegir_navegador(anima=False) is not None
        except Exception:
            _SONDEADOS[binario] = False
    return _SONDEADOS[binario]


def _dibujo_vivo(png):
    """Si ESE PNG contiene una pieza dibujada, y no un cuadro liso.

    Es el criterio que faltaba. Un PNG valido y en blanco pasa cualquier
    chequeo de formato, y despues todos los cuadros del ciclo salen iguales
    entre si -- indistinguible de un icono muerto. Un dibujo real tiene mas de
    dos colores; un lienzo vacio tiene uno.

    Sin Pillow se cae a un piso de bytes: un PNG liso de 96 px pesa ~300 B.
    """
    if not png or png[:4] != b"\x89PNG":
        return False
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(png)).convert("RGB")
        colores = im.getcolors(maxcolors=64)
        return colores is None or len(colores) > 2
    except Exception:
        return len(png) > 800


# Los colores que la sonda PONE en el lienzo. Es el criterio exacto: un
# instrumento que sirve me devuelve las formas que le di. "Mas de dos colores"
# no alcanzaba -- en ubuntu un fondo con antialias pasaba ese liston mientras
# las figuras no se dibujaban, y cuatro iconos con fondo de dos tonos seguian
# acusados de no moverse.
_COLORES_SONDA = ((0x33, 0x55, 0xcc), (0xee, 0x22, 0x44))


# CairoSVG does not execute CSS animations. MAK still needs a Linux-only,
# deterministic validation path when browser execution is forbidden, so this
# adapter evaluates the small CSS animation vocabulary emitted by the semantic
# compiler and hands each static frame back to CairoSVG. It is intentionally a
# validator for compiler output, not a general CSS engine.
_CSS_ANIMATION_BACKEND = "cairosvg-css-animation"
_SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", _SVG_NS)


def _balanced_css_blocks(css, marker="@keyframes"):
    """Return (name, body) blocks for a CSS at-rule with balanced braces."""
    found = []
    for match in re.finditer(r"%s\s+([\w-]+)\s*\{" % re.escape(marker), css):
        depth = 1
        pos = match.end()
        while pos < len(css) and depth:
            if css[pos] == "{":
                depth += 1
            elif css[pos] == "}":
                depth -= 1
            pos += 1
        if depth == 0:
            found.append((match.group(1), css[match.end():pos - 1]))
    return found


def _css_properties(text):
    return {name.strip(): value.strip()
            for name, value in re.findall(r"([\w-]+)\s*:\s*([^;]+)", text)}


def _css_rules(css):
    """Parse flat rules after removing keyframe blocks."""
    plain = css
    for match in re.finditer(r"@keyframes\s+[\w-]+\s*\{", css):
        depth = 1
        pos = match.end()
        while pos < len(css) and depth:
            if css[pos] == "{":
                depth += 1
            elif css[pos] == "}":
                depth -= 1
            pos += 1
        if depth == 0:
            plain = plain.replace(css[match.start():pos], "")
    return [(selector.strip(), _css_properties(body))
            for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", plain)
            if selector.strip()]


def _resolve_css_vars(value, variables):
    for _ in range(8):
        changed = False

        def replace(match):
            nonlocal changed
            key = match.group(1)
            fallback = match.group(2)
            if key in variables:
                changed = True
                return variables[key]
            if fallback is not None:
                changed = True
                return fallback.strip()
            return match.group(0)

        new_value = re.sub(r"var\((--[\w-]+)(?:\s*,\s*([^)]*))?\)",
                           replace, value)
        value = new_value
        if not changed:
            break
    return value


def _parse_css_time(value, default=0.0):
    match = re.search(r"(-?[\d.]+)\s*(ms|s)?", value or "")
    if not match:
        return default
    number = float(match.group(1))
    return number * (1000.0 if match.group(2) == "s" else 1.0)


def _parse_keyframes(css):
    result = {}
    for name, body in _balanced_css_blocks(css):
        stops = []
        for selector, declarations in re.findall(r"([^{}]+)\{([^{}]*)\}", body):
            props = _css_properties(declarations)
            for token in selector.split(","):
                token = token.strip().lower()
                if token == "from":
                    position = 0.0
                elif token == "to":
                    position = 1.0
                else:
                    try:
                        position = float(token.rstrip("%")) / 100.0
                    except ValueError:
                        continue
                stops.append((position, props))
        if stops:
            result[name] = sorted(stops, key=lambda item: item[0])
    return result


def _css_class_names(selector):
    return re.findall(r"\.([\w-]+)", selector)


def _neutral_transform(value):
    """Build the identity form of a transform function sequence."""
    pattern = r"([A-Za-z][\w-]*)\(([^)]*)\)"

    def replace(match):
        name = match.group(1)
        neutral = "1" if name.lower().startswith("scale") else "0"
        args = re.sub(r"-?(?:\d+(?:\.\d+)?|\.\d+)([A-Za-z%]*)",
                      lambda number: neutral + number.group(1),
                      match.group(2))
        return "%s(%s)" % (name, args)

    return re.sub(pattern, replace, value) or "none"


def _css_transform_to_svg(value):
    """Convert the CSS transform forms emitted by the compiler to SVG syntax."""
    value = re.sub(r"translateX\(([^)]*)\)",
                   lambda match: "translate(%s,0)" % match.group(1), value)
    value = re.sub(r"translateY\(([^)]*)\)",
                   lambda match: "translate(0,%s)" % match.group(1), value)
    value = re.sub(r"rotate\(([-+]?\d+(?:\.\d+)?|[-+]?\.\d+)deg\)",
                   lambda match: "rotate(%s)" % match.group(1), value)
    return value


def _lerp_css_value(left, right, amount):
    """Interpolate common numeric SVG values, preserving CSS function shape."""
    if left.strip() == "none" and right.strip() != "none":
        left = _neutral_transform(right)
    left_hex = re.fullmatch(r"#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6,8})", left.strip())
    right_hex = re.fullmatch(r"#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6,8})", right.strip())
    if left_hex and right_hex and len(left_hex.group(1)) == len(right_hex.group(1)):
        digits = left_hex.group(1)
        other = right_hex.group(1)
        if len(digits) in (3, 4):
            digits = "".join(char * 2 for char in digits)
            other = "".join(char * 2 for char in other)
            short = True
        else:
            short = False
        channels = [round(int(digits[index:index + 2], 16)
                          + (int(other[index:index + 2], 16)
                             - int(digits[index:index + 2], 16)) * amount)
                    for index in range(0, len(digits), 2)]
        value = "#" + "".join("%02x" % channel for channel in channels)
        if short:
            value = "#" + "".join(value[index] for index in range(1, 8, 2))
        return value
    number = r"-?(?:\d+(?:\.\d+)?|\.\d+)"
    left_numbers = [float(x) for x in re.findall(number, left)]
    right_numbers = [float(x) for x in re.findall(number, right)]
    if len(left_numbers) != len(right_numbers) or not left_numbers:
        return left if amount < 0.5 else right
    index = 0

    def replace(_match):
        nonlocal index
        value = left_numbers[index] + (right_numbers[index] - left_numbers[index]) * amount
        index += 1
        return "%.6g" % value

    return re.sub(number, replace, left)


def _default_css_value(property_name):
    """Return a neutral value for a property omitted at a keyframe edge."""
    return {"transform": "none", "opacity": "1"}.get(property_name, "")


def _frame_properties(stops, progress):
    if not stops:
        return {}
    effective = list(stops)
    if effective[0][0] > 0:
        effective.insert(0, (0.0, {}))
    if effective[-1][0] < 1:
        effective.append((1.0, {}))
    if progress <= effective[0][0]:
        return dict(effective[0][1])
    if progress >= effective[-1][0]:
        return dict(effective[-1][1])
    for (left_pos, left_props), (right_pos, right_props) in zip(
            effective, effective[1:]):
        if progress <= right_pos:
            span = right_pos - left_pos or 1.0
            amount = (progress - left_pos) / span
            props = {}
            for key in set(left_props) | set(right_props):
                left = left_props.get(key, _default_css_value(key))
                right = right_props.get(key, left)
                props[key] = _lerp_css_value(left, right, amount)
            return props
    return dict(effective[-1][1])


def _animation_config(properties, variables):
    shorthand = _resolve_css_vars(properties.get("animation", ""), variables)
    if not shorthand:
        return None
    parts = shorthand.split()
    if not parts:
        return None
    name = parts[0]
    duration = next((part for part in parts if re.search(r"(?:ms|s)$", part)), "1s")
    delay = _resolve_css_vars(properties.get("animation-delay", "0s"), variables)
    direction = properties.get("animation-direction", "normal")
    if "reverse" in parts:
        direction = "reverse"
    if "alternate" in parts:
        direction = "alternate"
    if "alternate-reverse" in parts:
        direction = "alternate-reverse"
    return (_parse_css_time(duration, 1000.0), _parse_css_time(delay), direction, name)


def _selector_properties(element, rules):
    classes = set((element.get("class") or "").split())
    properties = {}
    for selector, rule_properties in rules:
        selector_classes = set(_css_class_names(selector))
        if selector_classes and not selector_classes.issubset(classes):
            continue
        if not selector_classes and selector.strip() not in ("*", "svg"):
            continue
        properties.update(rule_properties)
    return properties


def _rasterizar_css_animation(svg_txt, tam, avance_ms=0):
    """Render one CSS animation frame through CairoSVG without a browser."""
    cairo = _cairosvg()
    if cairo is None:
        raise RasterizadorNoDisponibleError("CairoSVG is unavailable")
    root = ET.fromstring(svg_txt)
    style = "\n".join(element.text or "" for element in root.iter()
                       if element.tag.rsplit("}", 1)[-1] == "style")
    variables = {}
    for selector, properties in _css_rules(style):
        if selector.strip() == "svg":
            variables.update({key: value for key, value in properties.items()
                              if key.startswith("--")})
    rules = _css_rules(style)
    keyframes = _parse_keyframes(style)
    for element in root.iter():
        properties = _selector_properties(element, rules)
        config = _animation_config(properties, variables)
        if config is None:
            continue
        duration, delay, direction, name = config
        stops = keyframes.get(name)
        if not stops or duration <= 0:
            continue
        phase = max(0.0, (float(avance_ms) - delay) / duration)
        iteration = int(phase)
        progress = phase - iteration
        if direction in ("reverse", "alternate-reverse"):
            progress = 1.0 - progress
        if direction in ("alternate", "alternate-reverse") and iteration % 2:
            progress = 1.0 - progress
        frame = _frame_properties(stops, progress)
        inline = element.get("style", "")
        # CairoSVG handles presentation attributes but does not apply SVG CSS
        # transform properties consistently. Keep the evaluated frame in the
        # native attributes so the static renderer sees the same geometry.
        # The same path also makes opacity and dash offsets deterministic.
        native = {"transform", "opacity", "fill", "stroke", "stroke-width",
                  "stroke-dasharray", "stroke-dashoffset", "visibility"}
        additions = ";".join("%s:%s" % (key, value)
                              for key, value in frame.items()
                              if key not in native and value)
        for key, value in frame.items():
            if key in native and value and value != "none":
                element.set(key, (_css_transform_to_svg(value)
                                  if key == "transform" else value))
        element.set("style", (inline + ";" if inline else "") + additions)
    rendered = ET.tostring(root, encoding="unicode")
    return cairo.svg2png(bytestring=rendered.encode("utf-8"),
                         output_width=tam, output_height=tam)


def _tiene_colores(png, esperados, tolerancia=40):
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(png)).convert("RGB")
    except Exception:
        return len(png) > 800  # sin Pillow, solo queda el piso de bytes
    presentes = [c for _n, c in (im.getcolors(maxcolors=100000) or [])]
    for esperado in esperados:
        if not any(all(abs(a - b) <= tolerancia for a, b in zip(c, esperado))
                   for c in presentes):
            return False
    return True


def _mide_movimiento(rasterizar_fn):
    """(dibuja_y_mueve) para una forma de rasterizar. La sonda se juzga con dos
    preguntas, no una: el cuadro tiene que MOSTRAR las figuras que le puse y
    ademas CAMBIAR. Sin la primera, la segunda mide ruido."""
    quieto = rasterizar_fn(_SONDA_ANIMA)
    if not _dibujo_vivo(quieto) or not _tiene_colores(quieto, _COLORES_SONDA):
        return False
    movido = rasterizar_fn(_adelantar(_SONDA_ANIMA, 500))
    return (_dibujo_vivo(movido) and _tiene_colores(movido, _COLORES_SONDA)
            and quieto != movido)


def _mide_css_animation():
    """Measure the deterministic CSS adapter at two explicit timeline points."""
    quieto = _rasterizar_css_animation(_SONDA_ANIMA, _TAM_SONDA, avance_ms=0)
    movido = _rasterizar_css_animation(_SONDA_ANIMA, _TAM_SONDA, avance_ms=500)
    return (_dibujo_vivo(quieto) and _tiene_colores(quieto, _COLORES_SONDA)
            and _dibujo_vivo(movido)
            and _tiene_colores(movido, _COLORES_SONDA)
            and quieto != movido)


def _anima(backend):
    """Si ESE backend dibuja Y mueve. Medido con la sonda representativa,
    cacheado por identidad del backend."""
    clave = backend if backend in ("cairosvg", _CSS_ANIMATION_BACKEND) else (_edge() or "?")
    if clave not in _ANIMADORES:
        try:
            if backend == "edge":
                _ANIMADORES[clave] = _perfil_navegador() is not None
            elif backend == _CSS_ANIMATION_BACKEND:
                _ANIMADORES[clave] = _mide_css_animation()
            else:
                _ANIMADORES[clave] = _mide_movimiento(
                    lambda t: _rasterizar_con(backend, t, _TAM_SONDA))
        except Exception:
            _ANIMADORES[clave] = False
    return _ANIMADORES[clave]


_PERFIL_ELEGIDO = {}


_INTENTOS = {}


def _elegir_navegador(anima=True):
    """El primer par (binario, perfil) que sirve para lo que se le pide.

    Aca es donde el instrumento se gana el derecho a acusar a un archivo. Con
    `anima=True` el liston es DIBUJAR Y MOVER la sonda; con `anima=False` basta
    con producir un PNG. Se recorren TODOS los binarios contra TODOS los
    perfiles, no el primero de cada uno, y se recuerda el par ganador. Si
    ninguno sirve, esta maquina no puede medir y hay que decirlo con nombres,
    no estimarlo: `_INTENTOS` guarda como fallo cada uno.
    """
    # La clave incluye los binarios presentes, no solo la pregunta: con una
    # clave global el resultado del primer sondeo sobrevivia a que cambiara el
    # entorno, que es exactamente lo que `_SONDEADOS` aprendio a no hacer.
    binarios = _binarios()
    clave = (anima, tuple(binarios))
    if clave not in _PERFIL_ELEGIDO:
        ganador, fallos = None, []
        for binario in binarios:
            for perfil in _PERFILES:
                try:
                    if anima:
                        ok = _mide_movimiento(
                            lambda t, b=binario, p=perfil: _rasterizar_edge(
                                t, _TAM_SONDA, perfil=p, binario=b))
                    else:
                        ok = _rasterizar_edge(
                            _SONDA, 8, perfil=perfil,
                            binario=binario)[:4] == b"\x89PNG"
                    if ok:
                        ganador = (binario, perfil)
                        break
                    fallos.append("%s %s: no %s"
                                  % (os.path.basename(binario), perfil[0],
                                     "dibuja/mueve la sonda" if anima
                                     else "produjo PNG"))
                except Exception as e:
                    fallos.append("%s %s: %s"
                                  % (os.path.basename(binario), perfil[0],
                                     type(e).__name__))
            if ganador:
                break
        _PERFIL_ELEGIDO[clave] = ganador
        _INTENTOS[clave] = fallos
    return _PERFIL_ELEGIDO[clave]


def _perfil_navegador(anima=True):
    par = _elegir_navegador(anima=anima)
    return par[1] if par else None


def por_que_no_hay_navegador(anima=True):
    """Que se probo y como fallo. Un salto que no nombra lo que intento cuesta
    una sesion en vez de una linea de log."""
    hallados = _binarios()
    if not hallados:
        return "no se encontro ningun navegador (%s)" % ", ".join(
            NAVEGADOR_CANDS[:3] + ["..."])
    fallos = _INTENTOS.get((anima, tuple(hallados))) or ["sin intentos"]
    return "probados %d binario(s): %s" % (len(hallados), "; ".join(fallos))


def backend_disponible(anima=False):
    """Return 'cairosvg', a browser, or the local CSS adapter.

    Con `anima=True` la pregunta es otra y mas estrecha: cual sirve para MEDIR
    movimiento. cairosvg rasteriza impecable y no ejecuta ni una animacion CSS,
    asi que para un GIF no es un backend peor: no es un backend. Se prefiere el
    navegador y la capacidad se MIDE con `_anima()`, no se declara por nombre.
    """
    if anima:
        for backend in ("edge", "cairosvg"):
            if backend == "edge" and not _edge_funciona():
                continue
            if backend == "cairosvg" and _cairosvg() is None:
                continue
            if _anima(backend):
                return backend
        if _cairosvg() is not None and _anima(_CSS_ANIMATION_BACKEND):
            return _CSS_ANIMATION_BACKEND
        return None
    if _cairosvg() is not None:
        return "cairosvg"
    return "edge" if _edge_funciona() else None


def _rasterizar_con(backend, txt, tam, anima=False):
    if backend == _CSS_ANIMATION_BACKEND:
        return _rasterizar_css_animation(txt, tam, avance_ms=0)
    if backend == "cairosvg":
        return _cairosvg().svg2png(bytestring=txt.encode("utf-8"),
                                   output_width=tam, output_height=tam)
    # Para medir movimiento se usa el perfil que se gano ese derecho; para
    # rasterizar a secas, el primero que produzca PNG.
    par = _elegir_navegador(anima=anima)
    return _rasterizar_edge(txt, tam,
                            perfil=par[1] if par else None,
                            binario=par[0] if par else None)


def rasterizar(svg_txt, tam=TAM, avance_ms=None, backend=None, anima=False):
    """SVG (str) -> bytes PNG de tam x tam.

    avance_ms adelanta la animacion inyectando un animation-delay negativo: es
    como se mide si el icono esta VIVO (si el cuadro tardio difiere del 0).
    Solo lo respeta un backend que anime, y quien quiera medir movimiento pide
    ese backend explicitamente (`backend_disponible(anima=True)`) en vez de
    confiar en el que toque.

    `anima=True` es una bandera aparte y no se deduce de `avance_ms`: el cuadro
    0 de una secuencia va SIN avance y tiene que salir del mismo perfil de
    navegador que los demas. Deducirlo lo haria salir de otro, y comparar dos
    cuadros producidos por instrumentos distintos no mide nada.
    """
    if backend == _CSS_ANIMATION_BACKEND:
        return _rasterizar_css_animation(svg_txt, tam,
                                         avance_ms=avance_ms or 0)
    txt = svg_txt
    if avance_ms:
        txt = _adelantar(txt, avance_ms)
    backend = backend or backend_disponible()
    if backend is None:
        raise RasterizadorNoDisponibleError(
            "ningun rasterizador disponible: cairosvg no se puede importar y "
            "no se encontro navegador. Instala cairosvg (Linux) o Edge/Chrome.")
    return _rasterizar_con(backend, txt, tam, anima=anima)


def _rasterizar_edge(svg_txt, tam, perfil=None, binario=None):
    edge = binario or _edge()
    inicio = svg_txt.find("<svg")
    if inicio < 0:
        raise ValueError("el texto no contiene un <svg")
    html = ('<!doctype html><meta charset="utf-8">'
            '<style>html,body{margin:0;padding:0}'
            'svg{display:block;width:%dpx;height:%dpx}</style>%s'
            % (tam, tam, svg_txt[inicio:]))
    with tempfile.TemporaryDirectory(prefix="motor-sem-") as tmp:
        tmp = pathlib.Path(tmp)
        entrada = tmp / "in.html"
        entrada.write_text(html, encoding="utf-8")
        png = tmp / "out.png"
        ventana = max(tam, VENTANA_MIN)
        subprocess.run(
            [edge] + _BASE + (perfil or _PERFILES[0])
            + ["--user-data-dir=%s" % (tmp / "perfil"),
             "--window-size=%d,%d" % (ventana, ventana),
             "--screenshot=%s" % png, entrada.as_uri()],
            check=False, timeout=90,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not png.exists() or png.stat().st_size == 0:
            raise RasterizadorNoDisponibleError(
                "Edge headless no produjo PNG (%s)" % edge)
        datos = png.read_bytes()
    if ventana == tam:
        return datos
    # El SVG va pegado arriba a la izquierda (margin:0), asi que el recorte es
    # exacto y no hay que buscar nada. RECORTE, nunca reescalado: resamplear lo
    # que despues se compara cuadro a cuadro inventaria diferencias.
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(datos)).convert("RGBA").crop(
            (0, 0, tam, tam))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        return buf.getvalue()
    except ImportError:
        # Sin Pillow no se puede recortar; devolver la ventana entera seria
        # entregar otra cosa que la pedida, callado.
        raise RasterizadorNoDisponibleError(
            "hace falta Pillow para recortar la ventana de %d px al tamano "
            "pedido de %d px" % (ventana, tam))


def animar(svg_txt, salida, cuadros=12, ciclo_ms=4000, tam=256):
    """Renderiza CUADROS a lo largo de un ciclo y los escribe como GIF animado.

    Por que GIF y no PNG (usuario, 2026-07-30): el artefacto es una ANIMACION,
    no un icono. Un PNG es la animacion mutilada -- y peor: un PNG mirado como
    prueba no distingue "quieto" de "animado", asi que valida algo que no es lo
    que se construyo.

    Devuelve (ruta, n_cuadros, cuadros_distintos). El tercer numero es la
    medicion que importa: si todos los cuadros son iguales, la animacion NO
    esta pasando y hay que decirlo, no suponerla.

    Y por eso mismo exige un backend que anime, medido: con uno que no lo hace
    ese tercer numero seria un 1 indistinguible del 1 de un icono muerto, y un
    numero ambiguo en un instrumento es peor que una excepcion.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise RasterizadorNoDisponibleError("Pillow no disponible: %s" % e)
    if cuadros < 2:
        raise ValueError("un GIF necesita al menos 2 cuadros")
    backend = backend_disponible(anima=True)
    if backend is None:
        raise BackendNoAnimaError(
            "no hay backend que ejecute animaciones CSS (hay: %s). Medir "
            "movimiento necesita un navegador: Edge o Chrome/Chromium."
            % (backend_disponible() or "ninguno"))
    paso = ciclo_ms // cuadros
    imgs, firmas = [], []
    for n in range(cuadros):
        # avance_ms=0 en el primer cuadro: es el frame 0 real, el que decide si
        # el icono nace visible (invariante 3 del compilador).
        png = rasterizar(svg_txt, tam=tam, avance_ms=(n * paso) or None,
                         backend=backend, anima=True)
        import io
        im = Image.open(io.BytesIO(png)).convert("RGB")
        imgs.append(im)
        firmas.append(im.tobytes())
    # Ultimo control antes de devolver un numero: el backend puede haber pasado
    # la sonda y no estar dibujando ESTA pieza. Si el cuadro 0 es un lienzo
    # liso, lo que sigue no es una medicion del icono, es una medicion del
    # vacio -- y sus cuadros iguales acusarian al archivo por un defecto que es
    # del instrumento.
    colores = imgs[0].getcolors(maxcolors=64)
    if colores is not None and len(colores) <= 2:
        raise BackendNoDibujaError(
            "el backend %s devolvio un cuadro liso (%d color/es): no esta "
            "dibujando esta pieza, asi que no hay movimiento que medir"
            % (backend, len(colores)))
    distintos = len(set(firmas))
    salida = pathlib.Path(salida)
    imgs[0].save(salida, save_all=True, append_images=imgs[1:],
                 duration=paso, loop=0, optimize=True)
    return salida, cuadros, distintos


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "gif":
        if len(sys.argv) < 4:
            sys.exit("uso: py -m motor_semantico.rasterizador gif in.svg "
                     "out.gif [cuadros] [tam]")
        cuadros = int(sys.argv[4]) if len(sys.argv) > 4 else 12
        tam = int(sys.argv[5]) if len(sys.argv) > 5 else 256
        svg = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")
        ruta, n, distintos = animar(svg, sys.argv[3], cuadros=cuadros, tam=tam)
        print("OK %s (%d cuadros, %d distintos, %.1f KB, backend %s)"
              % (ruta, n, distintos, ruta.stat().st_size / 1024,
                 backend_disponible()))
        if distintos <= 1:
            print("! los cuadros son identicos: la animacion no llego al "
                  "rasterizador", file=sys.stderr)
            return 1
        return 0
    if len(sys.argv) < 3:
        sys.exit("uso: py -m motor_semantico.rasterizador in.svg out.png [tam]\n"
                 "     py -m motor_semantico.rasterizador gif in.svg out.gif "
                 "[cuadros] [tam]")
    tam = int(sys.argv[3]) if len(sys.argv) > 3 else TAM
    svg = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    datos = rasterizar(svg, tam)
    pathlib.Path(sys.argv[2]).write_bytes(datos)
    print("OK %s (%d bytes, backend %s)"
          % (sys.argv[2], len(datos), backend_disponible()))


if __name__ == "__main__":
    if __package__ in (None, ""):
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
        __package__ = "motor_semantico"
    main()
