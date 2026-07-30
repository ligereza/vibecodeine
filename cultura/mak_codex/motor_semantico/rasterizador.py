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
import shutil
import subprocess
import sys
import tempfile

TAM = 256

# Navegadores: los mismos candidatos de Edge que tools/svg/svg_to_pdf.py, mas
# Chrome/Chromium, que es lo que hay en un runner de Linux y en la caja. Se
# prueba por ejecucion, no por existencia.
NAVEGADOR_CANDS = [
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "/usr/bin/microsoft-edge",
    "/usr/bin/microsoft-edge-stable",
    "/opt/microsoft/msedge/msedge",
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
    ["--headless=old", "--disable-dev-shm-usage", "--no-sandbox"],
    ["--headless=old", "--disable-dev-shm-usage", "--no-sandbox",
     "--virtual-time-budget=1000"],
    ["--headless", "--disable-dev-shm-usage", "--no-sandbox"],
]


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


def _edge():
    """El binario de navegador, si hay alguno. Conserva el nombre historico
    porque es el punto que los tests intervienen para fingir su ausencia."""
    for e in NAVEGADOR_CANDS:
        if os.path.exists(e):
            return e
    return (shutil.which("microsoft-edge") or shutil.which("msedge")
            or shutil.which("google-chrome") or shutil.which("chromium"))


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
            _SONDEADOS[binario] = _perfil_navegador(anima=False) is not None
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


def _mide_movimiento(rasterizar_fn):
    """(dibuja_y_mueve) para una forma de rasterizar. La sonda se juzga con dos
    preguntas, no una: el cuadro tiene que TENER dibujo y ademas CAMBIAR."""
    quieto = rasterizar_fn(_SONDA_ANIMA)
    if not _dibujo_vivo(quieto):
        return False
    movido = rasterizar_fn(_adelantar(_SONDA_ANIMA, 500))
    return _dibujo_vivo(movido) and quieto != movido


def _anima(backend):
    """Si ESE backend dibuja Y mueve. Medido con la sonda representativa,
    cacheado por identidad del backend."""
    clave = backend if backend == "cairosvg" else (_edge() or "?")
    if clave not in _ANIMADORES:
        try:
            if backend == "edge":
                _ANIMADORES[clave] = _perfil_navegador() is not None
            else:
                _ANIMADORES[clave] = _mide_movimiento(
                    lambda t: _rasterizar_con(backend, t, _TAM_SONDA))
        except Exception:
            _ANIMADORES[clave] = False
    return _ANIMADORES[clave]


_PERFIL_ELEGIDO = {}


def _perfil_navegador(anima=True):
    """El primer perfil de banderas que sirve para lo que se le pide, o None.

    Aca es donde el instrumento se gana el derecho a acusar a un archivo. Con
    `anima=True` el listón es DIBUJAR Y MOVER la sonda representativa; con
    `anima=False` basta con producir un PNG. Se prueban en orden y se recuerda
    el ganador por binario; si ninguno sirve, esta maquina no puede medir y hay
    que decirlo, no estimarlo.
    """
    binario = _edge()
    if not binario:
        return None
    clave = (binario, anima)
    if clave not in _PERFIL_ELEGIDO:
        elegido = None
        for perfil in _PERFILES:
            try:
                if anima:
                    ok = _mide_movimiento(
                        lambda t, p=perfil: _rasterizar_edge(
                            t, _TAM_SONDA, perfil=p))
                else:
                    ok = _rasterizar_edge(_SONDA, 8, perfil=perfil)[:4] \
                        == b"\x89PNG"
                if ok:
                    elegido = perfil
                    break
            except Exception:
                continue
        _PERFIL_ELEGIDO[clave] = elegido
    return _PERFIL_ELEGIDO[clave]


def backend_disponible(anima=False):
    """'cairosvg', 'edge' o None; el backend se sondea una vez con un SVG 8x8.

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
        return None
    if _cairosvg() is not None:
        return "cairosvg"
    return "edge" if _edge_funciona() else None


def _rasterizar_con(backend, txt, tam, anima=False):
    if backend == "cairosvg":
        return _cairosvg().svg2png(bytestring=txt.encode("utf-8"),
                                   output_width=tam, output_height=tam)
    # Para medir movimiento se usa el perfil que se gano ese derecho; para
    # rasterizar a secas, el primero que produzca PNG.
    return _rasterizar_edge(txt, tam, perfil=_perfil_navegador(anima=anima))


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
    txt = svg_txt
    if avance_ms:
        txt = _adelantar(txt, avance_ms)
    backend = backend or backend_disponible()
    if backend is None:
        raise RasterizadorNoDisponibleError(
            "ningun rasterizador disponible: cairosvg no se puede importar y "
            "no se encontro navegador. Instala cairosvg (Linux) o Edge/Chrome.")
    return _rasterizar_con(backend, txt, tam, anima=anima)


def _rasterizar_edge(svg_txt, tam, perfil=None):
    edge = _edge()
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
        subprocess.run(
            [edge] + _BASE + (perfil or _PERFILES[0])
            + ["--user-data-dir=%s" % (tmp / "perfil"),
             "--window-size=%d,%d" % (tam, tam),
             "--screenshot=%s" % png, entrada.as_uri()],
            check=False, timeout=90,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not png.exists() or png.stat().st_size == 0:
            raise RasterizadorNoDisponibleError(
                "Edge headless no produjo PNG (%s)" % edge)
        return png.read_bytes()


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
