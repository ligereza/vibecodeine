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
    urls = re.findall(
        r'(?:data-src|src)="(https://[^"]+(?:imginn|scontent|cdninstagram)[^"]+)"', page)
    urls = [html_mod.unescape(u) for u in urls
            if "rsrc.php" not in u and (".jpg" in u or ".webp" in u)]
    # t51.82787-15 = media del post; t51.2885-19 = avatar del perfil
    post_media = [u for u in urls if "t51.82787" in u]
    candidatos = post_media or [u for u in urls if "t51.2885-19" not in u]
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


def _start_droplet(droplet_path: Path, psd_path: Path) -> None:
    if os.name == "nt":
        subprocess.Popen(["cmd", "/c", "start", "", str(droplet_path), str(psd_path)], shell=False)
    else:
        raise RuntimeError("Droplet launch is only supported on Windows.")


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


def _render_blender_texture(blender_exe: str, texture: Path, output: Path, template: Path | None) -> None:
    """Render headless via blender_render.py: textura -> material 'Texture' -> still."""
    script = Path(__file__).with_name("blender_render.py")
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [blender_exe, "--background", "--python", str(script), "--", str(texture), str(output)]
    if template is not None:
        cmd.append(str(template))
    subprocess.run(cmd, check=True)


def _render_blender_frame(blender_exe: str, blender_file: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Blender -o wants a path prefix; -f 1 appends frame number + extension.
    prefix = output_path.with_suffix("")
    cmd = [
        blender_exe,
        "-b",
        str(blender_file),
        "-o",
        str(prefix),
        "-f",
        "1",
    ]
    subprocess.run(cmd, check=True)
    expected = prefix.with_name(prefix.name + "0001.png")
    if expected.exists():
        if output_path.exists():
            output_path.unlink()
        expected.rename(output_path)
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
    """Download Instagram flyer and optionally launch Photoshop/Blender steps.

    Expected local files in base_dir:
    - Droplet_Flyer.exe
    - historia.psd
    - RD.blend (plantilla textura; si falta, fallback a cartelera.blend frame 1)
    - flyer_final.jpg (lo produce el Droplet; se espera activamente hasta 300s)
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
        if render_blender:
            if started_droplet:
                # espera activa al output del Droplet (antes: sleep ciego)
                if not _wait_for_file_update(flyer_final, droplet_launch_time):
                    raise TimeoutError(
                        f"El Droplet no produjo {flyer_final} en 300s; "
                        "revisa Photoshop antes de renderizar."
                    )
            if rd_blend.exists():
                # render con textura sobre la plantilla RD.blend
                texture = flyer_final if flyer_final.exists() else input_img
                _render_blender_texture(blender_exe, texture, render_out, rd_blend)
                blender_render = render_out
            else:
                # fallback legado: frame 1 de cartelera.blend
                if not blender_file.exists():
                    raise FileNotFoundError(
                        f"Missing Blender file: ni {rd_blend} ni {blender_file}"
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
