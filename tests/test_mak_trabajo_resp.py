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


def test_harvested_factual_question_does_not_use_essay_shape(monkeypatch):
    """A factual event question can arrive through the generative backlog.

    Measured on MAK 2026-08-05: "Quien organizo el evento del 2023-10-28" ran
    under verb `multiplicar`, requested essay format, and produced PARTE I /
    ANEXO ICONOGRAFICO around a triangulation task. The output contract must
    follow the product, not the rotation verb."""
    if trabajo.backlog is None:
        pytest.skip("backlog not importable")
    monkeypatch.setattr(trabajo.backlog, "pop_pendiente",
                        lambda _path: {
                            "pregunta": "Quien organizo el evento del 2023-10-28",
                        })
    depto, payload = trabajo._tarea("multiplicar", {})
    assert depto == "research"
    assert payload["formato"] == "informe"
    assert payload["densidad"] == "corto"


@pytest.mark.parametrize("pregunta", [
    "Que productora se encargo del evento en Santiago de Chile el 31 de enero de 2023",
    "Quien es el responsable de supervisar la seguridad privada en eventos masivos en Chile",
    "Cómo se coordina la seguridad entre las autoridades y los organizadores en la práctica",
    "¿Cuál es la política de devolución y reembolso de Ticketmaster?",
    "¿Cómo puedo comprar entradas en Puntoticket?",
])
def test_harvested_operational_questions_do_not_get_iconographic_essays(
        pregunta, monkeypatch):
    """Real MAK corpus 2026-08-05: operational/event questions were harvested
    under `multiplicar` and came out as essays with concept annexes. They must
    stay reports, even when the rotation verb is cultural."""
    if trabajo.backlog is None:
        pytest.skip("backlog not importable")
    monkeypatch.setattr(trabajo.backlog, "pop_pendiente",
                        lambda _path: {"pregunta": pregunta})
    depto, payload = trabajo._tarea("multiplicar", {})
    assert depto == "research"
    assert payload["formato"] == "informe"
    assert payload["densidad"] == "corto"


def test_cultural_multiplicar_topic_still_uses_essay_shape(monkeypatch):
    if trabajo.backlog is None:
        pytest.skip("backlog not importable")
    monkeypatch.setattr(trabajo.backlog, "pop_pendiente",
                        lambda _path: {
                            "pregunta": "genealogia cultural de la tilde en el arte digital",
                        })
    depto, payload = trabajo._tarea("multiplicar", {})
    assert depto == "research"
    assert payload["formato"] == "ensayo"
    assert payload["densidad"] == "medio"


def test_hallazgo_marker_en_correlacionar_archivos():
    src = (REPO_ROOT / "cultura" / "mak_research" / "correlacionar_archivos.py").read_text(
        encoding="utf-8")
    assert "HALLAZGO: " in src


def test_hallazgo_marker_en_memoria():
    src = (REPO_ROOT / "cultura" / "mak_research" / "memoria.py").read_text(encoding="utf-8")
    assert "HALLAZGO: " in src
