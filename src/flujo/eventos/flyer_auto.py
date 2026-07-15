"""EVENTOS Instagram flyer download + local Photoshop/Blender handoff.

Default behavior is safe:
- downloads Instagram image
- updates input_ig.jpg
- extracts a small palette preview
- does NOT open Photoshop or Blender unless explicit flags are used
"""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WINDOWS_BASE = Path(r"C:\rd\AUTOMATIZACION")


@dataclass
class EventFlyerResult:
    ok: bool
    shortcode: str = ""
    base_dir: Path | None = None
    downloaded_image: Path | None = None
    input_image: Path | None = None
    palette_image: Path | None = None
    palette_json: Path | None = None
    blender_file: Path | None = None
    blender_render: Path | None = None
    droplet_path: Path | None = None
    psd_path: Path | None = None
    droplet_started: bool = False
    blender_started: bool = False
    blender_rendered: bool = False
    productora: dict | None = None  # resultado de productoras.identify()
    error: str = ""


def extract_instagram_shortcode(url: str) -> str:
    """Extract shortcode from Instagram post/reel URL."""
    text = (url or "").strip()
    patterns = [r"instagram\.com/(?:[^/]+/)?p/([^/?#]+)", r"instagram\.com/(?:[^/]+/)?reel/([^/?#]+)"]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    for marker in ("/p/", "/reel/"):
        if marker in text:
            return text.split(marker, 1)[1].split("/", 1)[0].split("?", 1)[0]
    raise ValueError("Invalid Instagram URL. Expected /p/ or /reel/ link.")


def default_base_dir() -> Path:
    env = os.getenv("FLUJO_EVENTOS_AUTOMATIZACION_DIR", "").strip()
    if env:
        return Path(env)
    return DEFAULT_WINDOWS_BASE if os.name == "nt" else Path.cwd() / "eventos_automatizacion"


def _first_downloaded_image(temp_dir: Path) -> Path:
    candidates: list[str] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        candidates.extend(glob.glob(str(temp_dir / ext)))
    if not candidates:
        raise FileNotFoundError("No image was downloaded from Instagram.")
    return Path(sorted(candidates)[0]).resolve()


def _download_instagram(shortcode: str, temp_dir: Path) -> Path:
    import instaloader

    loader = instaloader.Instaloader(
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
    )
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=str(temp_dir))
    return _first_downloaded_image(temp_dir)


_MIRROR_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _download_via_mirror(shortcode: str, temp_dir: Path) -> Path:
    """Fallback sin login: mirror publico (IG bloquea instaloader anonimo desde 2026).

    Mejor esfuerzo sobre un servicio de terceros: si el mirror cambia su HTML o
    muere, volver a instaloader con sesion logueada (instaloader --login).
    """
    import html as html_mod
    import urllib.request

    def _fetch(url: str, referer: str | None = None) -> bytes:
        headers = {"User-Agent": _MIRROR_UA}
        if referer:
            headers["Referer"] = referer
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()

    page = _fetch(f"https://imginn.com/p/{shortcode}/").decode("utf-8", "replace")
    # 1) preferir imagenes DENTRO del contenedor del post (swiper-slide);
    #    fuera de el aparecen avatares (t51.82787-19 en posts collab) y thumbs
    slides = re.findall(
        r'<div class="swiper-slide[^>]*>.*?(?:data-src|src)="(https://[^"]+)"', page, re.DOTALL)
    urls = slides or re.findall(
        r'(?:data-src|src)="(https://[^"]+(?:imginn|scontent|cdninstagram)[^"]+)"', page)
    urls = [html_mod.unescape(u) for u in urls
            if "rsrc.php" not in u and "lazy.jpg" not in u and (".jpg" in u or ".webp" in u)]
    # t51.82787-15 = media del post; -19 y t51.2885-19 = avatares (tambien en collab)
    post_media = [u for u in urls if "t51.82787-15" in u]
    candidatos = post_media or [u for u in urls
                                if "t51.2885-19" not in u and "t51.82787-19" not in u]
    if not candidatos:
        raise FileNotFoundError("El mirror no devolvio imagen del post.")
    data = _fetch(candidatos[0], referer="https://imginn.com/")
    out = temp_dir / f"mirror_{shortcode}.jpg"
    out.write_bytes(data)
    return out


