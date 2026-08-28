from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


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
