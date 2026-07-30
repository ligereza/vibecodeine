#!/usr/bin/env python3
"""
critico.py — Intento de convertir en aritmética el "equilibrio compositivo".

En el turno anterior dije que no sabía cómo medir esto. Este módulo es el
intento honesto. Renderiza el SVG y calcula métricas PERCEPTUALES sobre los
píxeles — no sobre el código.

Mide seis cosas, todas defendibles:

  1. TINTA        — % del lienzo ocupado. Muy poco = vacío; mucho = saturado.
  2. CENTRADO     — distancia del centroide visual al centro del lienzo.
  3. DOMINANCIA   — ¿hay una figura que manda? (contraste protagonista/fondo)
  4. MARGEN       — ¿se respeta la zona segura en píxeles reales?
  5. LEGIBILIDAD  — ¿sobrevive a 24x24 px? (prueba de logo)
  6. VIDA         — ¿cambia algo entre el frame 0 y el frame medio?

Lo que SIGUE sin medir: si la metáfora funciona, si es bello, si es original.
Eso necesita ojo. Pero estas seis atrapan la mayoría de los defectos que
encontré mirando en las dos rondas de revisión.

USO:  py -m motor_semantico.critico salida/*.svg

El rasterizado vive en `rasterizador.py` (dos backends). Este modulo se puede
IMPORTAR en cualquier maquina, con o sin dependencias: `analizar()` devuelve un
dict con 'error' cuando no hay con que rasterizar. La version original salia
del interprete al importarse (`sys.exit`), y eso lo volvia intesteable.
"""
import io, math, sys, pathlib

if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    __package__ = "motor_semantico"

from . import rasterizador  # noqa: E402
from .rasterizador import RasterizadorNoDisponibleError  # noqa: E402

TAM = 256
CHICO = 24


class SinPillowError(RuntimeError):
    """Pillow no esta instalado: no hay analisis de pixeles posible."""


def _pil():
    """Pillow por dentro de las funciones, no al importar el modulo: asi
    `import critico` no exige dependencias y el modulo es testeable en
    cualquier maquina. Un accesor y no un import por funcion, porque la
    primera version dejo `Image` sin definir en `mascara_tinta` -- un
    NameError latente que compilaba perfecto (el mismo defecto que persigue
    tests/test_utilidades_mak_sanidad.py)."""
    try:
        from PIL import Image
        return Image
    except ImportError as e:
        raise SinPillowError("Pillow no disponible: %s" % e)


# -- utilidades -----------------------------------------------------------
def rasterizar(svg_txt, tam=TAM, avance_ms=None):
    """Renderiza a una imagen RGB de Pillow. Si avance_ms, adelanta la
    animacion (animation-delay negativo) para poder comparar frames."""
    Image = _pil()
    png = rasterizador.rasterizar(svg_txt, tam=tam, avance_ms=avance_ms)
    return Image.open(io.BytesIO(png)).convert("RGB")


def color_fondo(im):
    """El fondo es el color de las esquinas."""
    w, h = im.size
    esquinas = [im.getpixel((1, 1)), im.getpixel((w - 2, 1)),
                im.getpixel((1, h - 2)), im.getpixel((w - 2, h - 2))]
    return max(set(esquinas), key=esquinas.count)


def mascara_tinta(im, fondo, umbral=34):
    """Píxeles que difieren del fondo = contenido."""
    px = im.load()
    w, h = im.size
    m = _pil().new("L", (w, h), 0)
    mp = m.load()
    fr, fg, fb = fondo
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - fr) + abs(g - fg) + abs(b - fb) > umbral:
                mp[x, y] = 255
    return m


