"""
Tests for src/flujo/serve/server.py -- API endpoints of the local hub server.

Coverage: module imports cleanly, API functions return expected shapes on valid
input, error paths handled gracefully. Tests handler functions directly without
spinning a live server.
"""
from __future__ import annotations

import pytest
from flujo.serve.server import (
    api_health_stats,
    api_materials,
    api_index_brief,
    api_list_jobs,
    api_parse_pedido,
    api_list_svg_works,
    api_plano_render,
    _read_json,
)


def test_module_imports_cleanly():
    """Verify that the serve module and all endpoints are importable."""
    from flujo.serve import server  # noqa: F401
    assert hasattr(server, "api_health_stats")
    assert hasattr(server, "api_materials")
    assert hasattr(server, "api_plano_render")


def test_api_health_stats_returns_list_of_dicts():
    """Health stats should return a list of stat cards with k/v/s keys."""
    result = api_health_stats()
    assert isinstance(result, list)
    assert len(result) >= 3
    for stat in result:
        assert isinstance(stat, dict)
        assert "k" in stat  # key/label
        assert "v" in stat  # value
        assert "s" in stat  # subtitle
        assert isinstance(stat["k"], str)
        assert isinstance(stat["v"], str)
        assert isinstance(stat["s"], str)


def test_api_materials_returns_items():
    """Materials endpoint should return dict with 'items' key containing list."""
    result = api_materials()
    assert isinstance(result, dict)
    assert "items" in result
    assert isinstance(result["items"], list)
    # Each item should have basic structure
    if result["items"]:
        item = result["items"][0]
        assert "id" in item or "category" in item


def test_api_index_brief_returns_availability_info():
    """Index brief should indicate whether index is available."""
    result = api_index_brief()
    assert isinstance(result, dict)
    assert "disponible" in result
    assert isinstance(result["disponible"], bool)
    # If available, should have metadata fields
    if result["disponible"]:
        assert "base" in result or "n_archivos" in result


def test_api_list_jobs_returns_structured_dict():
    """Jobs list should return dict with jobs array, count, and metadata."""
    result = api_list_jobs()
    assert isinstance(result, dict)
    assert "jobs" in result
    assert "count" in result
    assert "connected" in result
    assert "source" in result
    assert isinstance(result["jobs"], list)
    assert isinstance(result["count"], int)
    assert result["count"] == len(result["jobs"])


def test_api_list_jobs_each_job_has_required_fields():
    """Each job in the list should have required fields."""
    result = api_list_jobs()
    for job in result["jobs"]:
        assert "name" in job
        assert "path" in job
        assert "estado" in job
        assert isinstance(job["name"], str)
        assert isinstance(job["path"], str)
        assert isinstance(job["estado"], str)


def test_api_parse_pedido_returns_structured_dict():
    """Parse pedido should return dict with tipo, medidas, formato, tool, etc."""
    result = api_parse_pedido("flyer para el evento")
    assert isinstance(result, dict)
    assert "tipo" in result
    assert "medidas" in result
    assert "formato" in result
    assert "tool" in result
    assert "area" in result
    assert "match" in result
    assert "source" in result


def test_api_parse_pedido_recognizes_flyer():
    """Parse pedido should recognize 'flyer' keyword."""
    result = api_parse_pedido("flyer para la fiesta")
    assert result["tipo"] == "flyer"
    assert "10x14" in result["medidas"]


def test_api_parse_pedido_recognizes_etiqueta():
    """Parse pedido should recognize 'etiqueta' keyword."""
    result = api_parse_pedido("etiqueta de suplementos")
    assert result["tipo"] == "etiqueta"
    assert "16.5" in result["medidas"] or "165" in result["medidas"]


def test_api_parse_pedido_handles_none_input():
    """Parse pedido should handle None gracefully."""
    result = api_parse_pedido(None)
    assert isinstance(result, dict)
    assert "tipo" in result
    # Should default to something sensible, not crash


def test_api_parse_pedido_handles_empty_string():
    """Parse pedido should handle empty string gracefully."""
    result = api_parse_pedido("")
    assert isinstance(result, dict)
    assert "tipo" in result


def test_api_list_svg_works_returns_groups_dict():
    """SVG works should return dict with groups, count, and root."""
    result = api_list_svg_works()
    assert isinstance(result, dict)
    assert "groups" in result
    assert "count" in result
    assert "root" in result
    assert isinstance(result["groups"], dict)
    assert isinstance(result["count"], int)


def test_api_plano_render_valid_evento():
    """Plano render should return layout, rider, and costos for valid evento."""
    evento = {
        "nombre": "Evento Prueba",
        "duracion_horas": 4,
        "asistentes_estimados": 100,
        "pack": "INFO",
    }
    result = api_plano_render(evento)
    assert isinstance(result, dict)
    assert "layout" in result
    assert "rider" in result
    assert "costos" in result
    assert "pack" in result
    assert "pack_label" in result


def test_api_plano_render_layout_has_required_structure():
    """Rendered layout should have dimensions and zones."""
    evento = {
        "nombre": "Test Event",
        "duracion_horas": 3,
        "asistentes_estimados": 50,
    }
    result = api_plano_render(evento)
    layout = result["layout"]
    assert "w" in layout
    assert "h" in layout
    assert "title" in layout
    assert "zones" in layout
    assert isinstance(layout["zones"], list)


def test_api_plano_render_rider_is_string():
    """Rider output should be a formatted string."""
    evento = {
        "nombre": "Test Event",
        "duracion_horas": 2,
        "asistentes_estimados": 30,
    }
    result = api_plano_render(evento)
    assert isinstance(result["rider"], str)
    assert len(result["rider"]) > 0
    assert "RIDER" in result["rider"].upper()


def test_api_plano_render_costos_is_string():
    """Costos output should be a formatted string with total."""
    evento = {
        "nombre": "Test Event",
        "duracion_horas": 2,
        "asistentes_estimados": 30,
    }
    result = api_plano_render(evento)
    assert isinstance(result["costos"], str)
    assert len(result["costos"]) > 0
    assert "TOTAL" in result["costos"].upper() or "$" in result["costos"]


def test_api_plano_render_empty_evento_dict():
    """Plano render should handle empty evento dict with defaults."""
    result = api_plano_render({})
    assert isinstance(result, dict)
    assert "layout" in result
    assert "rider" in result
    # Should not crash, uses defaults


def test_api_plano_render_none_evento():
    """Plano render should handle None evento gracefully."""
    result = api_plano_render(None)
    assert isinstance(result, dict)
    assert "layout" in result


def test_read_json_missing_file():
    """_read_json should return default when file doesn't exist."""
    result = _read_json("/nonexistent/path/file.json", {"default": "value"})
    assert result == {"default": "value"}


def test_read_json_returns_default_on_error():
    """_read_json should return default on any exception (corrupt JSON, etc)."""
    result = _read_json("/definitely/not/a/real/path.json", [])
    assert result == []


def test_api_plano_render_total_is_integer():
    """Plano render total should be an integer."""
    evento = {
        "nombre": "Test",
        "duracion_horas": 2,
        "asistentes_estimados": 50,
    }
    result = api_plano_render(evento)
    assert "total" in result
    assert isinstance(result["total"], int)
    assert result["total"] > 0
