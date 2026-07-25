#!/usr/bin/env python3
"""Issue -> PNG en MAK, sin manos: paleta + render Blender headless.

Camino v3 (self-hosted MAK, sin Photoshop/droplet): descarga ya hecha por
el workflow (issue_descarga_ig.yml) entrega una imagen local; este script
reproduce EXACTO el camino real de WIN
(src/flujo/eventos/flyer_auto.py:_render_blender_compuesto), no un swap de
nodo artesanal:

1. Paleta de color dominante (portado 1:1 de flyer_auto._extract_palette)
   -> palette_ig.png + palette_ig.json en --out.
2. Color predominante-pero-claro (portado 1:1 de
   flyer_auto._write_predominant_color) -> RESULTADOS/color_predominante.png
   junto al .blend (RD.blend lo linkea para el vidrio decorativo).
3. Genera un script .py TEMPORAL (no --python-expr inline) que, corriendo
   DENTRO de Blender, importa el modulo REAL
   src/flujo/eventos/blender_nodes.py (sys.path.insert a esa carpeta; el
   modulo no importa bpy a nivel de modulo, solo dentro de sus funciones,
   asi que es importable tal cual sin portar nada a mano) y llama:
   - blender_nodes._buscar_materiales_flyer() -- la MISMA busqueda por
     convencion "flyer_final" que ya vive en el codigo (Material.002 +
     Material.008 en el .blend real).
   - blender_nodes._color_predominante_bpy() / _repuntar_color_predominante()
     -- leen y re-apuntan el datablock color_predominante.png (mismo color
     que recolorea el vidrio decorativo, evita el bug de color viejo).
   - blender_nodes.hue_de_rgb() + blender_nodes.build_flyer_nodes() -- el
     update/build POR NODOS real (paleta + imagen + fit-width mapping +
     hue), NO un swap de un solo TEX_IMAGE.
   El script agrega ADEMAS los settings anti-OOM (Cycles CUDA, 512 samples,
   simplify, tile 512, sin persistent data) porque WIN no los necesita
   (mas VRAM) pero la GPU 1650 4GB de MAK si.

Requiere en --base: cartelera.blend + FRAME2.png (la convencion real de
FRAME2.png documentada en flyer_auto/blender_nodes; sin FRAME2.png el
camino "por nodos" no aplica y este script FALLA claro, nunca cae a un
swap artesanal que renderiza plano).

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
import tempfile
from pathlib import Path

DEFAULT_BASE = "/home/mak/RD/AUTOMATIZACION"
DEFAULT_BLENDER = "/home/mak/blender/blender"
BLEND_FILE = "cartelera.blend"
FRAME_FILE = "FRAME2.png"
COLOR_PNG_RELATIVE = Path("RESULTADOS") / "color_predominante.png"

# Carpeta real de src/flujo/eventos (contiene blender_nodes.py + blender_gpu.py),
# derivada de este archivo -- NO se porta la logica a mano, se importa tal cual.
EVENTOS_DIR = Path(__file__).resolve().parents[1] / "src" / "flujo" / "eventos"

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


def write_predominant_color(image_path: Path, out_png: Path) -> str:
    """Color predominante-pero-claro del flyer -> PNG solido que el .blend linkea.

    Portado 1:1 de src/flujo/eventos/flyer_auto.py:_write_predominant_color
    (mismo criterio: mas luminoso entre los colores con peso real, aclarado
    25% hacia blanco). El .blend real usa este mismo PNG para recolorear el
    vidrio decorativo (Decorative Glass 05), via
    blender_nodes._repuntar_color_predominante.
    """
    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    thumb = img.copy()
    thumb.thumbnail((240, 240))
    pal = thumb.convert("P", palette=Image.Palette.ADAPTIVE, colors=6)
    palette = pal.getpalette() or []
    counts = sorted(pal.getcolors(240 * 240) or [], reverse=True)[:6]
    colores = []
    for cnt, idx in counts:
        r, g, b = palette[idx * 3:idx * 3 + 3]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        colores.append((cnt, lum, (r, g, b)))
    if not colores:
        colores = [(1, 0.0, (0, 0, 0))]
    colores.sort(key=lambda c: (-c[1], -c[0]))
    candidato = next((c for c in colores if c[0] > counts[0][0] * 0.15), colores[0])
    r, g, b = candidato[2]
    r, g, b = (int(r + (255 - r) * 0.25), int(g + (255 - g) * 0.25), int(b + (255 - b) * 0.25))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (512, 512), (r, g, b)).save(out_png)
    return f"#{r:02x}{g:02x}{b:02x}"


def build_blender_script(
    frame_path: Path,
    imagen_path: Path,
    color_png_path: Path,
    output_path: Path,
) -> str:
    """Script Python REAL para `blender --python <script>` (temporal, no expr).

    Importa src/flujo/eventos/blender_nodes.py tal cual (sin portar su
    logica) y ejecuta el mismo update/build por nodos que WIN, mas los
    settings anti-OOM (Cycles CUDA, 512 samples, simplify, tile 512, sin
    persistent data) que la GPU 1650 4GB de MAK necesita y WIN no.
    """
    eventos_dir_lit = repr(str(EVENTOS_DIR))
    frame_lit = repr(str(frame_path))
    imagen_lit = repr(str(imagen_path))
    color_png_lit = repr(str(color_png_path))
    salida_lit = repr(str(output_path))
    return (
        "import sys\n"
        f"sys.path.insert(0, {eventos_dir_lit})\n"
        "import bpy\n"
        "import blender_nodes\n"
        "from blender_gpu import force_gpu\n"
        "\n"
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
        "\n"
        f"_frame_path = {frame_lit}\n"
        f"_imagen_path = {imagen_lit}\n"
        f"_color_png_path = {color_png_lit}\n"
        "import os\n"
        "if os.path.exists(_color_png_path):\n"
        "    _rgb = blender_nodes._color_predominante_bpy(_color_png_path)\n"
        "    blender_nodes._repuntar_color_predominante(_color_png_path)\n"
        "else:\n"
        "    _rgb = (0, 254, 254)\n"
        "_hue = blender_nodes.hue_de_rgb(_rgb)\n"
        "print(f'Color predominante RGB={_rgb} hue={_hue:.4f}')\n"
        "\n"
        "_materiales = blender_nodes._buscar_materiales_flyer()\n"
        "for _mat, _nodo in _materiales:\n"
        "    _modo = blender_nodes.build_flyer_nodes(_mat, _nodo, _frame_path, _imagen_path, _hue)\n"
        "    print(f\"Material '{_mat.name}' {_modo} por nodos (sin Photoshop).\")\n"
        "\n"
        "print(f'GPU: {force_gpu()}')\n"
        f"scene.render.filepath = {salida_lit}\n"
        "bpy.ops.render.render(write_still=True)\n"
    )


def build_blender_command(
    blender_exe: Path,
    blend_path: Path,
    script_path: Path,
) -> list[str]:
    return [str(blender_exe), "-b", str(blend_path), "--python", str(script_path)]


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
    """Corre Blender headless (script real por nodos). Devuelve (ok, detalle/motivo)."""
    blend_path = base_dir / BLEND_FILE
    if not blend_path.exists():
        return False, f"no existe {blend_path}"
    if not imagen_path.exists():
        return False, f"no existe la imagen de entrada {imagen_path}"

    frame_path = base_dir / FRAME_FILE
    if not frame_path.exists():
        return False, f"no existe {frame_path} (requerido para el camino por nodos)"

    color_png_path = base_dir / COLOR_PNG_RELATIVE
    script_text = build_blender_script(frame_path, imagen_path, color_png_path, output_path)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_render_flyer_mak.py", delete=False, encoding="utf-8",
    ) as tmp:
        tmp.write(script_text)
        script_path = Path(tmp.name)

    try:
        cmd = build_blender_command(blender_exe, blend_path, script_path)
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
    finally:
        script_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paleta + render Blender headless por nodos de un flyer descargado (MAK, v3 camino real).",
    )
    parser.add_argument("--imagen", required=True, type=Path, help="imagen descargada del post/reel de IG")
    parser.add_argument("--out", required=True, type=Path, help="directorio de salida (paleta + render)")
    parser.add_argument("--base", type=Path, default=Path(DEFAULT_BASE), help="carpeta con cartelera.blend y assets")
    parser.add_argument("--blender", type=Path, default=Path(DEFAULT_BLENDER), help="ejecutable de Blender")
    args = parser.parse_args(argv)

    imagen = args.imagen.resolve()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir = out_dir.resolve()
    base = args.base.resolve()

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

    try:
        color_png_path = base / COLOR_PNG_RELATIVE
        hex_color = write_predominant_color(imagen, color_png_path)
        print(f"color predominante: {hex_color}")
    except Exception as exc:
        print(f"RENDER_FALLO: color predominante fallo: {exc}")
        return 1

    output_path = out_dir / "render_output.png"
    ok, detalle = run_render(args.blender, base, imagen, output_path)
    if ok:
        print(f"RENDER_OK: {detalle}")
        return 0
    print(f"RENDER_FALLO: {detalle}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
