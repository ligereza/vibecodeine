"""Descarga de posts de Instagram: via unica parth-dl.

imginn retirado 2026-07-25, causa: 403 Cloudflare permanente desde
2026-07-22, resurreccion: mirror publico funcional verificado.
"""

import re
import time
import urllib.request
from pathlib import Path

SHORTCODE_RE = [
    re.compile(r"/(?:[A-Za-z0-9_.]+/)?p/([A-Za-z0-9_-]+)"),
    re.compile(r"/(?:[A-Za-z0-9_.]+/)?reels?/([A-Za-z0-9_-]+)"),
    re.compile(r"/(?:[A-Za-z0-9_.]+/)?tv/([A-Za-z0-9_-]+)"),
]

_FETCH_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def extract_shortcode(url: str) -> str | None:
    for rx in SHORTCODE_RE:
        m = rx.search(url)
        if m:
            return m.group(1)
    return None


def canonicalizar_url(url: str) -> str:
    """Quita el username de la ruta: /usuario/p/SC/ -> /p/SC/.

    parth-dl devuelve 403 con la forma con username (issues #5 y #171,
    2026-07-22). Preserva tipo (p|reel|tv) y query params.
    """
    return re.sub(
        r"(instagram\.com)/[A-Za-z0-9_.]+/(p|reel|tv)/",
        r"\1/\2/",
        url,
    )


def _fetch(url: str, referer: str | None = None) -> bytes:
    headers = {"User-Agent": _FETCH_UA}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


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


def _parth_download(url: str, shortcode: str, output_dir: Path) -> dict:
    """Via unica: parth-dl (pip install parth-dl).

    Lanza ImportError si el paquete no esta instalado, o la excepcion que
    corresponda (red, sin archivos) si la descarga falla. download_post()
    clasifica y convierte esas excepciones en un resultado manual_required.
    """
    from parth_dl import get_info  # lazy: el repo funciona sin parth-dl instalado

    data = get_info(url)
    urls, is_video = _parth_image_urls(data)
    if not urls:
        raise RuntimeError("sin_archivos")
    copied = []
    for i, img_url in enumerate(urls, 1):
        payload = _fetch(img_url)
        dst = output_dir / ("input_ig.jpg" if i == 1 else f"input_ig_{i}.jpg")
        dst.write_bytes(payload)
        copied.append(str(dst))
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
    """Descarga IG via parth-dl (unica via).

    parth-dl cubre posts, carruseles y video/reel (thumbnail como imagen).
    Sin fallback: si parth-dl no esta instalado o falla, retorna
    manual_required con la razon. instaloader murio (IG exige login
    incluso anonimo).
    """
    url = canonicalizar_url(url)
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
            return _parth_download(url, shortcode, output_dir)
        except ImportError:
            return {"status": "manual_required", "reason": "parth_dl_no_instalado", "url": url}
        except Exception as e:
            err = str(e)
            if "404" in err or "not found" in err.lower():
                err = "post_no_encontrado"
            elif "429" in err or "Too Many Requests" in err:
                err = "rate_limit"
            elif not err:
                err = "error_desconocido"
            last_err = err
            if attempt < retries:
                time.sleep(2 + attempt * 3)
                continue
            return {"status": "manual_required", "reason": err, "url": url}

    return {"status": "manual_required", "reason": last_err, "url": url}