def _extract_palette(image_path: Path, palette_png: Path, palette_json: Path, colors_count: int = 6) -> list[str]:
    """Extract dominant colors and write a swatch PNG + JSON list."""
    from PIL import Image, ImageDraw

    img = Image.open(image_path).convert("RGB")
    thumb = img.copy()
    thumb.thumbnail((240, 240))
    # Adaptive palette is good enough for quick art direction.
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


def _photoshop_running() -> bool:
    if os.name != "nt":
        return False
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Photoshop.exe"],
                             capture_output=True, text=True, timeout=15).stdout
        return "Photoshop.exe" in out
    except Exception:
        return False


def _start_droplet(droplet_path: Path, psd_path: Path) -> None:
    if os.name != "nt":
        raise RuntimeError("Droplet launch is only supported on Windows.")
    if _photoshop_running():
        # varias instancias de Photoshop compiten y el droplet nunca entrega
        # (comprobado 2026-07-08: 5 instancias colgadas); mejor fallar claro
        raise RuntimeError(
            "Photoshop ya esta abierto: cierra las instancias antes de lanzar "
            "el droplet (multiples instancias se traban entre si)."
        )
    subprocess.Popen(["cmd", "/c", "start", "", str(droplet_path), str(psd_path)], shell=False)


def _write_predominant_color(image_path: Path, out_png: Path) -> str:
    """Color predominante-pero-claro del flyer -> PNG solido que RD.blend linkea."""
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
    # el mas luminoso entre los que tienen peso real (>15% del dominante)
    colores.sort(key=lambda c: (-c[1], -c[0]))
    candidato = next((c for c in colores if c[0] > counts[0][0] * 0.15), colores[0])
    r, g, b = candidato[2]
    # aclarar 25% hacia blanco
    r, g, b = (int(r + (255 - r) * 0.25), int(g + (255 - g) * 0.25), int(b + (255 - b) * 0.25))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (512, 512), (r, g, b)).save(out_png)
    return f"#{r:02x}{g:02x}{b:02x}"


def _open_blender(blender_exe: str, blender_file: Path) -> None:
    subprocess.Popen([blender_exe, str(blender_file)], shell=False)


def _wait_for_file_update(path: Path, after_time: float, timeout_s: float = 300.0, poll_s: float = 2.0) -> bool:
    """Espera activa a que `path` exista con mtime posterior a `after_time`."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            if path.exists() and path.stat().st_mtime >= after_time:
                return True
        except OSError:
            pass  # el Droplet puede estar escribiendo el archivo justo ahora
        time.sleep(poll_s)
    return False




_BLENDER_GPU_SCRIPT = Path(__file__).resolve().parent / "blender_gpu.py"
_BLENDER_NODES_SCRIPT = Path(__file__).resolve().parent / "blender_nodes.py"


def _render_blender_compuesto(
    blender_exe: str,
    blender_file: Path,
    frame_png: Path,
    input_img: Path,
    color_png: Path,
    output_path: Path,
) -> Path:
    """Render SIN Photoshop: blender_nodes.py recompone el material en memoria
    (FRAME2 + input + recolor por color predominante) y renderiza."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        blender_exe,
        "-b",
        str(blender_file),
        "--python",
        str(_BLENDER_NODES_SCRIPT),
        "--",
        "--frame",
        str(frame_png),
        "--input",
        str(input_img),
        "--color-png",
        str(color_png),
        "--salida",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path


