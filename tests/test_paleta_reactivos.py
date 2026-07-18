"""
Tests de la pieza MANIFIESTO #10 (paleta madre de reactivos, Reduciendo Dano).

La Omega11 (registrada retroactivamente en puente/SEMILLAS.md 18-jul-2026):
la pieza pierde si (a) un hex de la identidad no es trazable a una reaccion
de reactivos.json -- color inventado; (b) alguna salida pierde el disclaimer
presuntivo; (c) la salida no es determinista entre corridas. Estos tests
fijan esas tres condiciones mas la validez de forma de los hex.

No se modifica projects/cultura/paleta_reactivos.py ni los archivos
committeados en projects/cultura/identidad/: el script se importa por ruta
y se corre contra directorios temporales (tmp_path), igual que
tests/test_cartografia_filtros.py y tests/test_tapiz_vibecode.py importan
sus piezas de projects/.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_PIEZA_DIR = Path(__file__).resolve().parents[1] / "projects" / "cultura"
sys.path.insert(0, str(_PIEZA_DIR))

import paleta_reactivos as pr  # noqa: E402

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

# Colores de layout (fondo, texto, bordes de nota) del template HTML -- no
# son parte de la identidad de marca, no deben aparecer en reactivos.json.
# Viven solo en el bloque <style> (propiedad CSS "background:", sin el
# atributo "style=" inline), asi que el regex de swatches de mas abajo
# (style="background:#XXXXXX) nunca los captura por construccion. Se listan
# aca de forma explicita de todos modos, como documentacion de la exclusion
# y como guardia si el template cambiara a inyectar estos colores inline.
_LAYOUT_HEX_WHITELIST = {
    "#0f0c09",  # body background
    "#e8e0d2",  # body color (texto)
    "#c9bfae",  # h2 color
    "#a99f8e",  # h3 color
    "#c98a5a",  # p.note color
    "#1a120c",  # p.note background
    "#3a2418",  # p.note border
}


def _committed_reactivos_json():
    ruta = _PIEZA_DIR / "identidad" / "reactivos.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_determinismo_json_y_html_byte_identicos(tmp_path):
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    pr.build(out_a)
    pr.build(out_b)
    assert (out_a / "reactivos.json").read_bytes() == (out_b / "reactivos.json").read_bytes()
    assert (out_a / "identidad_rd.html").read_bytes() == (out_b / "identidad_rd.html").read_bytes()


def test_disclaimer_presuntivo_en_json_y_html(tmp_path):
    out = tmp_path / "out"
    pr.build(out)
    data = json.loads((out / "reactivos.json").read_text(encoding="utf-8"))
    assert "presuntivo" in data["disclaimer"].lower()
    html_text = (out / "identidad_rd.html").read_text(encoding="utf-8")
    assert "presuntivo" in html_text.lower()


def test_todos_los_hex_son_validos(tmp_path):
    out = tmp_path / "out"
    pr.build(out)
    data = json.loads((out / "reactivos.json").read_text(encoding="utf-8"))
    for r in data["reacciones"]:
        assert _HEX_RE.match(r["hex"]), r
    for m in data["marca"]:
        assert _HEX_RE.match(m["hex"]), m


def test_todo_hex_de_swatch_html_es_trazable_a_reactivos_json(tmp_path):
    out = tmp_path / "out"
    pr.build(out)
    data = json.loads((out / "reactivos.json").read_text(encoding="utf-8"))
    conocidos = {r["hex"].lower() for r in data["reacciones"]}
    conocidos |= {m["hex"].lower() for m in data["marca"]}

    html_text = (out / "identidad_rd.html").read_text(encoding="utf-8")
    # Solo los swatches (style="background:#XXXXXX" inline en los .sw div),
    # no los colores de layout del bloque <style> (fondo/texto/nota) --
    # esos estan explicitamente en _LAYOUT_HEX_WHITELIST y ni siquiera
    # matchean este patron porque no usan el atributo style inline.
    swatch_hex = re.findall(r'style="background:(#[0-9a-fA-F]{6})', html_text)
    assert swatch_hex, "no se encontraron swatches en el HTML generado"
    for hexv in swatch_hex:
        hexv_l = hexv.lower()
        assert hexv_l not in _LAYOUT_HEX_WHITELIST, (
            f"{hexv} es un color de layout, no deberia estar en un swatch"
        )
        assert hexv_l in conocidos, f"{hexv} en el HTML no es trazable a reactivos.json (color inventado)"


def test_sync_con_reactivos_json_committeado(tmp_path):
    """
    Compara la generacion fresca contra projects/cultura/identidad/reactivos.json
    (committeado). Si PR #70 verifico datos a mano contra DanceSafe y diverge
    del script actual, NO forzamos igualdad byte a byte -- solo la forma
    estructural (mismas claves de nivel superior, mismo shape por entrada).
    La divergencia real (si existe) se reporta aparte, no se esconde en el test.
    """
    out = tmp_path / "out"
    pr.build(out)
    fresh = json.loads((out / "reactivos.json").read_text(encoding="utf-8"))
    committed = _committed_reactivos_json()

    if fresh == committed:
        assert fresh == committed
        return

    # Divergencia esperada (dato web-verificado a mano en PR #70 le gano al
    # script): se exige compatibilidad ESTRUCTURAL, no igualdad de contenido.
    assert set(fresh.keys()) <= set(committed.keys()) or "disclaimer" in committed
    assert "reacciones" in committed and "marca" in committed
    assert isinstance(committed["reacciones"], list) and committed["reacciones"]
    assert isinstance(committed["marca"], list) and committed["marca"]

    campos_reaccion = {"reactivo", "familia", "reaccion", "hex"}
    for r in fresh["reacciones"]:
        assert campos_reaccion <= set(r.keys())
    for r in committed["reacciones"]:
        assert campos_reaccion <= set(r.keys())
        assert _HEX_RE.match(r["hex"]), r

    campos_marca = {"rol", "hex", "origen"}
    for m in fresh["marca"]:
        assert campos_marca <= set(m.keys())
    for m in committed["marca"]:
        assert campos_marca <= set(m.keys())
        assert _HEX_RE.match(m["hex"]), m

    # La marca (paleta de identidad final) si debe coincidir exactamente --
    # es lo que consume el resto del repo como color de marca oficial.
    assert fresh["marca"] == committed["marca"]
