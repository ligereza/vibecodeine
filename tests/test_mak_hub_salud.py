#!/usr/bin/env python3
"""tests/test_mak_hub_salud.py -- Tests for hub.py _salud_proveedores()
(widget "salud proveedores" del panel research, endpoint GET /api/salud).

No network, no live server. hub.py is safe to import: server only starts
under `if __name__ == "__main__"`.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


class TestSaludProveedores:
    def test_archivo_valido_scores_y_orden(self, tmp_path, monkeypatch):
        ruta = os.path.join(str(tmp_path), "salud_proveedores.json")
        ahora = time.time()
        _write_json(ruta, {"desde": ahora, "proveedores": {
            "groq": {"successes": 8, "timeouts": 2, "api_errors": 0, "errors": 0},
            "azure": {"successes": 10, "timeouts": 0, "api_errors": 0, "errors": 0},
            "ollama": {"successes": 3, "timeouts": 3, "api_errors": 0, "errors": 0},
        }})
        monkeypatch.setattr(hub, "SALUD_PROVEEDORES", ruta)
        out = hub._salud_proveedores()
        nombres = [p["nombre"] for p in out["proveedores"]]
        assert nombres == ["azure", "groq", "ollama"]
        azure = out["proveedores"][0]
        assert azure["score"] == 1.0
        assert azure["intentos"] == 10
        assert out["desde"] == ahora

    def test_degradado_marcado(self, tmp_path, monkeypatch):
        ruta = os.path.join(str(tmp_path), "salud_proveedores.json")
        _write_json(ruta, {"desde": time.time(), "proveedores": {
            "malo": {"successes": 1, "timeouts": 4, "api_errors": 0, "errors": 0},
        }})
        monkeypatch.setattr(hub, "SALUD_PROVEEDORES", ruta)
        out = hub._salud_proveedores()
        p = out["proveedores"][0]
        assert p["intentos"] == 5
        assert p["score"] == 0.2
        assert p["degradado"] is True

    def test_cero_intentos_score_cero_sin_division(self, tmp_path, monkeypatch):
        ruta = os.path.join(str(tmp_path), "salud_proveedores.json")
        _write_json(ruta, {"desde": time.time(), "proveedores": {
            "nuevo": {"successes": 0, "timeouts": 0, "api_errors": 0, "errors": 0},
        }})
        monkeypatch.setattr(hub, "SALUD_PROVEEDORES", ruta)
        out = hub._salud_proveedores()
        p = out["proveedores"][0]
        assert p["intentos"] == 0
        assert p["score"] == 0.0
        assert p["degradado"] is False

    def test_archivo_ausente_retorna_vacio(self, tmp_path, monkeypatch):
        ruta = os.path.join(str(tmp_path), "no_existe.json")
        monkeypatch.setattr(hub, "SALUD_PROVEEDORES", ruta)
        out = hub._salud_proveedores()
        assert out == {"proveedores": [], "desde": None}

    def test_archivo_corrupto_retorna_vacio(self, tmp_path, monkeypatch):
        ruta = os.path.join(str(tmp_path), "salud_proveedores.json")
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("{esto no es json valido")
        monkeypatch.setattr(hub, "SALUD_PROVEEDORES", ruta)
        out = hub._salud_proveedores()
        assert out == {"proveedores": [], "desde": None}

    def test_ventana_vencida_retorna_vacio(self, tmp_path, monkeypatch):
        ruta = os.path.join(str(tmp_path), "salud_proveedores.json")
        vieja = time.time() - hub.SALUD_PROVEEDORES_VENTANA - 60
        _write_json(ruta, {"desde": vieja, "proveedores": {
            "groq": {"successes": 5, "timeouts": 0, "api_errors": 0, "errors": 0},
        }})
        monkeypatch.setattr(hub, "SALUD_PROVEEDORES", ruta)
        out = hub._salud_proveedores()
        assert out == {"proveedores": [], "desde": None}


class TestPaginaMarcoUnico:
    """PAGINA se reconstruyo como marco fino + iframe a pantalla completa
    (interfaz PRO unica). Estos asserts son baratos y evitan una regresion
    de template que reintroduzca el canvas de nodos viejo."""

    def test_contiene_iframes_de_ambos_deptos(self):
        assert 'id="ifr-research"' in hub.PAGINA
        assert 'id="ifr-codex"' in hub.PAGINA

    def test_contiene_tabs_research_codex(self):
        assert 'data-dep="research"' in hub.PAGINA
        assert 'data-dep="codex"' in hub.PAGINA

    def test_no_contiene_canvas_organismo_viejo(self):
        assert "crearEstatico" not in hub.PAGINA
        assert 'id="circuitos"' not in hub.PAGINA
        assert "nodo-mic" not in hub.PAGINA
