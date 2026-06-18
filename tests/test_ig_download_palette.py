"""Tests de descarga IG + extracción/aplicación de paleta en el editor.

La descarga real usa instaloader (red); aquí se mockea download_post para
testear el cableado y el post-procesamiento (paleta) sin tocar la red.
"""

from pathlib import Path

import pytest

from flujo.web import editor


def test_descargar_sin_links():
    res, msg, img = editor.descargar_instagram("texto sin instagram")
    assert res == {}
    assert "No hay links" in msg
    assert img == ""


def test_descargar_y_paleta(tmp_path, monkeypatch):
    pytest.importorskip("PIL")
    from PIL import Image
    import flujo.ig.download as dl

    monkeypatch.setattr(editor, "repo_root", lambda: tmp_path)

    def fake_download(url, out_dir, retries=1):
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / "input_ig.jpg"
        Image.new("RGB", (80, 80), (20, 80, 160)).save(dst)
        return {
            "status": "downloaded", "media_type": "image", "file_count": 1,
            "files": [str(dst)], "owner": "cuenta", "date": "2026-06-10T00:00:00",
            "caption": "hola", "is_video": False,
        }

    monkeypatch.setattr(dl, "download_post", fake_download)

    res, msg, img = editor.descargar_instagram(
        "https://www.instagram.com/cuenta/p/ABC123/"
    )
    assert res["status"] == "downloaded"
    assert "✓ Descargado" in msg
    assert "@cuenta" in msg
    assert Path(img).exists()
    assert res.get("palette", {}).get("colors"), "debió extraer paleta"


def test_descargar_maneja_error(tmp_path, monkeypatch):
    import flujo.ig.download as dl
    monkeypatch.setattr(editor, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(dl, "download_post", lambda url, out_dir, retries=1: {
        "status": "manual_required", "reason": "login_requerido_o_privado", "url": url,
    })
    res, msg, img = editor.descargar_instagram("instagram.com/cuenta/p/XYZ/")
    assert "privado" in msg.lower() or "login" in msg.lower()
    assert img == ""


def test_aplicar_paleta_sin_config():
    cfg, msg = editor.aplicar_paleta({}, {"palette": {"colors": [{"hex": "#111111"}]}})
    assert cfg == {}
    assert "Primero elige" in msg


def test_aplicar_paleta_sin_paleta():
    cfg = {"palette": {"ink": "#000"}}
    out, msg = editor.aplicar_paleta(cfg, {})
    assert "No hay paleta" in msg
    assert out == cfg


def test_aplicar_paleta_ok():
    cfg = {"palette": {"ink": "#000"}, "documents": []}
    desc = {"palette": {"colors": [{"hex": "#aa1122"}, {"hex": "#223344"}, {"hex": "#556677"}]}}
    out, msg = editor.aplicar_paleta(cfg, desc)
    assert out["palette"]["accent"] == "#aa1122"
    assert out["palette"]["ink"] == "#223344"
    assert "aplicada" in msg.lower()
    # no muta el original
    assert cfg["palette"] == {"ink": "#000"}
