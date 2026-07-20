#!/usr/bin/env python3
"""test_mak_pausa.py -- tests para pausa.py + pausa-en-error de research.py (pytest).

Contrato: cultura/mak_research/pausa.py (checkpoints), research.py (pausa
al fallar el LLM/Tavily), worker.py (reconoce la marca PAUSADO). worker.py
importa fcntl (Linux-only) por eso NUNCA se importa aca a nivel de modulo;
research.py y research_lib.py son stdlib puro y se pueden importar en
Windows sin problema (verificado: sin fcntl en la cadena de imports).
"""
import json
import sys
from pathlib import Path

import pytest

test_dir = Path(__file__).parent
repo_root = test_dir.parent
sys.path.insert(0, str(repo_root / "cultura" / "mak_research"))

import pausa  # noqa: E402
import research  # noqa: E402 -- puro stdlib, sin fcntl en la cadena


# ---------------------------------------------------------------------
# guardar_checkpoint / cargar_checkpoint
# ---------------------------------------------------------------------

class TestGuardarCargarCheckpoint:
    def test_roundtrip(self, tmp_path):
        datos = {"job_id": "abc-123", "tema": "algo", "i": 2}
        path = pausa.guardar_checkpoint(datos, base_dir=str(tmp_path))
        cargado = pausa.cargar_checkpoint(path)
        assert cargado == datos

    def test_job_id_en_nombre_archivo(self, tmp_path):
        datos = {"job_id": "mi-job-42", "tema": "x"}
        path = pausa.guardar_checkpoint(datos, base_dir=str(tmp_path))
        assert Path(path).name == "mi-job-42.json"

    def test_mkdir_p(self, tmp_path):
        destino = tmp_path / "no" / "existe" / "aun"
        datos = {"job_id": "j1"}
        path = pausa.guardar_checkpoint(datos, base_dir=str(destino))
        assert Path(path).exists()
        assert Path(path).parent == destino

    def test_devuelve_ruta_absoluta(self, tmp_path):
        datos = {"job_id": "j2"}
        path = pausa.guardar_checkpoint(datos, base_dir=str(tmp_path))
        assert Path(path).is_absolute()

    def test_default_base_dir_usa_dir_checkpoints(self, tmp_path, monkeypatch):
        # nunca debe escribir al home real: se monkeypatchea DIR_CHECKPOINTS
        monkeypatch.setattr(pausa, "DIR_CHECKPOINTS", str(tmp_path / "cp"))
        datos = {"job_id": "j3"}
        path = pausa.guardar_checkpoint(datos)
        assert str(tmp_path) in path
        assert Path(path).exists()


# ---------------------------------------------------------------------
# aplicar_accion
# ---------------------------------------------------------------------

class TestAplicarAccion:
    def _make(self, tmp_path, **extra):
        datos = {"job_id": "j", "tema": "t", "current": "orig", "saltar": False}
        datos.update(extra)
        return pausa.guardar_checkpoint(datos, base_dir=str(tmp_path))

    def test_reintentar_no_op(self, tmp_path):
        path = self._make(tmp_path)
        antes = pausa.cargar_checkpoint(path)
        resultado = pausa.aplicar_accion(path, "reintentar")
        assert resultado == antes

    def test_editar_setea_current(self, tmp_path):
        path = self._make(tmp_path)
        resultado = pausa.aplicar_accion(path, "editar", texto="nueva consulta")
        assert resultado["current"] == "nueva consulta"

    def test_saltar_setea_flag(self, tmp_path):
        path = self._make(tmp_path)
        resultado = pausa.aplicar_accion(path, "saltar")
        assert resultado["saltar"] is True

    def test_accion_desconocida_raises(self, tmp_path):
        path = self._make(tmp_path)
        with pytest.raises(ValueError):
            pausa.aplicar_accion(path, "volar")

    def test_persiste_a_disco(self, tmp_path):
        path = self._make(tmp_path)
        pausa.aplicar_accion(path, "editar", texto="persistido")
        recargado = pausa.cargar_checkpoint(path)
        assert recargado["current"] == "persistido"

    def test_accion_desconocida_no_muta_disco(self, tmp_path):
        path = self._make(tmp_path)
        antes = pausa.cargar_checkpoint(path)
        with pytest.raises(ValueError):
            pausa.aplicar_accion(path, "invalida")
        assert pausa.cargar_checkpoint(path) == antes


# ---------------------------------------------------------------------
# formatear_marca / parsear_marca
# ---------------------------------------------------------------------

class TestMarca:
    def test_formatear_incluye_marca_y_path(self):
        linea = pausa.formatear_marca("/tmp/x.json", "motivo simple")
        assert linea.startswith(pausa.MARCA)
        assert "/tmp/x.json" in linea

    def test_formatear_trunca_a_200(self):
        motivo = "x" * 500
        linea = pausa.formatear_marca("/p", motivo)
        _, motivo_out = pausa.parsear_marca(linea)
        assert len(motivo_out) <= 200

    def test_formatear_limpia_saltos_linea(self):
        motivo = "linea uno\nlinea dos\r\notra"
        linea = pausa.formatear_marca("/p", motivo)
        assert "\n" not in linea
        assert "\r" not in linea

    def test_roundtrip(self):
        linea = pausa.formatear_marca("/ruta/checkpoints/j1.json", "algo fallo")
        resultado = pausa.parsear_marca(linea)
        assert resultado == ("/ruta/checkpoints/j1.json", "algo fallo")

    def test_no_marker_devuelve_none(self):
        assert pausa.parsear_marca("STATUS: buscando algo") is None
        assert pausa.parsear_marca("") is None

    def test_motivo_con_pipe_interno_split_en_primero(self):
        linea = pausa.formatear_marca("/p/j.json", "error: a | b | c")
        resultado = pausa.parsear_marca(linea)
        assert resultado == ("/p/j.json", "error: a | b | c")


