"""Offline tests for cultura/mak_plataforma/latido.py -- the organism's
heartbeat: one descriptive research per fire, capped so it never floods the
free APIs.

Rescued 2026-07-30 (138 lines, cron every 4h, existed on the box only, never
in git). The caps ARE the file: MAX_DIA per day, MIN_GAP between beats, skip
under load. These tests pin the seed rotation, the state ratchet and each
skip in turn. The research hub is never reached: urlopen is faked.
"""
import importlib.util
import io
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LATIDO_PY = RAIZ / "cultura" / "mak_plataforma" / "latido.py"


def _cargar():
    spec = importlib.util.spec_from_file_location("latido_bajo_prueba",
                                                  LATIDO_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


latido = _cargar()


class RespuestaFalsa(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _en_tmp(monkeypatch, tmp_path):
    peticiones = []
    monkeypatch.setattr(latido, "SEMILLAS", str(tmp_path / "semillas.txt"))
    monkeypatch.setattr(latido, "IDX", str(tmp_path / ".idx"))
    monkeypatch.setattr(latido, "STATE", str(tmp_path / ".state.json"))
    monkeypatch.setattr(latido, "LOG", str(tmp_path / "latido.log"))
    monkeypatch.setattr(latido, "load1", lambda: 0.0)

    def urlopen(req, timeout=None):
        peticiones.append(req)
        return RespuestaFalsa(b'{"ok": true}')

    monkeypatch.setattr(latido.urllib.request, "urlopen", urlopen)
    return peticiones


# ----------------------------------------------------------------- semillas

def test_semillas_ausentes_siembra_el_default_editable(monkeypatch, tmp_path):
    _en_tmp(monkeypatch, tmp_path)
    assert latido.semillas() == latido.SEED_DEFAULT
    sembrado = (tmp_path / "semillas.txt").read_text(encoding="utf-8")
    assert latido.SEED_DEFAULT[0] in sembrado, "the file is left for editing"
    assert sembrado.startswith("#"), "with the how-to-edit comment on top"


def test_semillas_del_usuario_ignoran_comentarios_y_vacios(monkeypatch,
                                                           tmp_path):
    _en_tmp(monkeypatch, tmp_path)
    (tmp_path / "semillas.txt").write_text(
        "# comentario\n\n  idea uno  \nidea dos\n", encoding="utf-8")
    assert latido.semillas() == ["idea uno", "idea dos"]


def test_semillas_archivo_vacio_cae_al_default(monkeypatch, tmp_path):
    _en_tmp(monkeypatch, tmp_path)
    (tmp_path / "semillas.txt").write_text("# solo comentarios\n")
    assert latido.semillas() == latido.SEED_DEFAULT


def test_prox_idx_rota_circular_y_sobrevive_basura(monkeypatch, tmp_path):
    _en_tmp(monkeypatch, tmp_path)
    assert [latido.prox_idx(3) for _ in range(4)] == [0, 1, 2, 0]
    (tmp_path / ".idx").write_text("no-un-numero")
    assert latido.prox_idx(3) == 0, "corrupt index restarts, never crashes"


# --------------------------------------------------------------------- main

def test_latido_lanza_un_research_y_avanza_el_estado(monkeypatch, tmp_path):
    peticiones = _en_tmp(monkeypatch, tmp_path)
    latido.main()
    assert len(peticiones) == 1
    req = peticiones[0]
    assert req.get_method() == "POST"
    assert req.full_url == latido.RESEARCH
    cuerpo = req.data.decode()
    assert "modo=research" in cuerpo and "densidad=corto" in cuerpo
    assert "latido" in cuerpo

    st = json.loads((tmp_path / ".state.json").read_text())
    assert st["count"] == 1 and st["last"] > 0


def test_tope_diario_frena_el_sexto_latido(monkeypatch, tmp_path):
    peticiones = _en_tmp(monkeypatch, tmp_path)
    (tmp_path / ".state.json").write_text(json.dumps(
        {"date": time.strftime("%Y-%m-%d"), "count": latido.MAX_DIA,
         "last": 0}))
    latido.main()
    assert peticiones == [], "MAX_DIA reached: no request leaves"
    assert "tope diario" in (tmp_path / "latido.log").read_text()


def test_gap_minimo_de_2h_entre_latidos(monkeypatch, tmp_path):
    peticiones = _en_tmp(monkeypatch, tmp_path)
    (tmp_path / ".state.json").write_text(json.dumps(
        {"date": time.strftime("%Y-%m-%d"), "count": 1,
         "last": time.time() - 60}))
    latido.main()
    assert peticiones == []
    assert "gap" in (tmp_path / "latido.log").read_text()


def test_carga_alta_salta_el_latido(monkeypatch, tmp_path):
    peticiones = _en_tmp(monkeypatch, tmp_path)
    monkeypatch.setattr(latido, "load1", lambda: latido.LOAD_MAX + 1)
    latido.main()
    assert peticiones == [], "busy body: the beat yields"


def test_cambio_de_dia_reinicia_el_conteo(monkeypatch, tmp_path):
    peticiones = _en_tmp(monkeypatch, tmp_path)
    (tmp_path / ".state.json").write_text(json.dumps(
        {"date": "2001-01-01", "count": latido.MAX_DIA, "last": 0}))
    latido.main()
    assert len(peticiones) == 1, "yesterday's cap does not gag today"
    assert json.loads((tmp_path / ".state.json").read_text())["count"] == 1


def test_research_caido_no_consume_el_cupo(monkeypatch, tmp_path):
    """A failed POST must not count as a beat: the quota measures work done,
    not attempts."""
    _en_tmp(monkeypatch, tmp_path)
    monkeypatch.setattr(latido.urllib.request, "urlopen",
                        lambda req, timeout=None: (_ for _ in ()).throw(
                            OSError("connection refused")))
    latido.main()
    assert not (tmp_path / ".state.json").exists()
    assert "FALLO" in (tmp_path / "latido.log").read_text()
