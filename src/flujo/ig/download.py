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


def download_post(url: str, output_dir: Path, retries: int = 1) -> dict:
    """Descarga via mirror publico (imginn.com).

    instaloader murio: IG exige login incluso anonimo desde 2026-07-1x. No hay
    caption/owner/fecha (el mirror no los expone de forma confiable); solo
    imagenes -- videos no soportados via este camino.
    """
    shortcode = extract_shortcode(url)
    if not shortcode:
        return {"status": "error", "reason": "shortcode_no_detectado", "url": url}

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for f in output_dir.glob("input_ig*"):
        f.unlink(missing_ok=True)
    (output_dir / "ig_caption.txt").unlink(missing_ok=True)

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
