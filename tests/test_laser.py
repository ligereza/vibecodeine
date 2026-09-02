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
    for cmd in ("estado", "hatched", "flow", "lote", "medir", "ild"):
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


# ---------------------------------------------------------------------------
# Geometry layer: pen-up travel measured, not claimed
# ---------------------------------------------------------------------------

def _svg(tmp_path, cuerpo, nombre="g.svg"):
    p = tmp_path / nombre
    p.write_text('<svg xmlns="http://www.w3.org/2000/svg">%s</svg>' % cuerpo,
                 encoding="utf-8")
    return p


def test_polilineas_lee_line_polyline_polygon_y_path(tmp_path):
    svg = _svg(tmp_path,
               '<line x1="0" y1="0" x2="3" y2="4"/>'
               '<polyline points="0,0 1,0 1,1"/>'
               '<polygon points="0,0 2,0 2,2"/>'
               '<path d="M 0 0 L 1 0 l 1 0 H 5 v 2 Z m 1 1 2 2"/>')
    polys = laser.polilineas(svg)
    # line=1, polyline=1, polygon=1 (closed), path: Z closes one subpath,
    # then the implicit-lineto after m opens another
    assert len(polys) == 5
    assert polys[0] == [(0.0, 0.0), (3.0, 4.0)]
    assert polys[2][-1] == polys[2][0]  # polygon closes itself
    # H/V/relative and Z-closure resolved to absolute coordinates
    assert polys[3] == [(0, 0), (1, 0), (2, 0), (5, 0), (5, 2), (0, 0)]
    assert polys[4] == [(1.0, 1.0), (3.0, 3.0)]


def test_polilineas_aplica_transformaciones_anidadas(tmp_path):
    svg = _svg(tmp_path,
               '<g transform="translate(10,0) scale(2)">'
               '<line x1="1" y1="1" x2="2" y2="1"/></g>')
    (a, b), (c, d) = laser.polilineas(svg)[0]
    assert (a, b) == (12.0, 2.0) and (c, d) == (14.0, 2.0)


def test_polilineas_rechaza_curvas_y_figuras_con_instruccion(tmp_path):
    con_curva = _svg(tmp_path, '<path d="M 0 0 C 1 1 2 2 3 3"/>', "c.svg")
    with pytest.raises(RuntimeError, match="vpype"):
        laser.polilineas(con_curva)
    con_rect = _svg(tmp_path, '<rect x="0" y="0" width="5" height="5"/>',
                    "r.svg")
    with pytest.raises(RuntimeError, match="vpype"):
        laser.polilineas(con_rect)


def test_medir_reporta_viaje_apagado(tmp_path):
    # two strokes with a 10-unit blank jump between end (5,0) and start (15,0)
    svg = _svg(tmp_path, '<polyline points="0,0 5,0"/>'
                         '<polyline points="15,0 20,0"/>')
    m = laser.medir(svg)
    assert m == {"puntos": 4, "trazos": 2, "dibujo": 10.0,
                 "viaje_apagado": 10.0}


def test_medir_demuestra_el_beneficio_de_ordenar(tmp_path):
    # same three strokes, pathological vs sorted order: the number moves
    desordenado = _svg(tmp_path, '<polyline points="0,0 1,0"/>'
                                 '<polyline points="100,0 101,0"/>'
                                 '<polyline points="2,0 3,0"/>', "malo.svg")
    ordenado = _svg(tmp_path, '<polyline points="0,0 1,0"/>'
                              '<polyline points="2,0 3,0"/>'
                              '<polyline points="100,0 101,0"/>', "bueno.svg")
    antes = laser.medir(desordenado)["viaje_apagado"]
    despues = laser.medir(ordenado)["viaje_apagado"]
    assert antes == 198.0 and despues == 98.0  # less than half, measured


def test_generar_mide_viaje_antes_y_despues(monkeypatch, tmp_path):
    """With medir_viaje the pipeline runs generator -> measure -> sort ->
    measure and reports both numbers; the fake sort actually reorders."""
    salida = tmp_path / "x.svg"
    malo = ('<svg xmlns="http://www.w3.org/2000/svg">'
            '<polyline points="0,0 1,0"/><polyline points="100,0 101,0"/>'
            '<polyline points="2,0 3,0"/></svg>')
    bueno = ('<svg xmlns="http://www.w3.org/2000/svg">'
             '<polyline points="0,0 1,0"/><polyline points="2,0 3,0"/>'
             '<polyline points="100,0 101,0"/></svg>')

    def falso_correr(args):
        salida.write_text(bueno if "linesort" in args else malo,
                          encoding="utf-8")
    monkeypatch.setattr(laser, "_correr", falso_correr)
    medida = laser.hatched(tmp_path / "img.png", salida, medir_viaje=True)
    assert medida["viaje_apagado_antes"] == 198.0
    assert medida["viaje_apagado_despues"] == 98.0
    assert medida["viaje_apagado"] == 98.0  # final svg, measured again
    assert medida["dentro"] is True


