"""
Loom modes del telar: composiciones historicas de alfombra aplicadas al
patron de espacios del codigo digerido.

Gramatica curada en projects/cultura/dossiers/tapiz.md (seccion "Del dossier
al telar"): field (malla repetitiva de motivos), border (marcos concentricos
que encuadran un vacio central), medallion (foco central radiante) y mihrab
(nicho direccional, arco asimetrico apuntando hacia arriba).

Regla curatorial del dossier: toda pieza que use un motivo cita su significado
real. MOTIF_CITATIONS guarda esa cita de una linea por modo; el exportador SVG
la incrusta como <desc> y el render de terminal la imprime bajo el header.

Todo es deterministico: el indice de color de cada celda depende solo de su
posicion (x, y) en el canvas, no del largo del bloque. Asi la composicion es
estructural (como en el telar real) y no un gradiente accidental.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

LOOM_MODES: Tuple[str, ...] = ("field", "border", "medallion", "mihrab")

# Citas curadas del dossier (projects/cultura/dossiers/tapiz.md, "Lenguaje de
# motivos"). Una linea por modo, ASCII-only, con el significado real del motivo.
MOTIF_CITATIONS = {
    "field": (
        "field / gul: motivo octogonal repetido en el campo de la alfombra; "
        "sello tribal o totem de la familia tejedora (dossier tapiz)"
    ),
    "border": (
        "border / boteh: gota-cipres persa sembrada en los marcos que "
        "encuadran el campo; simboliza hoja, llama o vida (dossier tapiz)"
    ),
    "medallion": (
        "medallion: foco central de la gramatica medallon+borde persa; "
        "eco del jardin-paraiso que simboliza la vida eterna (dossier tapiz)"
    ),
    "mihrab": (
        "mihrab: nicho de oracion en arco de las alfombras de oracion, "
        "orientado hacia La Meca durante el rezo (dossier tapiz)"
    ),
}

# Ancho de banda (en celdas) de cada marco concentrico del modo border.
_BORDER_RING = 2


def loom_color_index(
    mode: str,
    x: int,
    y: int,
    n_cols: int,
    n_rows: int,
    n_colors: int,
) -> Optional[int]:
    """
    Indice de paleta para la celda (x, y) de un canvas n_cols x n_rows.

    Devuelve None cuando la celda pertenece a un vacio compositivo (el centro
    del modo border): el llamador la pinta apagada, no con paleta.
    """
    if n_colors <= 0:
        raise ValueError("n_colors debe ser positivo")
    if mode not in LOOM_MODES:
        raise ValueError(f"modo loom desconocido: {mode!r}")

    n_cols = max(n_cols, 1)
    n_rows = max(n_rows, 1)

    if mode == "field":
        # Malla repetitiva all-over: celdas de 4x2 en diagonal, como guls
        # sembrados en el campo. Solo depende de la posicion en la malla.
        return ((x // 4) + (y // 2)) % n_colors

    if mode == "border":
        # Marcos concentricos: profundidad = distancia al borde del canvas.
        # Cada _BORDER_RING celdas de profundidad cambian de color; el centro
        # (mas alla del ultimo marco) queda como vacio (None).
        depth = min(x, n_cols - 1 - x, y, n_rows - 1 - y)
        # Cantidad de marcos que caben sin comerse el centro: un tercio del
        # semieje menor, al menos un marco.
        max_depth = max(min(n_cols, n_rows) // 6, 1) * _BORDER_RING
        if depth >= max_depth:
            return None  # vacio central
        return (depth // _BORDER_RING) % n_colors

    cx = (n_cols - 1) / 2.0
    cy = (n_rows - 1) / 2.0

    if mode == "medallion":
        # Medallon central: anillos de color segun distancia radial al centro,
        # normalizada por semiejes (las celdas de terminal no son cuadradas,
        # la normalizacion la vuelve elipse como un medallon real).
        dx = (x - cx) / max(cx, 1.0)
        dy = (y - cy) / max(cy, 1.0)
        dist = math.sqrt(dx * dx + dy * dy)  # 0 centro .. ~1.41 esquina
        # Clamp (no modulo): los anillos exteriores saturan en el ultimo
        # color, como el campo solido que rodea un medallon real.
        return min(int(dist * n_colors), n_colors - 1)

    # mihrab: arco direccional apuntando hacia arriba. El foco esta en el
    # apice superior central; los anillos se abren hacia abajo como el nicho.
    # Asimetrico por construccion: no hay simetria vertical.
    dx = (x - cx) / max(cx, 1.0)
    dy = y / max(n_rows - 1, 1)
    dist = math.sqrt(dx * dx + dy * dy)  # 0 apice .. ~1.41 esquinas de abajo
    # Mismo clamp que el medallon: el pie de la alfombra es campo solido.
    return min(int(dist * n_colors), n_colors - 1)


def block_segments(
    mode: str,
    x0: int,
    y: int,
    length: int,
    n_cols: int,
    n_rows: int,
    n_colors: int,
) -> List[Tuple[int, Optional[int]]]:
    """
    Divide un bloque de espacios (fila y, columnas x0..x0+length-1) en
    segmentos consecutivos con el mismo indice loom.

    Devuelve una lista de (largo_del_segmento, indice_o_None) en orden.
    Asi un bloque que cruza un anillo del medallon se parte en dos colores.
    """
    segments: List[Tuple[int, Optional[int]]] = []
    for i in range(length):
        idx = loom_color_index(mode, x0 + i, y, n_cols, n_rows, n_colors)
        if segments and segments[-1][1] == idx:
            segments[-1] = (segments[-1][0] + 1, idx)
        else:
            segments.append((1, idx))
    return segments


def canvas_size(lines: List[str]) -> Tuple[int, int]:
    """Dimensiones (n_cols, n_rows) del canvas que ocupan las lineas."""
    n_rows = max(len(lines), 1)
    n_cols = max((len(line) for line in lines), default=1)
    return max(n_cols, 1), n_rows
