#!/usr/bin/env python3
"""
VibeCode Spaces — CLI/librería para visualizar la topología del código
mediante sus espacios vacíos.

La idea es no colorear el código, sino los huecos entre palabras, indentaciones
y saltos de línea. Así la estructura se convierte en un patrón detectable a ojo,
ligeramente psicodélico, sin ser invasivo.

Uso:
    python vibecode_spaces.py archivo.py -m flow -a
    cat archivo.py | python vibecode_spaces.py -m drift

Como librería:
    from vibecode_spaces import render_spaces
    render_spaces(codigo, mode="flow", animate=True)
"""

import sys
import re
import math
import time
import select
import argparse
from typing import List

# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------
RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J\033[H"


def fg256(n: int) -> str:
    return f"\033[38;5;{n}m"


# Paletas de 256 colores, todas oscilando en una misma familia
PALETTES = {
    "neon": [fg256(c) for c in (51, 198, 135, 226, 48, 87, 213)],
    "cyber": [fg256(c) for c in (87, 141, 219, 255, 117, 213)],
    "matrix": [fg256(c) for c in (22, 28, 34, 46, 82, 120, 154)],
    "fire": [fg256(c) for c in (52, 88, 124, 166, 202, 208, 226)],
    "rainbow": [fg256(c) for c in (196, 208, 226, 46, 51, 21, 129, 201)],
    "deep": [fg256(c) for c in (17, 18, 19, 24, 29, 66, 96)],
    "glitch": [fg256(c) for c in (46, 196, 226, 201, 51, 255)],
}


# ---------------------------------------------------------------------------
# Parsing: la base es saber dónde están los espacios
# ---------------------------------------------------------------------------
def tokenize_line(line: str) -> List[tuple]:
    """
    Divide una línea en tokens conservando los espacios.
    Retorna [(tipo, texto)] donde tipo es 'space' o 'word'.
    """
    parts = re.split(r"(\s+)", line)
    tokens = []
    for part in parts:
        if not part:
            continue
        tokens.append(("space" if part.isspace() else "word", part))
    return tokens


# ---------------------------------------------------------------------------
# Modos estáticos y animados
# ---------------------------------------------------------------------------
def render_static(
    text: str,
    mode: str = "void",
    palette_name: str = "neon",
    fill_char: str = "·",
    ghost: bool = True,
) -> str:
    """
    Renderiza un frame estático.

    Modos:
      - void:   espacios coloreados, texto en gris tenue.
      - length: el color del espacio depende de la longitud del bloque.
      - blocks: cada bloque de espacios es un bloque sólido.
    """
    palette = PALETTES.get(palette_name, PALETTES["neon"])
    lines = text.splitlines()
    out_lines: List[str] = []

    for line in lines:
        rendered = []
        tokens = tokenize_line(line)

        for kind, part in tokens:
            if kind == "space":
                length = len(part)
                if mode == "length":
                    idx = min(length, len(palette)) - 1
                    color = palette[idx]
                elif mode == "blocks":
                    color = palette[length % len(palette)]
                else:  # void
                    color = palette[length % len(palette)]
                rendered.append(f"{color}{fill_char * length}{RESET}")
            else:
                if ghost:
                    # Texto fantasma: se ve, pero no roba atención
                    rendered.append(f"\033[90m{part}{RESET}")
                else:
                    rendered.append(part)
        out_lines.append("".join(rendered))

    return "\n".join(out_lines)


def render_frame(
    text: str,
    mode: str = "flow",
    palette_name: str = "neon",
    t: int = 0,
    fill_char: str = "·",
    ghost: bool = True,
) -> str:
    """
    Renderiza un frame animado. El parámetro `t` es el índice de tiempo.

    Modos animados:
      - flow:  onda sinusoidal que se desplaza por los espacios.
      - scan:  barra vertical que recorre la pantalla.
      - drift: colores de los bloques de espacios cambian lentamente.
      - pulse: bloques largos de espacios "pulsan" con intensidad.
      - rain:  líneas de color caen de arriba a abajo.
    """
    palette = PALETTES.get(palette_name, PALETTES["neon"])
    lines = text.splitlines()
    out_lines: List[str] = []
    n_colors = len(palette)

    for y, line in enumerate(lines):
        rendered = []
        tokens = tokenize_line(line)
        x = 0

        for kind, part in tokens:
            length = len(part)
            if kind == "space":
                if mode == "flow":
                    idx = int((math.sin((x + y * 2 + t * 3) * 0.15) + 1) * 0.5 * n_colors) % n_colors
                    color = palette[idx]
                elif mode == "scan":
                    scan_pos = (t * 2) % 80
                    dist = abs((x + length // 2) - scan_pos)
                    if dist < 6:
                        idx = dist % n_colors
                        color = palette[idx]
                    else:
                        color = "\033[90m"
                elif mode == "drift":
                    idx = (x + y + t) % n_colors
                    color = palette[idx]
                elif mode == "pulse":
                    idx = min(length, n_colors) - 1
                    pulse = abs(math.sin(t * 0.2 + length))
                    color = palette[idx] if pulse > 0.3 else "\033[90m"
                elif mode == "rain":
                    drop = (y + t) % (len(lines) + 5)
                    if abs(drop - y) < 3:
                        idx = (y + t) % n_colors
                        color = palette[idx]
                    else:
                        color = "\033[90m"
                else:
                    color = palette[length % n_colors]
                rendered.append(f"{color}{fill_char * length}{RESET}")
            else:
                rendered.append(f"\033[90m{part}{RESET}" if ghost else part)
            x += length
        out_lines.append("".join(rendered))

    return "\n".join(out_lines)


def header(mode: str, palette: str, animated: bool) -> str:
    return (
        f"\n\033[90m{'=' * 60}{RESET}\n"
        f"\033[1;97m✨ VibeCode Spaces \033[0;90m| "
        f"modo: {mode} | paleta: {palette}{' | animado' if animated else ''}{RESET}\n"
        f"\033[90m{'=' * 60}{RESET}\n"
    )


def footer() -> str:
    return f"\n\033[90m{'=' * 60}{RESET}\n"


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def render_spaces(
    text: str,
    mode: str = "flow",
    palette: str = "neon",
    animate: bool = False,
    cycles: int = 200,
    speed: float = 0.08,
    fill_char: str = "·",
    ghost: bool = True,
    file=None,
):
    """
    API de librería. Muestra el texto coloreando sus espacios.

    Args:
        text: código o texto a visualizar.
        mode: void, length, blocks, flow, scan, drift, pulse, rain.
        palette: nombre de paleta del diccionario PALETTES.
        animate: si True, reproduce una animación en terminal.
        cycles: cantidad de frames de animación.
        speed: segundos entre frames.
        fill_char: carácter que rellena los espacios.
        ghost: mostrar el texto real en gris tenue.
        file: archivo de salida (default sys.stdout).
    """
    out = file or sys.stdout
    static_modes = {"void", "length", "blocks"}

    if not animate or mode in static_modes:
        out.write(header(mode, palette, False))
        out.write(render_static(text, mode=mode, palette_name=palette, fill_char=fill_char, ghost=ghost))
        out.write(footer())
        out.flush()
        return

    out.write(HIDE_CURSOR)
    out.write(CLEAR_SCREEN)
    out.flush()

    try:
        for t in range(cycles):
            out.write(CLEAR_SCREEN)
            out.write(header(mode, palette, True))
            out.write(
                render_frame(
                    text,
                    mode=mode,
                    palette_name=palette,
                    t=t,
                    fill_char=fill_char,
                    ghost=ghost,
                )
            )
            out.write(footer())
            out.flush()
            time.sleep(speed)
    finally:
        out.write(SHOW_CURSOR)
        out.flush()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
SAMPLE_CODE = """# --- Topología de IA: indentación y one-liners ---

def procesar_tensores(matriz, factores):
    resultados = []
    for fila in matriz:
        activacion = [max(0.0, x * f) for x, f in zip(fila, factores)]
        if sum(activacion) > 100.5:
            resultados.append(activacion)
    return resultados

# One-liner denso
data = list(map(lambda x: x**2, filter(lambda y: y % 2 == 0, range(1000))))

class Modelo:
    def __init__(self, capas):
        self.capas = capas

    def forward(self, x):
        for capa in self.capas:
            x = capa(x)
        return x
"""


def main():
    parser = argparse.ArgumentParser(
        description="Visualiza la topología de espacios de código como arte ANSI."
    )
    parser.add_argument("file", nargs="?", help="Archivo de entrada (o pipe por stdin)")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["void", "length", "blocks", "flow", "scan", "drift", "pulse", "rain"],
        default="flow",
        help="Modo visual",
    )
    parser.add_argument(
        "-p",
        "--palette",
        choices=list(PALETTES.keys()),
        default="neon",
        help="Paleta de colores",
    )
    parser.add_argument("-a", "--animate", action="store_true", help="Activar animación")
    parser.add_argument(
        "-c", "--cycles", type=int, default=200, help="Frames de animación"
    )
    parser.add_argument(
        "-s", "--speed", type=float, default=0.08, help="Segundos entre frames"
    )
    parser.add_argument(
        "-f",
        "--fill",
        default="·",
        help="Carácter que rellena los espacios (default: medio punto)",
    )
    parser.add_argument(
        "--no-ghost",
        action="store_true",
        help="Ocultar el texto real y mostrar solo los espacios",
    )

    args = parser.parse_args()

    # Leer entrada: archivo > pipe > sample por defecto
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error al leer archivo: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
        if not content:
            content = SAMPLE_CODE
    else:
        content = SAMPLE_CODE

    render_spaces(
        content,
        mode=args.mode,
        palette=args.palette,
        animate=args.animate,
        cycles=args.cycles,
        speed=args.speed,
        fill_char=args.fill,
        ghost=not args.no_ghost,
    )


if __name__ == "__main__":
    main()
