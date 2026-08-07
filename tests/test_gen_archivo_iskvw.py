#!/usr/bin/env python3
"""tests/test_gen_archivo_iskvw.py -- the micelio-snapshot fallback (2026-08-01).

CI cannot reach the box: publicar_iskvw.yml runs on ubuntu-latest, and
gen_archivo_iskvw.py's desde_micelio() defaults to http://127.0.0.1:8890,
which is only the box's own research service when run ON the box. Measured
the same day: the live site published 269 vinculos and 0 of them were
clase "semantico" -- proof the live micelio never actually reaches
--fuente todo from CI. cultura/mak_plataforma/entregar_micelio.py closes
that by pushing a converted snapshot from the box itself; these tests
cover the repo side that reads it back.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import gen_archivo_iskvw as G  # noqa: E402


def test_snapshot_ausente_da_partes_vacias(tmp_path):
    # Same contract as every other optional source here: without the file,
    # it stays without it -- never an invented result.
    vacio = G.desde_micelio_snapshot(tmp_path / "no-existe.json")
    assert vacio == {"piezas": [], "vinculos": []}


def test_snapshot_presente_se_lee_tal_cual(tmp_path):
    ruta = tmp_path / "micelio.json"
    contenido = {
        "version": 1, "fuente": "micelio_snapshot", "umbral": 0.55,
        "generado": "2026-08-01T00:00:00+00:00",
        "piezas": [{"id": "obra-x", "titulo": "", "clase": "obra"}],
        "vinculos": [{"de": "obra-x", "a": "obra-y", "peso": 0.7,
                      "clase": "semantico"}],
    }
    ruta.write_text(json.dumps(contenido, ensure_ascii=False), encoding="utf-8")
    datos = G.desde_micelio_snapshot(ruta)
    assert datos["piezas"] == contenido["piezas"]
    assert datos["vinculos"] == contenido["vinculos"]
    # extra keys (version/fuente/umbral/generado) get dropped, not carried
    assert set(datos) == {"piezas", "vinculos"}


def test_snapshot_con_listas_ausentes_no_revienta(tmp_path):
    ruta = tmp_path / "parcial.json"
    ruta.write_text(json.dumps({"version": 1}), encoding="utf-8")
    assert G.desde_micelio_snapshot(ruta) == {"piezas": [], "vinculos": []}


def test_public_sustrato_filters_research_without_mutating_source():
    source = {
        "piezas": [{"id": "obra", "clase": "obra"},
                   {"id": "informe", "clase": "informe"}],
        "vinculos": [{"de": "obra", "a": "informe", "clase": "semantico"}],
    }
    public = G.contrato_archivo.sustrato_publico(source)
    assert [pieza["id"] for pieza in public["piezas"]] == ["obra"]
    assert public["vinculos"] == []
    assert len(source["piezas"]) == 2


def test_todo_cae_al_snapshot_cuando_el_micelio_en_vivo_falla(
        tmp_path, monkeypatch, capsys):
    """--fuente todo: if desde_micelio() blows up (the real CI case), main()
    must not lose the versioned snapshot -- that is the entire point of
    having one."""
    def _explota(url, umbral):
        raise TimeoutError("simulated: CI cannot reach the box")
    monkeypatch.setattr(G, "desde_micelio", _explota)

    def _snapshot_falso():
        return {
            "piezas": [{"id": "snap-obra", "titulo": "", "clase": "obra",
                       "fecha": None, "resumen": None, "etiquetas": [],
                       "peso": 1, "medio": {"tipo": "texto"},
                       "estado": "publicada", "extra": {}},
                      {"id": "snap-obra-2", "titulo": "", "clase": "obra",
                       "fecha": None, "resumen": None, "etiquetas": [],
                       "peso": 1, "medio": {"tipo": "texto"},
                       "estado": "publicada", "extra": {}}],
            "vinculos": [{"de": "snap-obra", "a": "snap-obra-2",
                         "peso": 0.9, "clase": "semantico"}],
        }
    monkeypatch.setattr(G, "desde_micelio_snapshot", _snapshot_falso)

    salida = tmp_path / "archivo.json"
    monkeypatch.setattr(sys, "argv", [
        "gen_archivo_iskvw.py", "--fuente", "todo", "--salida", str(salida),
        "--posiciones", str(tmp_path / "sin-campo.json"),
    ])
    rc = G.main()
    assert rc == 0

    aviso = capsys.readouterr().err
    assert "snapshot" in aviso  # says explicitly that it degraded, does not hide it

    datos = json.loads(salida.read_text(encoding="utf-8"))
    ids = {p["id"] for p in datos["piezas"]}
    assert "snap-obra" in ids
    clases = {v["clase"] for v in datos["vinculos"]}
    assert "semantico" in clases  # the snapshot's measured link made it through


def test_fuente_micelio_explicita_no_usa_snapshot_y_falla_fuerte(
        tmp_path, monkeypatch):
    """--fuente micelio (unlike 'todo') asks for the LIVE micelio and
    nothing else: if it does not respond, a real error -- it never
    silently degrades to a snapshot that might be stale."""
    def _explota(url, umbral):
        raise TimeoutError("simulated")
    monkeypatch.setattr(G, "desde_micelio", _explota)
    monkeypatch.setattr(sys, "argv", [
        "gen_archivo_iskvw.py", "--fuente", "micelio",
        "--salida", str(tmp_path / "archivo.json"),
    ])
    assert G.main() == 1
    assert not (tmp_path / "archivo.json").exists()


def test_fuente_micelio_snapshot_explicita_lee_solo_el_snapshot(
        tmp_path, monkeypatch):
    """--fuente micelio_snapshot isolates main()'s branch: confirms THAT
    branch calls desde_micelio_snapshot() and nothing else. (The real
    file -> piezas/vinculos read is already covered by the tests above,
    which pass an explicit `ruta` -- the argument's default binds at
    definition time, so patching the module constant afterward would
    never reach it.)"""
    def _snapshot_falso():
        return {
            "piezas": [{"id": "solo-snapshot", "titulo": "", "clase": "obra",
                       "fecha": None, "resumen": None, "etiquetas": [],
                       "peso": 1, "medio": {"tipo": "texto"},
                       "estado": "publicada", "extra": {}}],
            "vinculos": [],
        }
    monkeypatch.setattr(G, "desde_micelio_snapshot", _snapshot_falso)
    salida = tmp_path / "archivo.json"
    monkeypatch.setattr(sys, "argv", [
        "gen_archivo_iskvw.py", "--fuente", "micelio_snapshot",
        "--salida", str(salida), "--posiciones", str(tmp_path / "sin-campo.json"),
    ])
    assert G.main() == 0
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert [p["id"] for p in datos["piezas"]] == ["solo-snapshot"]


def test_todo_does_not_publish_essays_by_default(tmp_path, monkeypatch):
    """iskvw.cl is the artwork archive; research reports are an opt-in view.

    Measured 2026-08-05: --fuente todo was mixing one `informe`, sixteen
    `concepto` pieces and sixteen essay icons into the public archive. That
    made curation material appear with report shape. The essay icons remain a
    valid research guarantee lane; they just do not publish by accident."""
    monkeypatch.setattr(G, "desde_obras", lambda: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_campo_curado",
                        lambda _ruta: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_micelio",
                        lambda _url, _umbral: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_animadas",
                        lambda: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_laser_manifiesto",
                        lambda _campo: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_ensayos",
                        lambda: {"piezas": [{"id": "ensayo-rave",
                                             "clase": "informe",
                                             "titulo": "Rave"}],
                                 "vinculos": []})

    salida = tmp_path / "archivo.json"
    monkeypatch.setattr(sys, "argv", [
        "gen_archivo_iskvw.py", "--fuente", "todo", "--salida", str(salida),
        "--posiciones", str(tmp_path / "sin-campo.json"),
    ])
    assert G.main() == 0
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert datos["piezas"] == []


def test_todo_excludes_historical_research_from_public_sustrato(
        tmp_path, monkeypatch):
    monkeypatch.setattr(G, "desde_obras", lambda: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_campo_curado",
                        lambda _ruta: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_micelio",
                        lambda _url, _umbral: {
                            "piezas": [
                                {"id": "obra", "clase": "obra"},
                                {"id": "informe", "clase": "informe"},
                                {"id": "icono", "clase": "pieza_grafica"},
                            ],
                            "vinculos": [
                                {"de": "obra", "a": "informe", "clase": "semantico"},
                                {"de": "obra", "a": "obra", "clase": "semantico"},
                            ],
                        })
    monkeypatch.setattr(G, "desde_animadas", lambda: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_laser_manifiesto",
                        lambda _campo: {"piezas": [], "vinculos": []})
    salida = tmp_path / "archivo.json"
    monkeypatch.setattr(sys, "argv", [
        "gen_archivo_iskvw.py", "--fuente", "todo", "--salida", str(salida),
        "--posiciones", str(tmp_path / "sin-campo.json"),
    ])
    assert G.main() == 0
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert [p["id"] for p in datos["piezas"]] == ["obra"]
    assert all(v["de"] == "obra" and v["a"] == "obra"
               for v in datos["vinculos"])


def test_todo_can_include_essays_when_explicitly_requested(
        tmp_path, monkeypatch):
    monkeypatch.setattr(G, "desde_obras", lambda: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_campo_curado",
                        lambda _ruta: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_micelio",
                        lambda _url, _umbral: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_animadas",
                        lambda: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_laser_manifiesto",
                        lambda _campo: {"piezas": [], "vinculos": []})
    monkeypatch.setattr(G, "desde_ensayos",
                        lambda: {"piezas": [{"id": "ensayo-rave",
                                             "clase": "informe",
                                             "titulo": "Rave"}],
                                 "vinculos": []})

    salida = tmp_path / "archivo.json"
    monkeypatch.setattr(sys, "argv", [
        "gen_archivo_iskvw.py", "--fuente", "todo", "--incluir-ensayos",
        "--salida", str(salida), "--posiciones", str(tmp_path / "sin-campo.json"),
    ])
    assert G.main() == 0
    datos = json.loads(salida.read_text(encoding="utf-8"))
    assert [p["id"] for p in datos["piezas"]] == ["ensayo-rave"]
