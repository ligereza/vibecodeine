#!/usr/bin/env python3
"""Issue -> PNG en MAK, sin manos: paleta + render Blender headless.

Camino v2 (self-hosted MAK, sin Photoshop/droplet): descarga ya hecha por
el workflow (issue_descarga_ig.yml) entrega una imagen local; este script
hace lo que hacia src/flujo/eventos/flyer_auto.py del lado Windows pero
para el espejo MAK (RD.blend en /home/mak/RD/AUTOMATIZACION/):

1. Paleta de color dominante (portado 1:1 de flyer_auto._extract_palette)
   -> palette_ig.png + palette_ig.json en --out.
2. Render Blender headless de RD.blend: inyecta la imagen
   descargada en el/los material(es) que usa la convencion real de
   flyer_auto/blender_nodes.py (ver _buscar_materiales_flyer en
   src/flujo/eventos/blender_nodes.py): TODO nodo ShaderNodeTexImage cuyo
   `image.name` contiene "flyer_final" (sin importar mayusculas). NO se
   adivino un nombre de material nuevo -- es la unica convencion real
   encontrada en el codigo existente. Ver el reporte de la tarea para la
   unica cosa sin verificar: si RD.blend en MAK respeta esa misma
   convencion (no se pudo abrir el .blend real, solo vive en MAK).

Settings anti-OOM para GPU 1650 4GB (Cycles CUDA, nunca CPU/EEVEE): si
Blender se queda sin VRAM, el script FALLA con mensaje claro -- no cae a
CPU ni a EEVEE (la VRAM la puede estar usando ollama; liberarla es
responsabilidad del paso anterior del workflow, no de este script).

Uso:
    python3 tools/render_flyer_mak.py --imagen RUTA.jpg --out DIR \
        [--base /home/mak/RD/AUTOMATIZACION] [--blender /home/mak/blender/blender]

Imprime SIEMPRE una ultima linea `RENDER_OK: <ruta>` o
`RENDER_FALLO: <motivo>` para que el caller (workflow) parsee el resultado.
Sin dependencias nuevas: stdlib + Pillow (ya es dependencia del repo).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_BASE = "/home/mak/RD/AUTOMATIZACION"
DEFAULT_BLENDER = "/home/mak/blender/blender"
BLEND_FILE = "RD.blend"  # el real; "RD.blend" era config legacy que nunca existio

# Convencion real (NO adivinada) de src/flujo/eventos/blender_nodes.py
# _buscar_materiales_flyer(): el nodo de textura que trae el flyer tiene
# una imagen cuyo nombre contiene esta cadena.
MATERIAL_IMAGE_MARKER = "flyer_final"

RENDER_TIMEOUT_S = 900.0


def extract_palette(
    image_path: Path,
    palette_png: Path,
    palette_json: Path,
    colors_count: int = 6,
) -> list[str]:
    """Color dominante -> swatch PNG + JSON.

    Portado 1:1 de src/flujo/eventos/flyer_auto.py:_extract_palette
    (adaptive palette PIL, suficiente para direccion de arte rapida).
    """
    from PIL import Image, ImageDraw

    img = Image.open(image_path).convert("RGB")
    thumb = img.copy()
    thumb.thumbnail((240, 240))
    pal = thumb.convert("P", palette=Image.Palette.ADAPTIVE, colors=max(1, colors_count))
    palette = pal.getpalette() or []
    counts = pal.getcolors(maxcolors=240 * 240) or []
    counts = sorted(counts, reverse=True)[:colors_count]
    hex_colors: list[str] = []
    for _count, idx in counts:
        base = idx * 3
        if base + 2 < len(palette):
            rgb = tuple(palette[base:base + 3])
            hex_colors.append("#%02x%02x%02x" % rgb)

    if not hex_colors:
        hex_colors = ["#000000"]

    swatch_w, swatch_h = 140, 90
    out = Image.new("RGB", (swatch_w * len(hex_colors), swatch_h), "white")
    draw = ImageDraw.Draw(out)
    for i, color in enumerate(hex_colors):
        x = i * swatch_w
        draw.rectangle([x, 0, x + swatch_w, swatch_h], fill=color)
        draw.text((x + 10, swatch_h - 22), color.upper(), fill="white")
    palette_png.parent.mkdir(parents=True, exist_ok=True)
    out.save(palette_png)
    palette_json.write_text(json.dumps({"colors": hex_colors}, indent=2), encoding="utf-8")
    return hex_colors


def build_blender_python_expr(imagen_path: Path, output_path: Path) -> str:
    """Codigo Python inline para `blender --python-expr`.

    Fuerza Cycles/CUDA + settings anti-OOM (GPU 1650 4GB), inyecta la
    imagen descargada en TODO material con el marcador MATERIAL_IMAGE_MARKER
    y renderiza still a output_path. Si no encuentra el material, levanta
    SystemExit('NO_MATERIAL_FLYER_FINAL') -- Blender sale con codigo != 0 y
    el caller lo reporta como RENDER_FALLO (nunca cae a CPU/EEVEE).
    """
    imagen_lit = repr(str(imagen_path))
    salida_lit = repr(str(output_path))
    marcador_lit = repr(MATERIAL_IMAGE_MARKER)
    return (
        "import bpy\n"
        "scene = bpy.context.scene\n"
        "scene.render.engine = 'CYCLES'\n"
        "cprefs = bpy.context.preferences.addons['cycles'].preferences\n"
        "cprefs.compute_device_type = 'CUDA'\n"
        "cprefs.get_devices()\n"
        "_gpu_found = False\n"
        "for _d in cprefs.devices:\n"
        "    _d.use = (_d.type == 'CUDA')\n"
        "    _gpu_found = _gpu_found or _d.type == 'CUDA'\n"
        "if not _gpu_found:\n"
        "    raise SystemExit('NO_CUDA_DEVICE')\n"
        "scene.cycles.device = 'GPU'\n"
        "scene.cycles.samples = 512\n"
        # anti-OOM GPU 1650 4GB (CLAUDE.md): simplify + texture limit render
        # 2048 + auto tile 512 + sin persistent data.
        "scene.render.use_simplify = True\n"
        "scene.cycles.texture_limit_render = '2048'\n"
        "scene.cycles.use_auto_tile = True\n"
        "scene.cycles.tile_size = 512\n"
        "scene.render.use_persistent_data = False\n"
        f"_img = bpy.data.images.load({imagen_lit}, check_existing=True)\n"
        "_found = False\n"
        "for _mat in bpy.data.materials:\n"
        "    if not _mat.use_nodes:\n"
        "        continue\n"
        "    for _node in _mat.node_tree.nodes:\n"
        f"        if _node.type == 'TEX_IMAGE' and _node.image and {marcador_lit} in _node.image.name.lower():\n"
        "            _node.image = _img\n"
        "            _found = True\n"
        "if not _found:\n"
        "    raise SystemExit('NO_MATERIAL_FLYER_FINAL')\n"
        f"scene.render.filepath = {salida_lit}\n"
        "bpy.ops.render.render(write_still=True)\n"
    )


def build_blender_command(
    blender_exe: Path,
    blend_path: Path,
    imagen_path: Path,
    output_path: Path,
) -> list[str]:
    expr = build_blender_python_expr(imagen_path, output_path)
    return [str(blender_exe), "-b", str(blend_path), "--python-expr", expr]


def parse_render_marker(texto: str) -> tuple[bool, str] | None:
    """Busca la ultima linea RENDER_OK/RENDER_FALLO en un bloque de texto.

    Devuelve (ok, detalle) o None si no hay ninguna linea con el marcador.
    """
    ultima = None
    for linea in texto.splitlines():
        linea = linea.strip()
        if linea.startswith("RENDER_OK:") or linea.startswith("RENDER_FALLO:"):
            ultima = linea
    if ultima is None:
        return None
    ok = ultima.startswith("RENDER_OK:")
    detalle = ultima.split(":", 1)[1].strip()
    return ok, detalle


def run_render(
    blender_exe: Path,
    base_dir: Path,
    imagen_path: Path,
    output_path: Path,
) -> tuple[bool, str]:
    """Corre Blender headless. Devuelve (ok, detalle/motivo)."""
    blend_path = base_dir / BLEND_FILE
    if not blend_path.exists():
        return False, f"no existe {blend_path}"
    if not imagen_path.exists():
        return False, f"no existe la imagen de entrada {imagen_path}"

    cmd = build_blender_command(blender_exe, blend_path, imagen_path, output_path)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=RENDER_TIMEOUT_S,
        )
    except FileNotFoundError as exc:
        return False, f"no se pudo ejecutar blender: {exc}"
    except subprocess.TimeoutExpired:
        return False, f"blender no termino en {RENDER_TIMEOUT_S:.0f}s (timeout)"

    if proc.returncode != 0:
        salida = (proc.stderr or proc.stdout or "").strip()
        motivo = salida.splitlines()[-1] if salida else f"blender salio con codigo {proc.returncode}"
        return False, motivo

    if not output_path.exists():
        return False, "blender termino OK pero no genero el archivo de salida"

    return True, str(output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paleta + render Blender headless de un flyer descargado (MAK, v2 sin Photoshop).",
    )
    parser.add_argument("--imagen", required=True, type=Path, help="imagen descargada del post/reel de IG")
    parser.add_argument("--out", required=True, type=Path, help="directorio de salida (paleta + render)")
    parser.add_argument("--base", type=Path, default=Path(DEFAULT_BASE), help="carpeta con RD.blend y assets")
    parser.add_argument("--blender", type=Path, default=Path(DEFAULT_BLENDER), help="ejecutable de Blender")
    args = parser.parse_args(argv)

    imagen = args.imagen.resolve()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir = out_dir.resolve()

    if not imagen.exists():
        print(f"RENDER_FALLO: no existe la imagen de entrada {imagen}")
        return 1

    palette_png = out_dir / "palette_ig.png"
    palette_json = out_dir / "palette_ig.json"
    try:
        colores = extract_palette(imagen, palette_png, palette_json)
        print(f"paleta extraida: {colores}")
    except Exception as exc:
        print(f"RENDER_FALLO: paleta fallo: {exc}")
        return 1

    output_path = out_dir / "render_output.png"
    ok, detalle = run_render(args.blender, args.base.resolve(), imagen, output_path)
    if ok:
        print(f"RENDER_OK: {detalle}")
        return 0
    print(f"RENDER_FALLO: {detalle}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