# ---------------------------------------------------------------------------
# ILDA format 5: the file QuickShow actually imports
# ---------------------------------------------------------------------------

def test_ild_ida_y_vuelta_formato_5(tmp_path):
    svg = _svg(tmp_path, '<polyline points="0,0 10,0 10,10"/>'
                         '<polyline points="0,10 0,5"/>')
    ild = tmp_path / "x.ild"
    r = laser.escribir_ild(svg, ild, color=(255, 0, 128), reposo=2)
    # 2 strokes: (2+3+2) + (2+2+2) = 13 records, 8 of them blanked dwell
    assert r == {"puntos_ild": 13, "en_blanco": 8, "trazos": 2}
    frames = laser.leer_ild(ild)
    assert len(frames) == 1
    f = frames[0]
    assert f["formato"] == 5 and f["total"] == 1
    pts = f["puntos"]
    assert len(pts) == 13
    assert pts[0]["apagado"] is True          # dwell before the beam opens
    assert pts[2]["apagado"] is False
    assert pts[2]["rgb"] == (255, 0, 128)      # lit points carry the color
    assert pts[0]["rgb"] == (0, 0, 0)          # blanked points carry none
    assert pts[-1]["ultimo"] is True           # bit 7 on the very last point
    assert all(p["ultimo"] is False for p in pts[:-1])


def test_ild_bytes_cabecera_y_orden_bgr(tmp_path):
    """Byte-level: 'ILDA' magic, format code 5 at offset 7, true-color
    records ordered Blue,Green,Red (the spec reverses the palette order --
    getting this wrong swaps red and blue on the projector)."""
    svg = _svg(tmp_path, '<polyline points="0,0 10,0"/>')
    ild = tmp_path / "x.ild"
    laser.escribir_ild(svg, ild, color=(255, 10, 20), reposo=0)
    datos = ild.read_bytes()
    assert datos[:4] == b"ILDA" and datos[7] == 5
    primero = datos[32:40]  # first 8-byte record
    assert primero[5:8] == bytes([20, 10, 255])  # B, G, R
    # closes with an EOF header of 0 records
    assert datos[-32:-28] == b"ILDA" and datos[-8:-6] == b"\x00\x00"


def test_ild_encaja_y_voltea_y(tmp_path):
    # SVG y grows DOWN, ILDA y grows UP: the top of the drawing must land
    # on positive Y or every piece projects upside down
    svg = _svg(tmp_path, '<polyline points="0,0 10,10"/>')
    ild = tmp_path / "x.ild"
    laser.escribir_ild(svg, ild, reposo=0)
    pts = laser.leer_ild(ild)[0]["puntos"]
    assert (pts[0]["x"], pts[0]["y"]) == (-32000, 32000)   # svg top-left
    assert (pts[1]["x"], pts[1]["y"]) == (32000, -32000)   # svg bottom-right


def test_ild_es_determinista(tmp_path):
    svg = _svg(tmp_path, '<polyline points="0,0 5,5 10,0"/>')
    a, b = tmp_path / "a.ild", tmp_path / "b.ild"
    laser.escribir_ild(svg, a, nombre="pieza")
    laser.escribir_ild(svg, b, nombre="pieza")
    assert a.read_bytes() == b.read_bytes()


def test_ild_svg_vacio_falla_con_mensaje(tmp_path):
    svg = _svg(tmp_path, "")
    with pytest.raises(RuntimeError, match="sin trazos"):
        laser.escribir_ild(svg, tmp_path / "x.ild")


def test_lote_con_ild_extiende_el_manifiesto(monkeypatch, tmp_path):
    """lote --ild: manifest rows gain ild/puntos_ild plus the measured
    trazos/viaje_apagado; without the flag the schema stays additive."""
    (tmp_path / "111.jpg").write_bytes(b"\xff")
    (tmp_path / "222.jpg").write_bytes(b"\xff")

    def falso_flow(imagen, salida, semilla=7, **kw):
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<polyline points="0,0 5,0"/><polyline points="15,0 20,0"/>'
            '</svg>', encoding="utf-8")
        return {"puntos": 4, "tolerancia_mm": None, "dentro": True,
                "trazos": 2, "viaje_apagado": 10.0}
    monkeypatch.setattr(laser, "flow", falso_flow)
    manif = tmp_path / "laser.json"
    filas = laser.lote(tmp_path, tmp_path / "out", manif, modo="flow",
                       ild=True)
    assert len(filas) == 2
    for fila in filas:
        assert fila["ild"].endswith(fila["stem"] + ".ild")
        assert fila["puntos_ild"] == 4 + 4 * 4  # 4 lit + 2*4 dwell per stroke
        assert fila["trazos"] == 2 and fila["viaje_apagado"] == 10.0
    guardado = json.loads(manif.read_text(encoding="utf-8"))
    assert guardado["piezas"][0]["ild"].endswith("111.ild")
    # the archive contract still reads these rows (additive schema)
    r = contrato_archivo.desde_laser(guardado, {"piezas": []},
                                     existe=lambda s: True)
    assert len(r["piezas"]) == 2
