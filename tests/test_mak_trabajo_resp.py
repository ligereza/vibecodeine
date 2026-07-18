"""Tests de _resp_ok en cultura/mak_plataforma/trabajo.py.

trabajo.py despacha por HTTP a research/codex; el /run puede devolver
{"ok": false, "error": "..."} para un rechazo a nivel de aplicacion (ej.
sin token, cuota agotada). Antes del fix, cualquier 200 se contaba como
exito. _resp_ok separa exito real de rechazo, tolerando bodies legacy
no-JSON o sin campo "ok" (se tratan como exito, no rompen compat).
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MAK_PLATAFORMA = REPO_ROOT / "cultura" / "mak_plataforma"

_IMPORT_ERROR = None
try:
    sys.path.insert(0, str(MAK_PLATAFORMA))
    import trabajo  # noqa: E402
except Exception as e:  # noqa: BLE001 - se reporta como skip, no crash de colecta
    _IMPORT_ERROR = e
    trabajo = None


pytestmark = pytest.mark.skipif(
    trabajo is None,
    reason="no se pudo importar trabajo.py en esta plataforma: %r" % (_IMPORT_ERROR,))


def test_resp_ok_true():
    ok, err = trabajo._resp_ok('{"ok": true}')
    assert ok is True
    assert err == ""


def test_resp_ok_false_con_error():
    ok, err = trabajo._resp_ok('{"ok": false, "error": "sin token"}')
    assert ok is False
    assert err == "sin token"


def test_resp_ok_no_json_legacy():
    ok, err = trabajo._resp_ok("no json")
    assert ok is True
    assert err == ""


def test_resp_ok_lista_no_dict():
    ok, err = trabajo._resp_ok("[]")
    assert ok is True
    assert err == ""


def test_resp_ok_sin_campo_ok():
    ok, err = trabajo._resp_ok('{"otra": 1}')
    assert ok is True
    assert err == ""


def test_resp_ok_error_truncado_200():
    error_largo = "x" * 500
    ok, err = trabajo._resp_ok(
        '{"ok": false, "error": "%s"}' % error_largo)
    assert ok is False
    assert len(err) == 200


def test_resp_ok_empty_string():
    ok, err = trabajo._resp_ok("")
    assert ok is True
    assert err == ""


def test_dispatch_rechazado_no_incrementa_count(monkeypatch):
    """main(): si _post responde ok=false, no debe subir st['count'] ni
    st['last'], para que el proximo tick del cron reintente."""
    saved = {}
    monkeypatch.setattr(trabajo, "_post", lambda url, data: '{"ok": false, "error": "cuota"}')
    monkeypatch.setattr(trabajo, "_save", lambda s: saved.update(s))
    monkeypatch.setattr(trabajo, "log", lambda m: None)
    monkeypatch.setattr(trabajo, "load1", lambda: 0.0)
    monkeypatch.setattr(trabajo, "_state", lambda: {
        "date": trabajo.time.strftime("%Y-%m-%d"),
        "count": 0, "last": 0, "verbo_idx": 0,
    })
    monkeypatch.setattr(trabajo.roles, "LOAD_MAX", 999)
    monkeypatch.setattr(trabajo.roles, "GAP_MIN", 0)
    monkeypatch.setattr(trabajo.roles, "GAP_MIN_OFFLINE", 0)
    monkeypatch.setattr(trabajo.roles, "MAX_DIA", 999)
    monkeypatch.setattr(trabajo, "red_ok", lambda: True)
    if trabajo.backlog is not None:
        monkeypatch.setattr(trabajo.backlog, "cosechar", lambda *a, **k: 0)

    trabajo.main()

    assert saved.get("count", 0) == 0
    assert saved.get("last", 0) == 0


def test_hallazgo_marker_en_correlacionar_archivos():
    src = (REPO_ROOT / "cultura" / "mak_research" / "correlacionar_archivos.py").read_text(
        encoding="utf-8")
    assert "HALLAZGO: " in src


def test_hallazgo_marker_en_memoria():
    src = (REPO_ROOT / "cultura" / "mak_research" / "memoria.py").read_text(encoding="utf-8")
    assert "HALLAZGO: " in src
