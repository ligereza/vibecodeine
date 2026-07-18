#!/usr/bin/env python3
"""tests/test_mak_hub_eventos.py -- Tests for hub.py eventos integrity flag
(_eventos_depto, _job_ids_conocidos, _marcar_sin_job).

No network, no live server. hub.py is safe to import: server only starts
under `if __name__ == "__main__"`.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

import hub  # noqa: E402


def _write_jsonl(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


class TestEventosDepto:
    def test_regresion_linea_malformada_no_vacia_todo(self, tmp_path, monkeypatch):
        """Regla anterior: json.loads en una sola lista rompia todo el archivo por
        una linea mala. Ahora debe saltarse solo la linea mala."""
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        ruta = os.path.join(str(tmp_path), "research", "eventos.jsonl")
        _write_jsonl(ruta, [
            json.dumps({"tipo": "llm_result", "resumen": "bueno1", "job_id": "j1"}),
            "{esto no es json valido",
            json.dumps({"tipo": "paso", "resumen": "bueno2", "job_id": "j2"}),
        ])
        evs = hub._eventos_depto("research")
        assert len(evs) == 2
        assert evs[0]["resumen"] == "bueno1"
        assert evs[1]["resumen"] == "bueno2"

    def test_archivo_inexistente_retorna_lista_vacia(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        evs = hub._eventos_depto("research")
        assert evs == []

    def test_respeta_limite_n(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hub, "HOME", str(tmp_path))
        ruta = os.path.join(str(tmp_path), "research", "eventos.jsonl")
        _write_jsonl(ruta, [json.dumps({"resumen": "e%d" % i}) for i in range(10)])
        evs = hub._eventos_depto("research", n=3)
        assert len(evs) == 3
        assert evs[-1]["resumen"] == "e9"


class TestJobIdsConocidos:
    def test_local_jobs_jsonl_provee_ids(self, tmp_path, monkeypatch):
        research_jobs = os.path.join(str(tmp_path), "research_jobs.jsonl")
        _write_jsonl(research_jobs, [
            json.dumps({"job_id": "j1", "tema": "x"}),
            json.dumps({"job_id": "j2", "tema": "y"}),
        ])
        monkeypatch.setattr(hub, "RESEARCH_JOBS", research_jobs)
        monkeypatch.setattr(hub, "_http_json", lambda url, timeout=2.0: None)
        ids, ok = hub._job_ids_conocidos("research")
        assert ids == {"j1", "j2"}
        assert ok is True

    def test_ambas_fuentes_fallan_ok_false(self, tmp_path, monkeypatch):
        missing = os.path.join(str(tmp_path), "no_existe.jsonl")
        monkeypatch.setattr(hub, "RESEARCH_JOBS", missing)
        monkeypatch.setattr(hub, "_http_json", lambda url, timeout=2.0: None)
        ids, ok = hub._job_ids_conocidos("research")
        assert ids == set()
        assert ok is False

    def test_local_existe_pero_vacio_cuenta_ok(self, tmp_path, monkeypatch):
        """El archivo existe y es legible, aunque no tenga job_id -> ok True."""
        research_jobs = os.path.join(str(tmp_path), "research_jobs.jsonl")
        _write_jsonl(research_jobs, [])
        monkeypatch.setattr(hub, "RESEARCH_JOBS", research_jobs)
        monkeypatch.setattr(hub, "_http_json", lambda url, timeout=2.0: None)
        ids, ok = hub._job_ids_conocidos("research")
        assert ids == set()
        assert ok is True

    def test_live_proxy_provee_ids_en_vuelo(self, tmp_path, monkeypatch):
        missing = os.path.join(str(tmp_path), "no_existe.jsonl")
        monkeypatch.setattr(hub, "RESEARCH_JOBS", missing)
        monkeypatch.setattr(
            hub, "_http_json",
            lambda url, timeout=2.0: [{"job_id": "jlive1"}, {"job_id": "jlive2"}],
        )
        ids, ok = hub._job_ids_conocidos("research")
        assert ids == {"jlive1", "jlive2"}
        assert ok is True

    def test_union_de_ambas_fuentes(self, tmp_path, monkeypatch):
        research_jobs = os.path.join(str(tmp_path), "research_jobs.jsonl")
        _write_jsonl(research_jobs, [json.dumps({"job_id": "jlocal"})])
        monkeypatch.setattr(hub, "RESEARCH_JOBS", research_jobs)
        monkeypatch.setattr(
            hub, "_http_json",
            lambda url, timeout=2.0: [{"job_id": "jlive"}],
        )
        ids, ok = hub._job_ids_conocidos("research")
        assert ids == {"jlocal", "jlive"}
        assert ok is True

    def test_codex_usa_puerto_y_archivo_codex(self, tmp_path, monkeypatch):
        codex_jobs = os.path.join(str(tmp_path), "codex_jobs.jsonl")
        _write_jsonl(codex_jobs, [json.dumps({"job_id": "cj1"})])
        monkeypatch.setattr(hub, "CODEX_JOBS", codex_jobs)
        llamadas = []

        def _stub(url, timeout=2.0):
            llamadas.append(url)
            return None

        monkeypatch.setattr(hub, "_http_json", _stub)
        ids, ok = hub._job_ids_conocidos("codex")
        assert ids == {"cj1"}
        assert ok is True
        assert "8891" in llamadas[0]


class TestMarcarSinJob:
    def test_evento_huerfano_se_marca(self):
        evs = [{"job_id": "j-fantasma", "resumen": "x"}]
        out = hub._marcar_sin_job(evs, {"j1", "j2"}, True)
        assert out[0]["sin_job"] is True

    def test_evento_con_job_local_no_se_marca(self):
        evs = [{"job_id": "j1", "resumen": "x"}]
        out = hub._marcar_sin_job(evs, {"j1", "j2"}, True)
        assert "sin_job" not in out[0]

    def test_evento_con_job_solo_en_vivo_no_se_marca(self):
        evs = [{"job_id": "jlive", "resumen": "x"}]
        out = hub._marcar_sin_job(evs, {"jlive"}, True)
        assert "sin_job" not in out[0]

    def test_ambas_fuentes_fallidas_no_marca_nada(self):
        evs = [{"job_id": "j-cualquiera", "resumen": "x"}, {"resumen": "sin job_id"}]
        out = hub._marcar_sin_job(evs, set(), False)
        assert "sin_job" not in out[0]
        assert "sin_job" not in out[1]

    def test_evento_sin_job_id_se_marca_cuando_ok(self):
        evs = [{"resumen": "sin campo job_id"}]
        out = hub._marcar_sin_job(evs, {"j1"}, True)
        assert out[0]["sin_job"] is True

    def test_no_toca_otros_campos(self):
        evs = [{"job_id": "j-fantasma", "resumen": "x", "tipo": "paso", "t": "12:00"}]
        out = hub._marcar_sin_job(evs, set(), True)
        assert out[0]["resumen"] == "x"
        assert out[0]["tipo"] == "paso"
        assert out[0]["t"] == "12:00"
