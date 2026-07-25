"""Descarga de posts de Instagram: parth-dl primaria, curl_cffi secundaria.

imginn retirado 2026-07-25, causa: 403 Cloudflare permanente desde
2026-07-22, resurreccion: mirror publico funcional verificado.

curl_cffi NO se retira: es la via que hace funcionar la descarga en Linux
(box MAK), donde parth-dl pega login-wall por fingerprint TLS -- verificado
2026-07-23. Se restauro el 2026-07-25 tras haber sido podada por error junto
con imginn.
"""

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


def _meta_content(html: str, prop: str) -> str | None:
    """Extrae content="..." de un <meta property="prop" .../>, en cualquier
    orden de atributos (property antes o despues de content)."""
    prop_re = re.escape(prop)
    pattern = re.compile(
        r'<meta\s+[^>]*?property=["\']' + prop_re + r'["\'][^>]*?content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    m = pattern.search(html)
    if not m:
        pattern2 = re.compile(
            r'<meta\s+[^>]*?content=["\']([^"\']+)["\'][^>]*?property=["\']' + prop_re + r'["\']',
            re.IGNORECASE,
        )
        m = pattern2.search(html)
    if not m:
        return None
    return html_mod.unescape(m.group(1))


def _cffi_download(url: str, shortcode: str, output_dir: Path) -> dict | None:
    """Via secundaria: curl_cffi con impersonate="chrome".

    parth-dl (Linux) recibe login-wall de IG por fingerprint TLS; curl_cffi
    imita el fingerprint TLS de Chrome y obtiene la pagina real (verificado
    2026-07-23 en el box MAK Debian, https://www.instagram.com/p/DZdW4_vmY4l/).
    Lazy import: el repo funciona sin la dep. None => no hay via secundaria.
    """
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        return None
    try:
        session = cffi_requests.Session()
        page = session.get(url, impersonate="chrome", timeout=30)
        html = page.text

        image_url = _meta_content(html, "og:image")
        if not image_url:
            return None
        is_video = _meta_content(html, "og:video") is not None
        caption = (_meta_content(html, "og:description")
                   or _meta_content(html, "og:title") or "")

        img_resp = session.get(image_url, impersonate="chrome", timeout=30)
        dst = output_dir / "input_ig.jpg"
        dst.write_bytes(img_resp.content)
        if caption:
            (output_dir / "ig_caption.txt").write_text(caption, encoding="utf-8")
    except Exception:
        return None

    return {
        "status": "downloaded",
        "shortcode": shortcode,
        "url": url,
        "media_type": "video" if is_video else "image",
        "files": [str(dst)],
        "file_count": 1,
        "caption": caption,
        "owner": "",
        "date": "",
        "is_video": is_video,
    }


def _parth_download(url: str, shortcode: str, output_dir: Path) -> dict:
    """Via primaria: parth-dl (pip install parth-dl).

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
    """Descarga IG: parth-dl primaria, curl_cffi (impersonate) secundaria.

    parth-dl cubre posts, carruseles y video/reel (thumbnail como imagen),
    pero en Linux puede pegar login-wall por fingerprint TLS -- ahi entra
    curl_cffi (verificado 2026-07-23 en el box MAK). Si ninguna via sirve,
    retorna manual_required con la razon. imginn quedo 403 Cloudflare
    (retirado 2026-07-25); instaloader murio (IG exige login incluso anonimo).
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
            last_err = "parth_dl_no_instalado"
            break
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
            break

    resultado = _cffi_download(url, shortcode, output_dir)
    if resultado is not None:
        return resultado

    return {"status": "manual_required", "reason": last_err, "url": url}
