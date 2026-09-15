from __future__ import annotations

import copy
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_hub():
    module_name = "hub_archive_portfolio_view_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(
        module_name, REPO_ROOT / "cultura" / "mak_plataforma" / "hub.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _archive_fixture() -> dict:
    return {
        "version": 1,
        "fuente": "bounded-test-evidence",
        "generado": "2026-08-27T12:00:00",
        "piezas": [
            {
                "id": "declared-work",
                "titulo": "Declared work",
                "clase": "obra",
                "fecha": "2026",
                "resumen": "Source-declared summary.",
                "etiquetas": ["visual"],
                "peso": 3,
                "medio": {"tipo": "imagen", "src": "assets/work.png"},
                "estado": "publicada",
            },
            {
                "id": "artist-name/famous-work-FINAL-authored-by-me",
                "titulo": "",
                "clase": "obra",
                "fecha": None,
                "resumen": None,
                "etiquetas": ["archive"],
                "peso": 2,
                "medio": {"tipo": "imagen", "src": "posts/observed.mp4"},
                "estado": "observada",
                "extra": {"percibido": "Blue form observed by a machine."},
            },
            {
                "id": "practice-code",
                "titulo": "Archive helper",
                "clase": "codigo",
                "fecha": None,
                "resumen": None,
                "etiquetas": ["code"],
                "peso": 1,
                "medio": {"tipo": "texto"},
                "estado": "observada",
            },
        ],
        "vinculos": [
            {
                "de": "artist-name/famous-work-FINAL-authored-by-me",
                "a": "declared-work",
                "peso": 0.8,
                "clase": "semantico",
            }
        ],
        "meta": {"por_clase": {"obra": 2, "codigo": 1}},
    }


def _write_archive(root: Path, payload: dict) -> Path:
    archive_path = root / "datos" / "archivo.json"
    archive_path.parent.mkdir(parents=True)
    archive_path.write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return archive_path


def test_archive_view_endpoint_is_deterministic_and_traceable(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    _write_archive(tmp_path, _archive_fixture())
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))

    first, first_code = hub._archive_portfolio_view_read_only()
    second, second_code = hub._archive_portfolio_view_read_only()

    assert (first_code, second_code) == (200, 200)
    assert first == second
    assert first["schema"] == "mak-archive-portfolio-view-v1"
    assert first["source"]["input_hash"].startswith("sha256:")
    assert all(row["source_ref"].startswith("iskvw:piece:")
               for row in first["items"])
    assert first["reconciliation"]["truth_promotions"] == 0


def test_composed_archive_envelope_validates_base_and_contracurator_binding(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    _write_archive(tmp_path, _archive_fixture())
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))

    payload, code = hub._archive_portfolio_view_read_only()

    assert code == 200
    assert hub._validate_archive_portfolio_envelope(payload) is True
    assert "contracurator" in payload

    tampered = copy.deepcopy(payload)
    tampered["contracurator"]["input"]["source_hash"] = "sha256:" + "0" * 64
    with pytest.raises(ValueError, match="source_hash_mismatch"):
        hub._validate_archive_portfolio_envelope(tampered)


def test_get_route_emits_the_existing_contract(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    _write_archive(tmp_path, _archive_fixture())
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))
    captured = {}

    class Handler:
        path = "/api/portfolio/archive-view"
        do_GET = hub.H.do_GET

        def _json(self, payload, code=200):
            captured.update({"payload": payload, "code": code})

    Handler().do_GET()

    assert captured["code"] == 200
    assert captured["payload"]["schema"] == "mak-archive-portfolio-view-v1"
    assert captured["payload"]["source"]["path_hint"] == (
        "iskvw/datos/archivo.json")


def test_portfolio_review_context_route_preserves_unbound_contract(monkeypatch) -> None:
    hub = _load_hub()
    monkeypatch.setattr(hub, "_portfolio_review_context_read_only", lambda project_id: ({
        "schema": "mak-portfolio-review-context-v1",
        "available": True,
        "read_only": True,
        "relation": {"status": "unbound", "selection_effect": "none"},
    }, 200))
    captured = {}

    class Handler:
        path = "/api/portfolio/review-context?project_id=project-1"
        do_GET = hub.H.do_GET

        def _json(self, payload, code=200):
            captured.update({"payload": payload, "code": code})

    Handler().do_GET()

    assert captured["code"] == 200
    assert captured["payload"]["schema"] == "mak-portfolio-review-context-v1"


