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

# Edge: mismos candidatos que tools/svg/svg_to_pdf.py mas los de Linux, por si
# la caja algun dia lo tiene. Se prueba por existencia, no por fe.
EDGE_CANDS = [
    r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "/usr/bin/microsoft-edge",
    "/usr/bin/microsoft-edge-stable",
    "/opt/microsoft/msedge/msedge",
]


class RasterizadorNoDisponibleError(RuntimeError):
    """No hay backend de rasterizado en esta maquina."""


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
    for e in EDGE_CANDS:
        if os.path.exists(e):
            return e
    hallado = shutil.which("microsoft-edge") or shutil.which("msedge")
    return hallado


_SONDA = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'>" \
         "<rect width='8' height='8' fill='#f00'/></svg>"
#  ruta del binario -> si rasteriza. Indexado por RUTA y no un solo booleano a
#  proposito: asi el resultado no sobrevive a que cambie el binario encontrado
#  (un test que finge "no hay Edge" tiene que ver "no hay Edge", no la sonda
#  vieja).
_SONDEADOS = {}


def _edge_funciona():
    """Si el Edge que encontramos DE VERDAD produce un PNG. Se sondea una vez
    por binario y se recuerda.

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
            _SONDEADOS[binario] = _rasterizar_edge(_SONDA, 8)[:4] == b"\x89PNG"
        except Exception:
            # Cualquier motivo -- binario roto, sin sandbox, sin HOME -- cuenta
            # como "no sirve". No se distingue porque no cambia la decision: no
            # hay con que rasterizar.
            _SONDEADOS[binario] = False
    return _SONDEADOS[binario]


def backend_disponible():
    """'cairosvg', 'edge' o None. Es la pregunta que hay que hacer antes de
    prometer un analisis perceptual, y la respuesta esta MEDIDA: el backend se
    sondea una vez con un SVG de 8x8."""
    if _cairosvg() is not None:
        return "cairosvg"
    return "edge" if _edge_funciona() else None


def rasterizar(svg_txt, tam=TAM, avance_ms=None):
    """SVG (str) -> bytes PNG de tam x tam.

    avance_ms adelanta la animacion inyectando un animation-delay negativo:
    es como se mide si el icono esta VIVO (si el frame tardio difiere del 0).
    Solo lo respeta un backend que anime; Edge headless si, cairosvg no
    necesariamente -- el llamador debe tratar un delta 0 como "no medido",
    no como "muerto".
    """
    txt = svg_txt
    if avance_ms:
        txt = _adelantar(txt, avance_ms)
    backend = backend_disponible()
    if backend is None:
        raise RasterizadorNoDisponibleError(
            "ningun rasterizador disponible: cairosvg no se puede importar y "
            "no se encontro Edge. Instala cairosvg (Linux) o Edge (Windows).")
    if backend == "cairosvg":
        cairosvg = _cairosvg()
        return cairosvg.svg2png(bytestring=txt.encode("utf-8"),
                                output_width=tam, output_height=tam)
    return _rasterizar_edge(txt, tam)


def _rasterizar_edge(svg_txt, tam):
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
            [edge, "--headless=new", "--disable-gpu", "--no-first-run",
             "--user-data-dir=%s" % (tmp / "perfil"),
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
    esta pasando en el rasterizador y hay que decirlo, no suponerla.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise RasterizadorNoDisponibleError("Pillow no disponible: %s" % e)
    if cuadros < 2:
        raise ValueError("un GIF necesita al menos 2 cuadros")
    paso = ciclo_ms // cuadros
    imgs, firmas = [], []
    for n in range(cuadros):
        # avance_ms=0 en el primer cuadro: es el frame 0 real, el que decide si
        # el icono nace visible (invariante 3 del compilador).
        png = rasterizar(svg_txt, tam=tam, avance_ms=(n * paso) or None)
        import io
        im = Image.open(io.BytesIO(png)).convert("RGB")
        imgs.append(im)
        firmas.append(im.tobytes())
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