def _render_blender_frame(blender_exe: str, blender_file: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Blender -o wants a path prefix; -f 1 appends frame number + extension.
    prefix = output_path.with_suffix("")
    # remove stale frames so a prior run cannot masquerade as this render
    for stale in prefix.parent.glob(prefix.name + "0001.*"):
        stale.unlink()
    cmd = [
        blender_exe,
        "-b",
        str(blender_file),
        # --python corre ANTES del render: fuerza GPU (OptiX/CUDA) en memoria,
        # no toca ni guarda el .blend (blender_gpu.py, agregado 2026-07-10;
        # sin esto Cycles renderiza en CPU por default).
        "--python",
        str(_BLENDER_GPU_SCRIPT),
        "-o",
        str(prefix),
        "-f",
        "1",
    ]
    subprocess.run(cmd, check=True)
    # Blender appends frame number + extension per the .blend's file_format
    # (not always PNG); pick up whatever it actually wrote.
    produced = sorted(prefix.parent.glob(prefix.name + "0001.*"))
    if not produced:
        raise FileNotFoundError(
            f"Blender no produjo {prefix.name}0001.*; revisa el formato de salida del .blend."
        )
    frame_file = produced[0]
    if output_path.exists():
        output_path.unlink()
    frame_file.rename(output_path)
    return output_path


def run_eventos_flyer_auto(
    url: str,
    base_dir: Path | None = None,
    run_droplet: bool = False,
    open_blender: bool = False,
    render_blender: bool = False,
    blender_exe: str = "blender",
    keep_temp: bool = False,
    sleep_seconds: float = 2.0,
) -> EventFlyerResult:
    """Download Instagram flyer and optionally launch Blender (y legado Photoshop).

    Expected local files in base_dir:
    - RD.blend (plantilla textura; si falta, fallback a cartelera.blend frame 1)
    - FRAME2.png: si existe junto a RD.blend, el render compone por NODOS
      (blender_nodes.py: FRAME2 + input + recolor) y NO usa Photoshop.
    - Droplet_Flyer.exe + historia.psd + flyer_final.jpg: solo camino legado
      (sin FRAME2.png), con espera activa de hasta 300s al Droplet.
    - input_ig.jpg will be replaced/created
    - palette_ig.png and palette_ig.json will be written
    - render_output.png (salida del render con RD.blend)
    """
    base = (base_dir or default_base_dir()).resolve()
    droplet = base / "Droplet_Flyer.exe"
    psd = base / "historia.psd"
    blender_file = base / "cartelera.blend"
    blender_render = base / "preview_cartelera.png"
    rd_blend = base / "RD.blend"
    flyer_final = base / "flyer_final.jpg"  # output real del Droplet de Photoshop
    render_out = base / "render_output.png"
    input_img = base / "input_ig.jpg"
    palette_png = base / "palette_ig.png"
    palette_json = base / "palette_ig.json"
    temp_dir = base / "temp_flyer"

    try:
        shortcode = extract_instagram_shortcode(url)
        base.mkdir(parents=True, exist_ok=True)
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            downloaded = _download_instagram(shortcode, temp_dir)
        except Exception:
            # IG bloquea instaloader anonimo; intentar mirror publico
            downloaded = _download_via_mirror(shortcode, temp_dir)

        if input_img.exists():
            input_img.unlink()
        shutil.copy(downloaded, input_img)
        _extract_palette(input_img, palette_png, palette_json)
        # RD.blend linkea RESULTADOS/color_predominante.png como material
        _write_predominant_color(input_img, base / "RESULTADOS" / "color_predominante.png")

        # identificacion de productora (wire-in opcion B, confirmado por el
        # usuario): 1 llamada Gemini vision para lo semantico. NUNCA fatal:
        # si Gemini esta caido/sin quota, el render sigue igual.
        productora_res: dict | None = None
        try:
            from .productoras import identify as _identificar_productora
            data_dir = Path(__file__).resolve().parents[3] / "data" / "productoras"
            productora_res = _identificar_productora(input_img, data_dir)
        except Exception as exc:  # noqa: BLE001 -- aviso, no bloqueo
            print(f"[aviso] identificacion de productora omitida: {exc}")
        time.sleep(max(0.0, sleep_seconds))

        started_droplet = False
        droplet_launch_time = 0.0
        if run_droplet:
            if not droplet.exists():
                raise FileNotFoundError(f"Missing droplet: {droplet}")
            if not psd.exists():
                raise FileNotFoundError(f"Missing PSD: {psd}")
            droplet_launch_time = time.time()
            _start_droplet(droplet, psd)
            started_droplet = True

        started_blender = False
        rendered_blender = False
        if open_blender and not blender_file.exists():
            raise FileNotFoundError(f"Missing Blender file: {blender_file}")
        frame2 = base / "FRAME2.png"
        if render_blender:
            if rd_blend.exists() and frame2.exists():
                # camino SIN Photoshop (2026-07-10): blender_nodes.py compone
                # FRAME2 + input + recolor en nodos; flyer_final.jpg y el
                # Droplet dejan de ser necesarios.
                _render_blender_compuesto(
                    blender_exe, rd_blend, frame2, input_img,
                    base / "RESULTADOS" / "color_predominante.png", render_out,
                )
                blender_render = render_out
            elif rd_blend.exists():
                if started_droplet:
                    # legado con Droplet: espera activa a flyer_final.jpg
                    if not _wait_for_file_update(flyer_final, droplet_launch_time):
                        raise TimeoutError(
                            f"El Droplet no produjo {flyer_final} en 300s; "
                            "revisa Photoshop antes de renderizar."
                        )
                elif not (flyer_final.exists()
                          and flyer_final.stat().st_mtime >= input_img.stat().st_mtime):
                    # sin Droplet, RD.blend linkea flyer_final.jpg de disco: exige
                    # uno fresco para ESTE evento (mtime >= input recien bajado a
                    # las 350), no un sobrante de un evento anterior.
                    raise FileNotFoundError(
                        f"RD.blend legado necesita un {flyer_final} fresco para este evento; "
                        "corre el Droplet (run_droplet=True) o provee FRAME2.png para el "
                        "camino sin Photoshop."
                    )
                # RD.blend linkea flyer_final.jpg desde disco (validado 2026-07-08)
                _render_blender_frame(blender_exe, rd_blend, render_out)
                blender_render = render_out
            else:
                # fallback legado: frame 1 de cartelera.blend
                if not blender_file.exists():
                    raise FileNotFoundError(
                        f"Missing Blender file: ni {rd_blend} ni {blender_file}"
                    )
                if started_droplet:
                    if not _wait_for_file_update(flyer_final, droplet_launch_time):
                        raise TimeoutError(
                            f"El Droplet no produjo {flyer_final} en 300s; "
                            "revisa Photoshop antes de renderizar."
                        )
                _render_blender_frame(blender_exe, blender_file, blender_render)
            rendered_blender = True
        if open_blender:
            _open_blender(blender_exe, blender_file)
            started_blender = True

        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return EventFlyerResult(
            ok=True,
            shortcode=shortcode,
            base_dir=base,
            downloaded_image=downloaded,
            input_image=input_img,
            palette_image=palette_png,
            palette_json=palette_json,
            blender_file=blender_file,
            blender_render=blender_render,
            droplet_path=droplet,
            psd_path=psd,
            droplet_started=started_droplet,
            blender_started=started_blender,
            blender_rendered=rendered_blender,
            productora=productora_res,
        )
    except Exception as exc:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return EventFlyerResult(
            ok=False,
            base_dir=base,
            input_image=input_img,
            palette_image=palette_png,
            palette_json=palette_json,
            blender_file=blender_file,
            blender_render=blender_render,
            droplet_path=droplet,
            psd_path=psd,
            error=str(exc),
        )
