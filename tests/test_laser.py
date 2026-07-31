"""The laser tool: budget honesty, contract joins, CLI registration.

The user's toolkit (docs/laser/TOOLKIT_INDICE.md) fixes the hard numbers:
600-1000 points per frame at 30 kpps, and a flattened mid-size SVG carries
15-20k -- so the budget logic is the tool, not an extra. vpype itself is an
external optional dependency (same pattern as Blender/Edge): these tests pin
everything that does NOT need it, and skip the live run when it is absent.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

import contrato_archivo  # noqa: E402
from flujo import laser  # noqa: E402


def test_cli_registra_el_grupo_laser():
    # encoding explicito: el help de typer trae box-drawing UTF-8 y el
    # decoder cp1252 por defecto de Windows lo revienta a stdout=None
    proc = subprocess.run([sys.executable, "-m", "flujo", "laser", "--help"],
                          capture_output=True, text=True, timeout=120, cwd=RAIZ,
                          encoding="utf-8", errors="replace")
    assert proc.returncode == 0
    for cmd in ("estado", "hatched", "flow", "lote"):
        assert cmd in proc.stdout


def test_puntos_cuenta_vertices(tmp_path):
    svg = tmp_path / "x.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<polyline points="0,0 1,1 2,2 3,3"/>'
        '<polyline points="5,5 6,6"/></svg>', encoding="utf-8")
    assert laser.puntos(svg) == 6


def test_presupuesto_simplifica_en_orden(monkeypatch, tmp_path):
    svg = tmp_path / "x.svg"
    svg.write_text("<svg/>", encoding="utf-8")
    llamadas = []
    valores = iter([5000, 2000, 900, 700])
    monkeypatch.setattr(laser, "puntos", lambda p: next(valores))
    monkeypatch.setattr(laser, "_correr", lambda args: llamadas.append(args))
    r = laser._ajustar_al_presupuesto(svg, 800)
    assert r["dentro"] is True and r["puntos"] == 700
    # tolerancias en orden declarado, sin saltarse ninguna
    assert [a[a.index("-t") + 1] for a in llamadas] == ["0.2mm", "0.5mm", "1.0mm"]


def test_presupuesto_no_recorta_en_silencio(monkeypatch, tmp_path):
    svg = tmp_path / "x.svg"
    svg.write_text("<svg/>", encoding="utf-8")
    monkeypatch.setattr(laser, "puntos", lambda p: 3000)
    monkeypatch.setattr(laser, "_correr", lambda args: None)
    r = laser._ajustar_al_presupuesto(svg, 800)
    assert r["dentro"] is False  # lo dice, no lo esconde


def test_contrato_une_por_media_id_y_tolera_huerfanas():
    campo = {"piezas": [
        {"id": "abc-111", "archivo": "posts/111.mp4"},
        {"id": "def-222", "archivo": "posts/222.jpg"},
    ]}
    manif = {"piezas": [
        {"stem": "111", "src": "iskvw/piel/laser/111.svg", "modo": "flow"},
        {"stem": "999", "src": "iskvw/piel/laser/999.svg", "modo": "flow"},
        {"stem": "222", "src": "iskvw/piel/laser/222.svg", "modo": "hatched"},
    ]}
    r = contrato_archivo.desde_laser(manif, campo, existe=lambda s: True)
    assert len(r["piezas"]) == 3
    enlaces = {(v["de"], v["a"]) for v in r["vinculos"]}
    assert enlaces == {("laser-111", "abc-111"), ("laser-222", "def-222")}
    huerfana = next(p for p in r["piezas"] if p["id"] == "laser-999")
    assert "derivada_de" not in huerfana["extra"]


def test_contrato_excluye_svg_ausente():
    manif = {"piezas": [{"stem": "1", "src": "x/1.svg", "modo": "flow"}]}
    r = contrato_archivo.desde_laser(manif, {"piezas": []},
                                     existe=lambda s: False)
    assert r["piezas"] == [] and r["vinculos"] == []


@pytest.mark.skipif(not laser.verificar().get("vpype"),
                    reason="vpype not installed (optional external tool)")
def test_estado_reporta_la_cadena_real():
    estado = laser.verificar()
    assert estado["vpype"] is True