def test_operation_receipt_route_is_read_only_and_scope_bound() -> None:
    hub = _load_hub()
    payload, code = hub._portfolio_operation_receipt_read_only()

    assert code == 200
    assert payload["schema"] == "mak-operation-receipt-v1"
    assert payload["status"] == "executed_structural_only"
    assert payload["operation"]["name"] == "expand_library_program"
    assert payload["operation"]["expanded_count"] == 16
    assert payload["control"] == {
        "database_write": False,
        "decision_write": False,
        "selection_effect": "none",
        "promotion": "none",
        "publication": False,
        "semantic_equivalence_authorized": False,
    }


def test_vizz_measurement_status_route_preserves_unknown_and_controls() -> None:
    hub = _load_hub()
    payload, code = hub._portfolio_vizz_measurement_status_read_only()

    assert code == 200
    assert payload["schema"] == "mak-vizz-measurement-status-v1"
    assert payload["status"] == "unknown_measurement_refused"
    assert payload["measurement"]["unknown"] is True
    assert payload["measurement"]["triangulation_attempted"] is False
    assert payload["measurement"]["depth_result_present"] is False
    assert len(payload["provenance"]["calibration_audit_sha256"]) == 64
    assert payload["provenance"]["calibration_provenance_ref"] is None
    assert payload["control"]["selection_effect"] == "none"
    assert payload["control"]["promotion"] == "none"
    assert payload["control"]["publication"] is False


def test_vizz_lineage_status_route_keeps_current_state_and_revision_context() -> None:
    hub = _load_hub()
    payload, code = hub._portfolio_vizz_lineage_status_read_only()

    assert code == 200
    assert payload["schema"] == "mak-vizz-lineage-status-v1"
    assert payload["status"] == "revision_context_only"
    assert payload["current"]["status"] == "unknown_measurement_refused"
    assert payload["revision"]["status"] == "revision_accepted"
    assert payload["revision"]["previous_artifact_sha256"] == payload["current"]["sha256"]
    assert payload["revision"]["current_artifact_sha256"] != payload["current"]["sha256"]
    assert payload["control"]["current_state_replaced"] is False
    assert payload["control"]["selection_effect"] == "none"
    assert payload["control"]["promotion"] == "none"
    assert payload["control"]["publication"] is False


def test_structural_delta_status_route_preserves_revision_only_boundary() -> None:
    hub = _load_hub()
    payload, code = hub._portfolio_structural_delta_status_read_only()

    assert code == 200
    assert payload["schema"] == "mak-structural-delta-status-v1"
    assert payload["status"] == "revision_only_delta"
    assert payload["delta"]["evaluated_keys"] == 17
    assert payload["delta"]["shared_keys"] == 2
    assert payload["delta"]["residue_keys"] == 15
    assert payload["control"]["learning_demonstrated"] is False
    assert payload["control"]["selection_effect"] == "none"
    assert payload["control"]["promotion"] == "none"
    assert payload["control"]["publication"] is False


