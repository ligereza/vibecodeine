# -*- coding: utf-8 -*-
"""Via secundaria curl_cffi (impersonate=chrome) en flujo.ig.download.

parth-dl pega login-wall de IG por fingerprint TLS en Linux; curl_cffi
imita el fingerprint TLS de Chrome y pasa (verificado 2026-07-23, box MAK
Debian). curl_cffi es dep opcional: se mockea via sys.modules (no esta
instalada en este entorno de tests), snapshot/restore en finally para no
contaminar otros tests.
"""
import sys
import types

import pytest

from flujo.ig.download import _cffi_download


class _FakeResponse:
    def __init__(self, text="", content=b""):
        self.text = text
        self.content = content


class _FakeSession:
    """Mapea url -> _FakeResponse (o Exception a levantar). Registra calls."""

    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        resp = self._responses.get(url)
        if resp is None:
            raise RuntimeError(f"url inesperada en el fake: {url}")
        if isinstance(resp, Exception):
            raise resp
        return resp


@pytest.fixture
def fake_curl_cffi():
    """Instala un curl_cffi falso en sys.modules; restaura (pop) en finally."""
    installed = {}

    def _install(responses):
        fake_requests_mod = types.ModuleType("curl_cffi.requests")
        fake_requests_mod.Session = lambda *a, **k: _FakeSession(responses)
        fake_pkg = types.ModuleType("curl_cffi")
        fake_pkg.requests = fake_requests_mod
        sys.modules["curl_cffi"] = fake_pkg
        sys.modules["curl_cffi.requests"] = fake_requests_mod
        installed["session_responses"] = responses
        return fake_requests_mod

    try:
        yield _install
    finally:
        sys.modules.pop("curl_cffi", None)
        sys.modules.pop("curl_cffi.requests", None)


PAGE_URL = "https://www.instagram.com/p/DZdW4_vmY4l/"
IMG_URL = "https://scontent.cdninstagram.com/v/t51.29350-15/photo.jpg"


def _page_html(extra_meta="", caption='caption de prueba con &quot;comillas&quot;'):
    return f"""<html><head>
<meta property="og:image" content="{IMG_URL}" />
<meta property="og:description" content="{caption}" />
{extra_meta}
</head><body></body></html>"""


def test_og_image_presente_descarga_y_contrato_correcto(fake_curl_cffi, tmp_path):
    fake_curl_cffi({
        PAGE_URL: _FakeResponse(text=_page_html()),
        IMG_URL: _FakeResponse(content=b"jpg-bytes-reales"),
    })

    out = _cffi_download(PAGE_URL, "DZdW4_vmY4l", tmp_path)

    assert out is not None
    assert out["status"] == "downloaded"
    assert out["shortcode"] == "DZdW4_vmY4l"
    assert out["url"] == PAGE_URL
    assert out["media_type"] == "image"
    assert out["is_video"] is False
    assert out["file_count"] == 1
    assert out["files"] == [str(tmp_path / "input_ig.jpg")]
    assert (tmp_path / "input_ig.jpg").read_bytes() == b"jpg-bytes-reales"
    assert out["caption"] == 'caption de prueba con "comillas"'


def test_sin_og_image_retorna_none(fake_curl_cffi, tmp_path):
    html = '<html><head><meta property="og:title" content="sin imagen" /></head></html>'
    fake_curl_cffi({PAGE_URL: _FakeResponse(text=html)})

    out = _cffi_download(PAGE_URL, "DZdW4_vmY4l", tmp_path)

    assert out is None
    assert not (tmp_path / "input_ig.jpg").exists()


def test_sin_curl_cffi_instalado_retorna_none_sin_explotar(tmp_path):
    # Sin fixture: curl_cffi NO esta en sys.modules (no instalado en este
    # entorno) -> ImportError real dentro de _cffi_download -> None.
    sys.modules.pop("curl_cffi", None)
    sys.modules.pop("curl_cffi.requests", None)

    out = _cffi_download(PAGE_URL, "DZdW4_vmY4l", tmp_path)

    assert out is None


def test_og_video_presente_baja_thumbnail_igual(fake_curl_cffi, tmp_path):
    video_url = "https://scontent.cdninstagram.com/v/video.mp4"
    html = _page_html(extra_meta=f'<meta property="og:video" content="{video_url}" />')
    fake_curl_cffi({
        PAGE_URL: _FakeResponse(text=html),
        IMG_URL: _FakeResponse(content=b"thumbnail-bytes"),
    })

    out = _cffi_download(PAGE_URL, "DZdW4_vmY4l", tmp_path)

    assert out is not None
    assert out["is_video"] is True
    assert out["media_type"] == "video"
    assert out["files"] == [str(tmp_path / "input_ig.jpg")]
    assert (tmp_path / "input_ig.jpg").read_bytes() == b"thumbnail-bytes"


def test_caption_escrita_en_archivo(fake_curl_cffi, tmp_path):
    fake_curl_cffi({
        PAGE_URL: _FakeResponse(text=_page_html(caption="hola &amp; chau &#39;test&#39;")),
        IMG_URL: _FakeResponse(content=b"x"),
    })

    out = _cffi_download(PAGE_URL, "DZdW4_vmY4l", tmp_path)

    assert out is not None
    caption_file = tmp_path / "ig_caption.txt"
    assert caption_file.exists()
    assert caption_file.read_text(encoding="utf-8") == "hola & chau 'test'"
    assert out["caption"] == "hola & chau 'test'"


def test_excepcion_de_red_retorna_none(fake_curl_cffi, tmp_path):
    fake_curl_cffi({PAGE_URL: RuntimeError("connection reset")})

    out = _cffi_download(PAGE_URL, "DZdW4_vmY4l", tmp_path)

    assert out is None
    assert not (tmp_path / "input_ig.jpg").exists()
