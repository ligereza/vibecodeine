"""Tests offline para flujo.ig.download: parsing de shortcode y flujo de
download_post con el mirror (imginn.com) mockeado. Nunca toca la red.
"""

from pathlib import Path

import flujo.paths  # noqa: F401
from flujo.ig import download as ig_download
from flujo.ig.download import download_post, extract_shortcode


# ---------------- extract_shortcode ----------------

def test_extract_shortcode_post_directo():
    assert extract_shortcode("https://www.instagram.com/p/DXelZPPCOuM/") == "DXelZPPCOuM"


def test_extract_shortcode_con_usuario():
    assert extract_shortcode("https://www.instagram.com/sundeckfiestas/p/ABC123/") == "ABC123"


def test_extract_shortcode_reel():
    assert extract_shortcode("https://www.instagram.com/reel/XYZ789/") == "XYZ789"


def test_extract_shortcode_reels_plural():
    assert extract_shortcode("https://www.instagram.com/reels/XYZ789/") == "XYZ789"


def test_extract_shortcode_tv():
    assert extract_shortcode("https://www.instagram.com/tv/IGTVCODE/") == "IGTVCODE"


def test_extract_shortcode_no_match():
    assert extract_shortcode("https://www.instagram.com/sundeckfiestas/") is None


def test_extract_shortcode_url_vacia():
    assert extract_shortcode("") is None


# ---------------- download_post (mirror mockeado) ----------------

def test_download_post_shortcode_no_detectado():
    out = download_post("https://www.instagram.com/sundeckfiestas/", Path("no-importa"))
    assert out["status"] == "error"
    assert out["reason"] == "shortcode_no_detectado"


def test_download_post_exitoso_imagen(monkeypatch, tmp_path):
    monkeypatch.setattr(ig_download, "_mirror_image_urls",
                         lambda shortcode: ["https://imginn.com/img/abc.jpg"])
    monkeypatch.setattr(ig_download, "_fetch", lambda url, referer=None: b"fake-jpg-bytes")

    out_dir = tmp_path / "out"
    out = download_post("https://www.instagram.com/p/ABC123/", out_dir)

    assert out["status"] == "downloaded"
    assert out["shortcode"] == "ABC123"
    assert out["media_type"] == "image"
    assert out["file_count"] == 1
    assert (out_dir / "input_ig.jpg").read_bytes() == b"fake-jpg-bytes"


def test_download_post_exitoso_carousel(monkeypatch, tmp_path):
    monkeypatch.setattr(
        ig_download, "_mirror_image_urls",
        lambda shortcode: ["https://imginn.com/a.jpg", "https://imginn.com/b.jpg"],
    )
    monkeypatch.setattr(ig_download, "_fetch", lambda url, referer=None: b"x")

    out_dir = tmp_path / "out"
    out = download_post("https://www.instagram.com/p/CAROUSEL1/", out_dir)

    assert out["status"] == "downloaded"
    assert out["media_type"] == "carousel"
    assert out["file_count"] == 2
    assert (out_dir / "input_ig.jpg").exists()
    assert (out_dir / "input_ig_2.jpg").exists()


def test_download_post_limpia_archivos_previos(monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "input_ig.jpg").write_bytes(b"viejo")
    (out_dir / "input_ig_2.jpg").write_bytes(b"viejo2")
    (out_dir / "ig_caption.txt").write_text("caption vieja", encoding="utf-8")

    monkeypatch.setattr(ig_download, "_mirror_image_urls",
                         lambda shortcode: ["https://imginn.com/new.jpg"])
    monkeypatch.setattr(ig_download, "_fetch", lambda url, referer=None: b"nuevo-bytes")

    out = download_post("https://www.instagram.com/p/NUEVO1/", out_dir)

    assert out["status"] == "downloaded"
    assert not (out_dir / "input_ig_2.jpg").exists()
    assert (out_dir / "input_ig.jpg").read_bytes() == b"nuevo-bytes"


def test_download_post_sin_archivos_es_manual_required(monkeypatch, tmp_path):
    monkeypatch.setattr(ig_download, "_mirror_image_urls", lambda shortcode: [])
    out = download_post("https://www.instagram.com/p/SINARCHIVOS/", tmp_path / "out", retries=0)
    assert out["status"] == "manual_required"
    assert out["reason"] == "sin_archivos"


def test_download_post_rate_limit(monkeypatch, tmp_path):
    def boom(shortcode):
        raise RuntimeError("429 Too Many Requests")

    monkeypatch.setattr(ig_download, "_mirror_image_urls", boom)
    out = download_post("https://www.instagram.com/p/RATE1/", tmp_path / "out", retries=0)
    assert out["status"] == "manual_required"
    assert out["reason"] == "rate_limit"


def test_download_post_reintenta_y_luego_funciona(monkeypatch, tmp_path):
    calls = {"n": 0}

    def flaky(shortcode):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("post not found")
        return ["https://imginn.com/ok.jpg"]

    monkeypatch.setattr(ig_download, "_mirror_image_urls", flaky)
    monkeypatch.setattr(ig_download, "_fetch", lambda url, referer=None: b"ok")
    monkeypatch.setattr("time.sleep", lambda *a, **k: None)

    out = download_post("https://www.instagram.com/p/RETRY1/", tmp_path / "out", retries=1)
    assert out["status"] == "downloaded"
    assert calls["n"] == 2