# ---------------------------------------------------------------------
# research.py: pausa-en-error y reanudacion (con LLM/tavily/fetch mockeados)
# ---------------------------------------------------------------------

class FakeLLM:
    """Reemplaza research_lib.LLM: nunca pega a la red."""

    def __init__(self, providers):
        self.stats = {}
        self.errors = []
        self.order = [p.strip() for p in providers.split(",") if p.strip()]

    def call(self, system, user, max_tok=1024, order=None):
        raise AssertionError("FakeLLM.call no deberia invocarse en este test")


class FinalizarLLM(FakeLLM):
    """Decide FINALIZAR de una y genera cualquier texto de informe."""

    def call(self, system, user, max_tok=1024, order=None):
        return "FINALIZAR: cobertura suficiente (informe fake)", "fake"


class RompeLLM(FakeLLM):
    """Siempre revienta -- simula que se agotaron los proveedores."""

    def call(self, system, user, max_tok=1024, order=None):
        raise RuntimeError("Todos los proveedores LLM fallaron. Ultimo: fake")


class TestResearchResume:
    def test_resume_restaura_estado_y_continua_desde_i(self, monkeypatch):
        ck = {
            "job_id": "job-resume-1",
            "tema": "tema-x",
            "params": {"iteraciones": 3, "depth": "basic",
                      "providers": "groq", "densidad": "medio",
                      "sin_marco": False},
            "i": 1,
            "current": "tema-x (angulo 2)",
            "query_history": ["tema-x"],
            "seen_urls": [],
            "findings": [],
            "fase_fallida": "decidir",
            "motivo": "algo fallo antes",
            "saltar": False,
            "ts": 0,
        }
        monkeypatch.setattr(research, "LLM", FinalizarLLM)
        monkeypatch.setattr(research, "web_search",
                            lambda *a, **k: {"results": [], "answer": None})

        resultado = research.investigar("tema-x", iteraciones=3, reanudar=ck)

        # arranco en i=1 (no repitio la iteracion 0): la query original
        # sigue siendo la unica previa mas la nueva de esta iteracion.
        assert resultado["meta"]["queries"] == ["tema-x", "tema-x (angulo 2)"]
        assert resultado["meta"]["iterations"] == 2

    def test_pausa_en_fase_fuentes_por_runtimeerror(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(pausa, "DIR_CHECKPOINTS", str(tmp_path))
        monkeypatch.setattr(research, "LLM", RompeLLM)
        monkeypatch.setattr(research, "web_search", lambda *a, **k: {
            "results": [{"url": "http://x.test", "title": "t",
                        "content": "contenido corto"}],
            "answer": None,
        })
        monkeypatch.setattr(research, "fetch_url", lambda url, limit=4000: "x" * 300)

        with pytest.raises(SystemExit) as exc:
            research.investigar("tema-pausa", iteraciones=1)
        assert exc.value.code == 3

        salida = capsys.readouterr().out
        assert pausa.MARCA in salida
        linea_marca = next(l for l in salida.splitlines() if l.startswith(pausa.MARCA))
        path, motivo = pausa.parsear_marca(linea_marca)
        assert Path(path).exists()
        ck = pausa.cargar_checkpoint(path)
        assert ck["fase_fallida"] == "fuentes"
        assert ck["tema"] == "tema-pausa"
        assert ck["saltar"] is False
        assert "Todos los proveedores" in motivo or "fallaron" in motivo

    def test_saltar_informe_devuelve_placeholder_sin_llamar_llm(self, monkeypatch):
        ck = {
            "job_id": "job-saltar-informe",
            "tema": "tema-y",
            "params": {"iteraciones": 2, "depth": "basic",
                      "providers": "groq", "densidad": "medio",
                      "sin_marco": False},
            "i": 2,
            "current": "tema-y",
            "query_history": ["tema-y", "tema-y (angulo 2)"],
            "seen_urls": [],
            "findings": [{"type": "tavily_answer", "iteration": 1,
                         "query": "tema-y", "content": "algo"}],
            "fase_fallida": "informe",
            "motivo": "se cayeron los proveedores",
            "saltar": True,
            "ts": 0,
        }
        # FakeLLM.call haria AssertionError si se llegara a invocar
        monkeypatch.setattr(research, "LLM", FakeLLM)

        resultado = research.investigar("tema-y", iteraciones=2, reanudar=ck)

        assert resultado["report"].startswith(
            "[Informe omitido por accion humana: saltar]")
        assert resultado["findings"] == ck["findings"]