def test_persistent_hub_serves_react_context_artifact(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    context = tmp_path / "context"
    context.mkdir()
    (context / "flujo_hub.html").write_text(
        "<html>projectReviewQueue</html>", encoding="utf-8")
    monkeypatch.setattr(hub, "_REPO_ROOT", str(tmp_path))
    captured = {}

    class Handler:
        path = "/context/flujo_hub.html"
        do_GET = hub.H.do_GET

        def _send_bytes(self, data, ctype="application/octet-stream", code=200):
            captured.update({"data": data, "ctype": ctype, "code": code})

        def _send(self, body, ctype="text/html; charset=utf-8", code=200):
            captured.update({"data": body.encode(), "ctype": ctype, "code": code})

    Handler().do_GET()

    assert captured["code"] == 200
    assert captured["ctype"] == "text/html; charset=utf-8"
    assert b"projectReviewQueue" in captured["data"]


def test_legacy_hub_links_to_persistent_work_panel() -> None:
    hub = _load_hub()

    assert 'href="/context/flujo_hub.html"' in hub.PAGINA
    assert "panel de trabajo" in hub.PAGINA


def test_authorial_looking_path_remains_observation_not_claim(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    _write_archive(tmp_path, _archive_fixture())
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))

    payload, code = hub._archive_portfolio_view_read_only()
    observed = next(
        row for row in payload["items"]
        if row["item_id"] == "artist-name/famous-work-FINAL-authored-by-me")

    assert code == 200
    assert observed["title"] is None
    assert observed["roles"] == ["observed_archive_piece"]
    assert observed["epistemic_status"] == "observed_source_record"
    assert observed["observed_description_is_not_author_statement"] is True
    assert payload["provenance"]["filename_is_not_authorship"] is True


def test_malformed_archive_fails_closed_without_partial_view(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    archive_path = tmp_path / "datos" / "archivo.json"
    archive_path.parent.mkdir(parents=True)
    archive_path.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(hub, "PORTFOLIO_ROOT", str(tmp_path))

    payload, code = hub._archive_portfolio_view_read_only()

    assert code == 503
    assert payload == {
        "ok": False,
        "error": "archive_portfolio_view_invalid",
        "detail": "JSONDecodeError",
    }


def test_source_resolver_prefers_compatible_local_motor_and_honors_override(
    tmp_path: Path, monkeypatch,
) -> None:
    hub = _load_hub()
    sibling = tmp_path / "flujo" / "src" / "flujo" / "knowledge"
    sibling.mkdir(parents=True)
    (sibling / "product_view.py").write_text(
        "def project_archive_portfolio_view(*, human_triage=None): pass\n",
        encoding="utf-8",
    )

    chosen, mode = hub._resolve_flujo_source_root(str(tmp_path))
    assert Path(chosen) == tmp_path / "flujo" / "src"
    assert mode == "compatible_local_source"

    (sibling / "product_view.py").write_text(
        "# human_triage is mentioned, but not part of the callable contract\n"
        "def project_archive_portfolio_view(archive): pass\n",
        encoding="utf-8",
    )
    chosen, mode = hub._resolve_flujo_source_root(str(tmp_path))
    assert Path(chosen) == tmp_path / "flujo" / "src"
    assert mode == "sibling_fallback"

    override = tmp_path / "forced-source"
    monkeypatch.setenv("FLUJO_SOURCE_ROOT", str(override))
    chosen, mode = hub._resolve_flujo_source_root(str(tmp_path))
    assert Path(chosen) == override
    assert mode == "explicit_override"


def test_project_review_queue_is_read_only_and_actionable(tmp_path: Path, monkeypatch) -> None:
    hub = _load_hub()
    database = tmp_path / "mak_knowledge.db"
    record = {
        "title": "pending-project",
        "reconstruction": {},
        "unknowns": ["missing evidence"],
        "evidence": [],
    }
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE project_records (project_id TEXT, title TEXT, state TEXT, ir_json TEXT, updated_at TEXT)"
        )
        connection.execute(
            "INSERT INTO project_records VALUES (?, ?, ?, ?, ?)",
            ("project-1", "pending-project", "review_required", json.dumps(record), "2026-09-13"),
        )
        connection.commit()
    monkeypatch.setattr(hub, "_learning_db_path", lambda: database)

    payload = hub._project_review_queue_read_only()

    assert payload["schema"] == "mak-review-queue-v1"
    assert payload["available"] is True
    assert payload["read_only"] is True
    assert payload["summary"]["pending"] == 1
    assert payload["items"][0]["project_id"] == "project-1"
    assert payload["items"][0]["decisions_available"]
    assert payload["controls"] == {
        "database_write": False,
        "decision_write": False,
        "promotion": "none",
        "publication": False,
    }
    assert payload["provenance"]["decisions_require_external_human_actor"] is True
