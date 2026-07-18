"""Tests offline para flujo.ig.download: parsing de shortcode y flujo de
download_post con instaloader mockeado por completo. Nunca toca la red.
"""

import sys
import types
from pathlib import Path

import flujo.paths  # noqa: F401
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


# ---------------- helpers para mockear instaloader ----------------

def _install_fake_instaloader(monkeypatch, *, download_behavior=None, caption="Fiesta hoy!",
                               owner="cuenta_test", is_video=False, date_utc=None):
    """Instala un modulo 'instaloader' falso en sys.modules.

    download_behavior(target: Path) -> None  escribe los archivos que
    'descargaria' instaloader.Instaloader.download_post en el target dir.
    Si es None, escribe una sola imagen jpg.
    """
    fake_mod = types.ModuleType("instaloader")

    class FakeContext:
        pass

    class FakePost:
        def __init__(self):
            self.caption = caption
            self.owner_username = owner
            self.is_video = is_video
            self.date_utc = date_utc

        @staticmethod
        def from_shortcode(context, shortcode):
            return FakePost()

    class FakeInstaloader:
        def __init__(self, **kwargs):
            self.context = FakeContext()

        def download_post(self, post, target):
            target_path = Path(target)
            if download_behavior:
                download_behavior(target_path)
            else:
                (target_path / "abc123.jpg").write_bytes(b"fake-jpg-bytes")

    fake_mod.Instaloader = FakeInstaloader
    fake_mod.Post = FakePost
    monkeypatch.setitem(sys.modules, "instaloader", fake_mod)
    return fake_mod


# ---------------- download_post ----------------

def test_download_post_instaloader_no_instalado(monkeypatch):
    # forzar ImportError real para "import instaloader"
    monkeypatch.setitem(sys.modules, "instaloader", None)
    out = download_post("https://www.instagram.com/p/ABC123/", Path("no-importa"))
    assert out["status"] == "error"
    assert out["reason"] == "instaloader_no_instalado"


def test_download_post_shortcode_no_detectado(monkeypatch, tmp_path):
    _install_fake_instaloader(monkeypatch)
    out = download_post("https://www.instagram.com/sundeckfiestas/", tmp_path)
    assert out["status"] == "error"
    assert out["reason"] == "shortcode_no_detectado"


def test_download_post_exitoso_imagen(monkeypatch, tmp_path):
    _install_fake_instaloader(monkeypatch, caption="Hola mundo", owner="fiestas_rd")
    out_dir = tmp_path / "out"
    out = download_post("https://www.instagram.com/p/ABC123/", out_dir)

    assert out["status"] == "downloaded"
    assert out["shortcode"] == "ABC123"
    assert out["media_type"] == "image"
    assert out["file_count"] == 1
    assert out["owner"] == "fiestas_rd"
    assert out["caption"] == "Hola mundo"
    assert (out_dir / "input_ig.jpg").exists()
    assert (out_dir / "ig_caption.txt").read_text(encoding="utf-8") == "Hola mundo"


def test_download_post_exitoso_carousel(monkeypatch, tmp_path):
    def behavior(target: Path):
        (target / "a.jpg").write_bytes(b"1")
        (target / "b.jpg").write_bytes(b"2")

    _install_fake_instaloader(monkeypatch, download_behavior=behavior)
    out_dir = tmp_path / "out"
    out = download_post("https://www.instagram.com/p/CAROUSEL1/", out_dir)

    assert out["status"] == "downloaded"
    assert out["media_type"] == "carousel"
    assert out["file_count"] == 2
    assert (out_dir / "input_ig.jpg").exists()
    assert (out_dir / "input_ig_2.jpg").exists()


def test_download_post_exitoso_video(monkeypatch, tmp_path):
    def behavior(target: Path):
        (target / "clip.mp4").write_bytes(b"video-bytes")

    _install_fake_instaloader(monkeypatch, download_behavior=behavior, is_video=True)
    out_dir = tmp_path / "out"
    out = download_post("https://www.instagram.com/reel/VID123/", out_dir)

    assert out["status"] == "downloaded"
    assert out["media_type"] == "video"
    assert out["is_video"] is True
    assert (out_dir / "input_ig_video.mp4").exists()


def test_download_post_limpia_archivos_previos(monkeypatch, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "input_ig.jpg").write_bytes(b"viejo")
    (out_dir / "input_ig_2.jpg").write_bytes(b"viejo2")
    (out_dir / "ig_caption.txt").write_text("caption vieja", encoding="utf-8")

    _install_fake_instaloader(monkeypatch, caption="")
    out = download_post("https://www.instagram.com/p/NUEVO1/", out_dir)

    assert out["status"] == "downloaded"
    # el archivo viejo _2 no debe sobrevivir (se limpio antes de descargar)
    assert not (out_dir / "input_ig_2.jpg").exists()
    assert (out_dir / "input_ig.jpg").read_bytes() == b"fake-jpg-bytes"


def test_download_post_sin_archivos_es_manual_required(monkeypatch, tmp_path):
    _install_fake_instaloader(monkeypatch, download_behavior=lambda target: None)
    out = download_post("https://www.instagram.com/p/SINARCHIVOS/", tmp_path / "out", retries=0)
    assert out["status"] == "manual_required"
    assert out["reason"] == "sin_archivos"


def test_download_post_login_requerido(monkeypatch, tmp_path):
    fake_mod = _install_fake_instaloader(monkeypatch)

    def boom_from_shortcode(context, shortcode):
        raise RuntimeError("Login required to view this post")

    fake_mod.Post.from_shortcode = staticmethod(boom_from_shortcode)
    out = download_post("https://www.instagram.com/p/PRIVADO1/", tmp_path / "out", retries=0)
    assert out["status"] == "manual_required"
    assert out["reason"] == "login_requerido_o_privado"


def test_download_post_rate_limit(monkeypatch, tmp_path):
    fake_mod = _install_fake_instaloader(monkeypatch)

    def boom_from_shortcode(context, shortcode):
        raise RuntimeError("429 Too Many Requests")

    fake_mod.Post.from_shortcode = staticmethod(boom_from_shortcode)
    out = download_post("https://www.instagram.com/p/RATE1/", tmp_path / "out", retries=0)
    assert out["status"] == "manual_required"
    assert out["reason"] == "rate_limit"


def test_download_post_reintenta_y_luego_funciona(monkeypatch, tmp_path):
    fake_mod = _install_fake_instaloader(monkeypatch)
    calls = {"n": 0}
    real_from_shortcode = fake_mod.Post.from_shortcode

    def flaky(context, shortcode):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("post not found")
        return real_from_shortcode(context, shortcode)

    fake_mod.Post.from_shortcode = staticmethod(flaky)
    monkeypatch.setattr("time.sleep", lambda *a, **k: None)  # no esperar de verdad

    out = download_post("https://www.instagram.com/p/RETRY1/", tmp_path / "out", retries=1)
    assert out["status"] == "downloaded"
    assert calls["n"] == 2