def _lum(c):
    f = lambda v: (v / 255) / 12.92 if v / 255 <= .03928 else (((v / 255) + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def contraste(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


# -- las seis métricas ----------------------------------------------------
def analizar(svg_txt, nombre="?"):
    """Las seis metricas, o {'error': ...} si esta maquina no puede rasterizar.
    Nunca levanta por falta de dependencias: el llamador decide si un icono sin
    analisis perceptual se entrega o no (en el modo iconos de codex, se entrega
    con el aviso puesto -- el compilador ya garantiza los invariantes duros)."""
    try:
        im = rasterizar(svg_txt)
    except (RasterizadorNoDisponibleError, SinPillowError) as e:
        return {"nombre": nombre, "error": str(e), "alertas": [], "notas": [],
                "puntaje": None}
    fondo = color_fondo(im)
    m = mascara_tinta(im, fondo)
    w, h = m.size
    px = m.load()

    total = w * h
    tinta = 0
    sx = sy = 0
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            if px[x, y]:
                tinta += 1
                sx += x; sy += y
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)

    r = {"nombre": nombre, "alertas": [], "notas": []}
    if tinta == 0:
        r["alertas"].append("LIENZO VACÍO — no se dibujó nada visible")
        r["puntaje"] = 0
        return r

    # 1. tinta
    ratio = tinta / total
    r["tinta"] = ratio
    if ratio < .06:
        r["alertas"].append(f"casi vacío ({ratio:.1%} de tinta) — el ícono no se lee")
    elif ratio > .72:
        r["alertas"].append(f"saturado ({ratio:.1%} de tinta) — no hay respiro")
    elif ratio < .12:
        r["notas"].append(f"algo vacío ({ratio:.1%})")

    # 2. centrado
    cx, cy = sx / tinta, sy / tinta
    desvio = math.hypot(cx - w / 2, cy - h / 2) / (w / 2)
    r["descentrado"] = desvio
    if desvio > .30:
        r["alertas"].append(f"composición descentrada ({desvio:.0%} del radio)")
    elif desvio > .18:
        r["notas"].append(f"ligeramente descentrado ({desvio:.0%})")

    # 3. dominancia — ¿hay jerarquía o todo compite?
    #    OJO: contar colores crudos NO sirve. Un render de 256px genera cientos
    #    de tonos por antialiasing de los bordes (medido: 801 de 808 colores de
    #    un ícono eran ruido de borde). Solo cuentan las familias con peso real.
    colores = {}
    ip = im.load()
    muestreados = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if px[x, y]:
                c = (ip[x, y][0] // 40, ip[x, y][1] // 40, ip[x, y][2] // 40)
                colores[c] = colores.get(c, 0) + 1
                muestreados += 1
    if colores and muestreados:
        # descartar familias por debajo del 4% del contenido = antialiasing
        reales = {k: v for k, v in colores.items() if v / muestreados >= .04}
        if reales:
            orden = sorted(reales.values(), reverse=True)
            dom = orden[0] / sum(orden)
            r["dominancia"] = dom
            r["familias_color"] = len(orden)
            if len(orden) >= 4 and dom < .34:
                r["alertas"].append(
                    f"sin jerarquía visual — {len(orden)} masas de color compiten "
                    f"(la mayor ocupa solo {dom:.0%})")

    # 4. margen real en píxeles
    #    Distinguir SANGRADO (deliberado: una banda que cruza todo el borde)
    #    de DESBORDE (accidental: una punta que se escapa). Se mide qué
    #    fracción de cada borde está cubierta; si es casi todo, es diseño.
    escala = w / 120
    marg = min(minx, miny, w - maxx, h - maxy) / escala
    r["margen"] = marg
    if marg < 3:
        bordes = {
            "sup": sum(1 for x in range(w) if px[x, 0]) / w,
            "inf": sum(1 for x in range(w) if px[x, h - 1]) / w,
            "izq": sum(1 for y in range(h) if px[0, y]) / h,
            "der": sum(1 for y in range(h) if px[w - 1, y]) / h,
        }
        tocados = {k: v for k, v in bordes.items() if v > .01}
        parcial = {k: v for k, v in tocados.items() if v <= .80}
        if not tocados:
            # margen mínimo pero sin tocar: solo está justo
            r["notas"].append(f"margen muy justo ({marg:.1f}/120) sin llegar a tocar")
        elif not parcial:
            # todos los bordes tocados están cubiertos casi enteros -> diseño
            r["sangrado"] = True
            r["notas"].append(
                f"sangra a propósito por {'/'.join(tocados)} (banda completa)")
        else:
            r["alertas"].append(
                f"el contenido se escapa parcialmente del lienzo "
                f"({', '.join(f'{k} {v:.0%}' for k, v in parcial.items())})")
    elif marg < 6:
        r["notas"].append(f"margen ajustado ({marg:.1f}/120)")

    # 5. legibilidad a tamaño chico
    chico = rasterizar(svg_txt, CHICO)
    grande_ref = im.resize((CHICO, CHICO), _pil().LANCZOS)
    dif = sum(abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])
              for a, b in zip(chico.getdata(), grande_ref.getdata()))
    dif /= (CHICO * CHICO * 3 * 255)
    r["perdida_al_reducir"] = dif
    mc = mascara_tinta(chico, color_fondo(chico))
    tinta_chica = sum(1 for v in mc.getdata() if v) / (CHICO * CHICO)
    if tinta_chica < .04:
        r["alertas"].append("ilegible a 24px — no funciona como logo")
    elif abs(tinta_chica - ratio) > .28:
        r["notas"].append("la silueta cambia bastante al reducir")

    # 6. vida — ¿la animación hace algo?
    tarde = rasterizar(svg_txt, TAM, avance_ms=1500)
    delta = sum(abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])
                for a, b in zip(im.getdata(), tarde.getdata()))
    delta /= (total * 3 * 255)
    r["movimiento"] = delta

    # puntaje
    p = 100
    p -= 34 * len(r["alertas"])
    p -= 7 * len(r["notas"])
    r["puntaje"] = max(0, p)
    return r


def imprimir(r):
    if r.get("error"):
        print(f"- {r['nombre']:<28} sin analisis: {r['error']}")
        return
    est = "OK" if not r["alertas"] else "x"
    print(f"{est} {r['nombre']:<28} puntaje {r['puntaje']:>3}", end="")
    if "tinta" in r:
        print(f"  tinta {r['tinta']:>5.1%}  centro {1-r['descentrado']:>5.0%}"
              f"  margen {r['margen']:>4.1f}", end="")
    print()
    for a in r["alertas"]:
        print(f"    x {a}")
    for n in r["notas"]:
        print(f"    - {n}")


def main():
    # Sin glob relativo al CWD: en la caja este modulo corre con cwd=/home/mak/
    # codex, no en su propia carpeta, y un default "salida/*.svg" analizaba una
    # carpeta que no existe y decia "sin archivos" como si fuera un veredicto.
    rutas = [pathlib.Path(p) for p in sys.argv[1:]]
    if not rutas:
        sys.exit("uso: py -m motor_semantico.critico icono.svg [otro.svg ...]")

    res = [analizar(p.read_text(encoding="utf-8"), p.stem) for p in rutas]
    for r in res:
        imprimir(r)

    medidos = [x for x in res if x.get("puntaje") is not None]
    if not medidos:
        print("\nNingun icono pudo rasterizarse: no hay veredicto perceptual.")
        return 1
    prom = sum(x["puntaje"] for x in medidos) / len(medidos)
    malos = [x for x in medidos if x["alertas"]]
    print("\n" + "-" * 62)
    print(f"{len(medidos)} íconos - puntaje medio {prom:.0f}/100 - "
          f"{len(malos)} con alertas")
    if malos:
        print("Revisar visualmente:", ", ".join(x["nombre"] for x in malos))
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
