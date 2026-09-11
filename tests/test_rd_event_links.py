from __future__ import annotations

import json

from flujo.rd.panel import datos_panel, rd_event_link


def _root(tmp_path):
    (tmp_path / "data" / "productoras").mkdir(parents=True)
    (tmp_path / "knowledge" / "logos" / "vector").mkdir(parents=True)
    (tmp_path / "knowledge" / "venues").mkdir(parents=True)
    (tmp_path / "data" / "productoras" / "acme.json").write_text(json.dumps({
        "name": "Acme",
        "eventos": [{
            "nombre": "Fecha Acme",
            "fecha": "2026-11-20",
            "venue": "Espacio Riesco",
            "fuente": "https://example.test/flyer",
        }],
    }), encoding="utf-8")
    (tmp_path / "knowledge" / "venues" / "espacio_riesco.yaml").write_text(
        "name: Espacio Riesco\n", encoding="utf-8")
    return tmp_path


def test_event_link_is_exact_and_pending_without_operating_data(tmp_path):
    root = _root(tmp_path)
    event = datos_panel(root)["productoras"][0]["eventos"][0]
    result = rd_event_link(root, event["event_key"])
    assert result["status"] == "pending_review"
    assert result["productora_slug"] == "acme"
    assert result["event"]["venue_link"]["status"] == "exact"
    assert set(result["missing"]) == {"pack", "duracion_horas", "asistentes_estimados"}


def test_event_link_consumes_existing_plano_engine_with_explicit_draft(tmp_path):
    root = _root(tmp_path)
    event = datos_panel(root)["productoras"][0]["eventos"][0]
    result = rd_event_link(root, event["event_key"], {
        "pack": "INFO",
        "duracion_horas": 4,
        "asistentes_estimados": 250,
    })
    assert result["status"] == "ready"
    assert result["render"]["layout"]["pack"] == "INFO"
    assert result["render"]["rider"]
