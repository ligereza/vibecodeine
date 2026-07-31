# -*- coding: utf-8 -*-
"""Vector aesthetics for laser and plotter: the vpype chain, wrapped.

One tool, two lives (the plano/rider pattern): as an OPERATOR tool it turns
any image into plotter/laser-ready vector art -- `hatched` converts dark
zones into hatching (a solid logo stops arriving hollow), `flow` converts an
image into long continuous flow-field strokes (few pen-ups, laser-friendly).
As a PORTFOLIO feeder, `lote` walks a material folder and writes SVGs plus a
manifest into the repo paths that `contrato_archivo.desde_laser` reads, so
each derived piece enters the archive linked to its curated work.

External-tool pattern (same as Blender/Edge elsewhere in flujo): vpype is a
pip-installed CLI, this module shells out to it and fails with instructions,
never with a traceback. Determinism: `flow` accepts a seed and `lote` derives
it from the file name, so the same material produces the same piece.

Install (once), measured 2026-07-30 -- the PyPI builds of both plugins are
broken against numpy 2.x (flow: kdtree TypeError; hatched: shapely empty
MultiLineString), so the pin and the git build are REQUIRED, not preference:
    pip install "vpype[all]" "numpy<2"
    pip install "git+https://github.com/plottertools/hatched"
    pip install "git+https://github.com/serycjon/vpype-flow-imager"

Verified state per mode (2026-07-30, this machine): hatched WORKS (168 pts
on the test image, within budget). flow_img installs and registers but two
runs on a 400px test exceeded 10 minutes without finishing -- treat flow as
experimental until someone measures a completed run; hatched is the proven
route.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _vpype() -> str | None:
    return shutil.which("vpype")


def verificar() -> dict:
    """What of the chain is actually present, measured by running it."""
    estado = {"vpype": False, "hatched": False, "flow": False}
    exe = _vpype()
    if not exe:
        return estado
    estado["vpype"] = True
    try:
        ayuda = subprocess.run([exe, "--help"], capture_output=True, text=True,
                               timeout=30).stdout
    except Exception:
        return estado
    estado["hatched"] = "hatched" in ayuda
    estado["flow"] = "flow_img" in ayuda
    return estado


def puntos(svg: Path) -> int:
    """Vertices de polilinea del SVG: la aproximacion honesta al costo en
    puntos ILDA. El toolkit del usuario fija 600-1000 puntos por frame a
    30 kpps; un SVG medio aplanado trae 15.000-20.000, asi que presupuestar
    no es opcional (docs/laser/TOOLKIT_INDICE.md)."""
    import re
    texto = svg.read_text(encoding="utf-8", errors="replace")
    # vpype emite tres formas: <line> suelto (2 puntos), <polyline points>
    # (un punto por par x,y) y <path d> (un punto por par de coordenadas).
    n = 2 * len(re.findall(r"<line\b", texto))
    for m in re.finditer(r'points="([^"]+)"', texto):
        n += len(re.findall(r"-?\d[\d.eE+-]*[,\s]+-?\d", m.group(1)))
    for m in re.finditer(r'\bd="([^"]+)"', texto):
        n += len(re.findall(r"-?\d[\d.eE+-]*[,\s]+-?\d", m.group(1)))
    return n


# Tolerancias de linesimplify (mm) que se prueban EN ORDEN hasta caber en el
# presupuesto. Deterministas: mismo input, mismo resultado.
_TOLERANCIAS = (0.2, 0.5, 1.0, 2.0, 4.0, 8.0)


def _correr(args: "list[str]") -> None:
    exe = _vpype()
    if not exe:
        raise RuntimeError(
            "vpype no esta instalado. Instalar con:\n"
            '  pip install "vpype[all]" hatched\n'
            '  pip install "git+https://github.com/serycjon/vpype-flow-imager"')
    proc = subprocess.run([exe, *args], capture_output=True, text=True,
                          timeout=600)
    if proc.returncode != 0:
        raise RuntimeError("vpype fallo:\n" + (proc.stderr or proc.stdout)[-800:])


def _ajustar_al_presupuesto(salida: Path, presupuesto: int) -> dict:
    """Simplifica EN ORDEN de tolerancias hasta caber en el presupuesto.

    Devuelve {puntos, tolerancia, dentro}: si ni la tolerancia mas gruesa
    alcanza, `dentro` queda False y el operador decide -- nunca se recorta
    geometria en silencio (la regla de no-silent-caps del repo).
    """
    actual = puntos(salida)
    tol_usada = None
    for tol in _TOLERANCIAS:
        if actual <= presupuesto:
            break
        _correr(["read", str(salida), "linesimplify", "-t", f"{tol}mm",
                 "linemerge", "linesort", "write", str(salida)])
        actual = puntos(salida)
        tol_usada = tol
    return {"puntos": actual, "tolerancia_mm": tol_usada,
            "dentro": actual <= presupuesto}


def hatched(imagen: Path, salida: Path, pitch: int = 4,
            niveles: "tuple[int, int, int]" = (64, 128, 192),
            presupuesto: int = 800) -> dict:
    """Dark zones become hatching: the plotterist technique, laser-ready.

    linemerge+linesort minimise pen-up travel (blanked jumps); the point
    budget then simplifies until the frame is drawable at 30 kpps.
    """
    salida.parent.mkdir(parents=True, exist_ok=True)
    _correr(["hatched", "--levels", *map(str, niveles), "--pitch", str(pitch),
             str(imagen), "linemerge", "linesort", "write", str(salida)])
    return _ajustar_al_presupuesto(salida, presupuesto)


def flow(imagen: Path, salida: Path, semilla: int = 7,
         escala_ruido: float | None = None, presupuesto: int = 800) -> dict:
    """The image becomes long continuous flow-field strokes.

    Seeded: same image + same seed = same drawing (the timecode-as-seed
    thesis applied to laser material).
    """
    salida.parent.mkdir(parents=True, exist_ok=True)
    args = ["flow_img", "--seed", str(semilla)]
    if escala_ruido is not None:
        args += ["--noise_coeff", str(escala_ruido)]
    args += [str(imagen), "linemerge", "linesort", "write", str(salida)]
    _correr(args)
    return _ajustar_al_presupuesto(salida, presupuesto)


def _semilla_de(nombre: str) -> int:
    return int.from_bytes(hashlib.sha256(nombre.encode()).digest()[:4], "big")


def lote(carpeta: Path, destino: Path, manifiesto: Path,
         modo: str = "flow", limite: int | None = None) -> "list[dict]":
    """Walk a material folder, derive one laser piece per image, write the
    manifest `contrato_archivo.desde_laser` reads.

    The join key with the curated field is the file STEM (the IG media id):
    campo.json's `archivo` carries `posts/<media_id>.mp4`, the material
    folder carries `<media_id>.jpg` -- same digits, same work.
    """
    imagenes = sorted(p for p in carpeta.iterdir()
                      if p.suffix.lower() in EXTENSIONES)
    if limite:
        imagenes = imagenes[:limite]
    filas = []
    for img in imagenes:
        salida = destino / f"{img.stem}.svg"
        try:
            if modo == "hatched":
                medida = hatched(img, salida)
            else:
                medida = flow(img, salida, semilla=_semilla_de(img.stem))
        except RuntimeError as e:
            filas.append({"stem": img.stem, "error": str(e)[:200]})
            continue
        filas.append({
            "stem": img.stem,
            "src": salida.as_posix(),
            "modo": modo,
            "semilla": _semilla_de(img.stem) if modo == "flow" else None,
            "puntos": medida["puntos"],
            "dentro_presupuesto": medida["dentro"],
        })
    manifiesto.parent.mkdir(parents=True, exist_ok=True)
    manifiesto.write_text(
        json.dumps({"version": 1, "modo": modo, "piezas": filas},
                   ensure_ascii=False, indent=1),
        encoding="utf-8", newline="\n")
    return filas
