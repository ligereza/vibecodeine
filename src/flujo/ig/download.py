import html as html_mod
import re
import time
import urllib.request
from pathlib import Path

SHORTCODE_RE = [
    re.compile(r"/(?:[A-Za-z0-9_.]+/)?p/([A-Za-z0-9_-]+)"),
    re.compile(r"/(?:[A-Za-z0-9_.]+/)?reels?/([A-Za-z0-9_-]+)"),
    re.compile(r"/(?:[A-Za-z0-9_.]+/)?tv/([A-Za-z0-9_-]+)"),
]

_MIRROR_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def extract_shortcode(url: str) -> str | None:
    for rx in SHORTCODE_RE:
        m = rx.search(url)
        if m:
            return m.group(1)
    return None


def _fetch(url: str, referer: str | None = None) -> bytes:
    headers = {"User-Agent": _MIRROR_UA}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _mirror_image_urls(shortcode: str) -> list[str]:
    page = _fetch(f"https://imginn.com/p/{shortcode}/").decode("utf-8", "replace")
    slides = re.findall(
        r'<div class="swiper-slide[^>]*>.*?(?:data-src|src)="(https://[^"]+)"', page, re.DOTALL)
    urls = slides or re.findall(
        r'(?:data-src|src)="(https://[^"]+(?:imginn|scontent|cdninstagram)[^"]+)"', page)
    urls = [html_mod.unescape(u) for u in urls
            if "rsrc.php" not in u and "lazy.jpg" not in u and (".jpg" in u or ".webp" in u)]
    # t51.82787-15 = media del post; -19 y t51.2885-19 = avatares (tambien en collab)
    post_media = [u for u in urls if "t51.82787-15" in u]
    return post_media or [u for u in urls
                           if "t51.2885-19" not in u and "t51.82787-19" not in u]


def _parth_image_urls(data: dict) -> tuple[list[str], bool]:
    """Extrae (urls_de_imagen, es_video) del metadata de parth-dl.

    Video/reel -> [thumbnail]; post/carrusel -> todas las imagenes (el
    contrato historico de este modulo entrega el carrusel completo; la
    regla "solo primera" es del flujo flyer, no de aca).
    """
    urls: list[str] = []
    for item in data.get("images") or []:
        if isinstance(item, str) and item:
            urls.append(item)
        elif isinstance(item, dict):
            u = item.get("url") or item.get("src")
            if u:
                urls.append(u)
    is_video = data.get("type") == "video"
    if not urls and data.get("thumbnail"):
        urls = [data["thumbnail"]]
    return urls, is_video


def _parth_download(url: str, shortcode: str, output_dir: Path) -> dict | None:
    """Via primaria: parth-dl (pip install parth-dl). None => caer al mirror."""
    try:
        from parth_dl import get_info  # lazy: el repo funciona sin parth-dl
    except ImportError:
        return None
    try:
        data = get_info(url)
        urls, is_video = _parth_image_urls(data)
        if not urls:
            return None
        copied = []
        for i, img_url in enumerate(urls, 1):
            payload = _fetch(img_url)
            dst = output_dir / ("input_ig.jpg" if i == 1 else f"input_ig_{i}.jpg")
            dst.write_bytes(payload)
            copied.append(str(dst))
    except Exception:
        return None
    return {
        "status": "downloaded",
        "shortcode": shortcode,
        "url": url,
        "media_type": "video" if is_video
        else ("carousel" if len(copied) > 1 else "image"),
        "files": copied,
        "file_count": len(copied),
        "caption": data.get("caption") or data.get("description") or "",
        "owner": data.get("uploader") or "",
        "date": "",
        "is_video": is_video,
    }


def download_post(url: str, output_dir: Path, retries: int = 1) -> dict:
    """Descarga IG: parth-dl primaria, mirror imginn fallback.

    imginn quedo 403 Cloudflare para posts (2026-07-22); parth-dl cubre
    posts, carruseles y video/reel (thumbnail como imagen). instaloader
    murio (IG exige login incluso anonimo).
    """
    shortcode = extract_shortcode(url)
    if not shortcode:
        return {"status": "error", "reason": "shortcode_no_detectado", "url": url}

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for f in output_dir.glob("input_ig*"):
        f.unlink(missing_ok=True)
    (output_dir / "ig_caption.txt").unlink(missing_ok=True)

    resultado = _parth_download(url, shortcode, output_dir)
    if resultado is not None:
        return resultado

    last_err = ""
    for attempt in range(retries + 1):
        try:
            image_urls = _mirror_image_urls(shortcode)
            if not image_urls:
                last_err = "sin_archivos"
                raise RuntimeError(last_err)

            copied = []
            for i, img_url in enumerate(image_urls, 1):
                data = _fetch(img_url, referer="https://imginn.com/")
                dst = output_dir / ("input_ig.jpg" if i == 1 else f"input_ig_{i}.jpg")
                dst.write_bytes(data)
                copied.append(str(dst))

            return {
                "status": "downloaded",
                "shortcode": shortcode,
                "url": url,
                "media_type": "carousel" if len(copied) > 1 else "image",
                "files": copied,
                "file_count": len(copied),
                "caption": "",
                "owner": "",
                "date": "",
                "is_video": False,
            }

        except Exception as e:
            err = str(e)
            if "404" in err or "not found" in err.lower():
                err = "post_no_encontrado"
            elif "429" in err or "Too Many Requests" in err:
                err = "rate_limit"
            last_err = err
            if attempt < retries:
                time.sleep(2 + attempt * 3)
                continue
            return {"status": "manual_required", "reason": err, "url": url}

    return {"status": "manual_required", "reason": last_err, "url": url}
