"""Tests de _resp_ok en cultura/mak_plataforma/trabajo.py.

trabajo.py despacha por HTTP a research/codex; el /run puede devolver
{"ok": false, "error": "..."} para un rechazo a nivel de aplicacion (ej.
sin token, cuota agotada). Antes del fix, cualquier 200 se contaba como
exito. _resp_ok separa exito real de rechazo, tolerando bodies legacy
no-JSON o sin campo "ok" (se tratan como exito, no rompen compat).
"""
import sys
import json
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


def test_idle_review_uses_revision_format(monkeypatch):
    monkeypatch.setattr(trabajo, "_has_pending_material", lambda: False)
    monkeypatch.setattr(trabajo, "_has_pending_research_backlog", lambda: False)
    monkeypatch.setattr(trabajo, "_has_pending_codex_backlog", lambda: False)
    depto, payload = trabajo._tarea("repasar", {})
    assert depto == "research"
    assert payload["formato"] == "revision"
    assert payload["densidad"] == "corto"
    assert "revision" in payload["tema"]


@pytest.mark.parametrize(("verbo", "expected"), [
    ("repasar", {"modo": "research", "formato": "revision"}),
    ("discutir", {"modo": "panel"}),
    ("refutar", {"modo": "refutar"}),
    ("exponer", {"modo": "research", "formato": "exposicion"}),
])
def test_idle_executive_nodes_have_distinct_contracts(monkeypatch, verbo, expected):
    monkeypatch.setattr(trabajo, "_has_pending_material", lambda: False)
    monkeypatch.setattr(trabajo, "_has_pending_research_backlog", lambda: False)
    monkeypatch.setattr(trabajo, "_has_pending_codex_backlog", lambda: False)
    depto, payload = trabajo._tarea(verbo, {})
    assert depto == "research"
    for key, value in expected.items():
        assert payload[key] == value
    assert payload["densidad"] == "corto"


@pytest.mark.parametrize("pending", [
    "_has_pending_material",
    "_has_pending_research_backlog",
    "_has_pending_codex_backlog",
])
def test_idle_review_waits_for_real_backlog(monkeypatch, pending):
    monkeypatch.setattr(trabajo, "_has_pending_material", lambda: False)
    monkeypatch.setattr(trabajo, "_has_pending_research_backlog", lambda: False)
    monkeypatch.setattr(trabajo, "_has_pending_codex_backlog", lambda: False)
    monkeypatch.setattr(trabajo, pending, lambda: True)
    for verbo in ("repasar", "discutir", "refutar", "exponer"):
        assert trabajo._tarea(verbo, {}) is None


def test_seeds_are_not_infinite_default_when_backlog_is_empty(monkeypatch):
    if trabajo.backlog is None:
        pytest.skip("backlog not importable")
    monkeypatch.delenv("MAK_SEED_FALLBACK", raising=False)
    monkeypatch.setattr(trabajo.backlog, "pop_pendiente", lambda _path: None)
    assert trabajo._tarea("multiplicar", {}) is None
    assert trabajo._tarea("definir", {}) is None


def test_seed_fallback_is_explicit_opt_in(monkeypatch):
    if trabajo.backlog is None:
        pytest.skip("backlog not importable")
    monkeypatch.setenv("MAK_SEED_FALLBACK", "1")
    monkeypatch.setattr(trabajo.backlog, "pop_pendiente", lambda _path: None)
    depto, payload = trabajo._tarea("multiplicar", {})
    assert depto == "research"
    assert payload["formato"] == "ensayo"
    assert payload["tema"]


def test_idle_decision_writes_auditable_jsonl(monkeypatch, tmp_path):
    audit = tmp_path / "idle_decisions.jsonl"
    monkeypatch.setattr(trabajo, "IDLE_AUDIT", str(audit))
    monkeypatch.setattr(trabajo, "_pending_snapshot", lambda: {
        "material": False,
        "research_backlog": False,
        "codex_backlog": False,
    })
    trabajo._audit_idle_decision(
        "2026-08-05 12:30:00", True, "exponer", "research",
        {"modo": "research", "formato": "exposicion", "densidad": "corto",
         "tema": "exponer cabos sueltos"},
        "accepted", '{"ok": true}')
    rows = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
    assert rows == [{
        "depto": "research",
        "densidad": "corto",
        "formato": "exposicion",
        "modo": "research",
        "online": True,
        "pending": {"codex_backlog": False, "material": False,
                    "research_backlog": False},
        "response_preview": '{"ok": true}',
        "status": "accepted",
        "tema": "exponer cabos sueltos",
        "ts": "2026-08-05 12:30:00",
        "verbo": "exponer",
    }]


def test_idle_audit_ignores_productive_verbs(monkeypatch, tmp_path):
    audit = tmp_path / "idle_decisions.jsonl"
    monkeypatch.setattr(trabajo, "IDLE_AUDIT", str(audit))
    trabajo._audit_idle_decision(
        "2026-08-05 12:30:00", True, "multiplicar", "research",
        {"modo": "research", "formato": "ensayo", "densidad": "medio",
         "tema": "tilde"},
        "accepted", '{"ok": true}')
    assert not audit.exists()


def test_hallazgo_marker_en_correlacionar_archivos():
    src = (REPO_ROOT / "cultura" / "mak_research" / "correlacionar_archivos.py").read_text(
        encoding="utf-8")
    assert "HALLAZGO: " in src


def test_hallazgo_marker_en_memoria():
    src = (REPO_ROOT / "cultura" / "mak_research" / "memoria.py").read_text(encoding="utf-8")
    assert "HALLAZGO: " in src
