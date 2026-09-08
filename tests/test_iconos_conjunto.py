#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the generic SVG set validator and gallery builder.

    Curated visual reports remain references, not CI dependencies.
"""
import json
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import iconos_conjunto as IC  # noqa: E402

ICONO_FIXTURE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
<style>
:root{--fondo:#08080b;--vel-muro: 5s;}
.muro{animation:i7l var(--vel-muro) infinite;}
@keyframes i7l{from{opacity:1}to{opacity:.5}}
</style>
<rect width="120" height="120" fill="var(--fondo)"/>
<rect id="muro" class="muro" width="120" height="120" fill="#fff"/>
</svg>"""


# ---------------------------------------------------------------------------
# validar: generic SVG fixture
# ---------------------------------------------------------------------------
def test_validator_accepts_a_synthetic_animated_svg(tmp_path):
    ruta = tmp_path / "icon.svg"
    ruta.write_text(ICONO_FIXTURE, encoding="utf-8")
    errores, _avisos = IC.revisar(ruta)
    assert errores == []


def test_mutation_removing_viewbox_is_detected(tmp_path):
    """Verificacion viva de la asercion anterior: si un icono real se
    rompiera (le falta el viewBox), revisar() debe dejar de devolver []."""
    roto = tmp_path / "roto.svg"
    txt = ICONO_FIXTURE
    roto.write_text(txt.replace('viewBox="0 0 120 120"', ""), encoding="utf-8")
    errores, _ = IC.revisar(roto)
    assert errores, "la mutacion no se detecto: el guard no prueba nada"
    assert any("viewBox" in e for e in errores)


# ---------------------------------------------------------------------------
# validar: las 7 clases de error, inyectadas sobre una copia de un icono real
# ---------------------------------------------------------------------------
def _copia_mutada(tmp_path, transformar):
    txt = ICONO_FIXTURE
    mutado = transformar(txt)
    destino = tmp_path / "mutado.svg"
    destino.write_text(mutado, encoding="utf-8")
    return destino


def test_undeclared_variable_is_detected(tmp_path):
    # la refactorizacion real que motivo esta clase: se borra la declaracion
    # de --vel-muro pero el CSS la sigue usando via var(--vel-muro)
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace("--vel-muro: 5s;", ""))
    errores, _ = IC.revisar(ruta)
    assert any("var(--vel-muro)" in e and "NO declarada" in e for e in errores)


def test_malformed_xml_is_detected(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace('<rect width="120" height="120"',
                                      '<rect width="120 height="120"'))
    errores, _ = IC.revisar(ruta)
    assert any("XML mal formado" in e for e in errores)


def test_missing_viewbox_is_detected(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace('viewBox="0 0 120 120"', ""))
    errores, _ = IC.revisar(ruta)
    assert any("falta viewBox" in e for e in errores)


def test_missing_keyframes_is_detected(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace("animation:i7l var(--vel-muro)",
                                      "animation:i7l_fantasma var(--vel-muro)"))
    errores, _ = IC.revisar(ruta)
    assert any("i7l_fantasma" in e and "no existe @keyframes" in e for e in errores)


def test_duplicate_id_is_detected(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace(
            '<rect width="120" height="120" fill="var(--fondo)"/>',
            '<rect id="dup" width="120" height="120" fill="var(--fondo)"/>'
            '<circle id="dup" r="1"/>'))
    errores, _ = IC.revisar(ruta)
    assert any('id="dup" duplicado' in e for e in errores)


def test_dangling_url_is_detected(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace(
            '<rect width="120" height="120" fill="var(--fondo)"/>',
            '<rect width="120" height="120" fill="url(#fantasma)"/>'))
    errores, _ = IC.revisar(ruta)
    assert any("url(#fantasma)" in e and "inexistente" in e for e in errores)


# ---------------------------------------------------------------------------
# construir: determinismo, titulos con diacriticos, ruta relativa a lib
# ---------------------------------------------------------------------------
def _clonar_conjunto(tmp_path):
    """Build a minimal generic set under the expected directory shape."""
    destino = tmp_path / "docs" / "cultura" / "ensayos" / "demo"
    (destino / "iconos").mkdir(parents=True)
    (destino / "iconos" / "demo.svg").write_text(
        ICONO_FIXTURE, encoding="utf-8")
    (destino / "iconos.json").write_text(json.dumps([{
        "n": "01", "archivo": "demo.svg", "slug": "demo",
        "titulo": "Berlín: synthetic fixture", "descripcion": "fixture",
        "estilo": "test",
    }], ensure_ascii=False), encoding="utf-8")
    (tmp_path / "docs" / "cultura" / "lib").mkdir(parents=True, exist_ok=True)
    return destino


def test_construir_es_deterministico_y_completo(tmp_path, monkeypatch):
    raiz = _clonar_conjunto(tmp_path)
    monkeypatch.setattr(IC, "RAIZ_REPO", tmp_path)
    args = types.SimpleNamespace(titulo=None)

    manifiesto = __import__("json").loads(
        (raiz / "iconos.json").read_text(encoding="utf-8"))

    rc1 = IC.cmd_construir(raiz, args)
    html1 = (raiz / "galeria.html").read_text(encoding="utf-8")
    rc2 = IC.cmd_construir(raiz, args)
    html2 = (raiz / "galeria.html").read_text(encoding="utf-8")

    assert rc1 == 0 and rc2 == 0
    assert html1 == html2, "construir() no es deterministico"

    for item in manifiesto:
        assert item["titulo"] in html1, item["titulo"]
    assert 'id="taller"' in html1
    assert "/lib" in html1
    assert "../../lib" in html1  # rave -> ensayos -> cultura -> ../../lib


def test_construir_reporta_diacriticos_intactos_no_mangled(tmp_path, monkeypatch):
    raiz = _clonar_conjunto(tmp_path)
    monkeypatch.setattr(IC, "RAIZ_REPO", tmp_path)
    IC.cmd_construir(raiz, types.SimpleNamespace(titulo=None))
    html = (raiz / "galeria.html").read_text(encoding="utf-8")
    # un titulo real del manifiesto que lleva tilde
    assert "Berlín: synthetic fixture" in html
    assert "Berlin: synthetic fixture" not in html


def test_construir_falla_si_el_manifiesto_apunta_a_archivo_inexistente(tmp_path, monkeypatch):
    raiz = _clonar_conjunto(tmp_path)
    monkeypatch.setattr(IC, "RAIZ_REPO", tmp_path)
    manifiesto_path = raiz / "iconos.json"
    import json
    manifiesto = json.loads(manifiesto_path.read_text(encoding="utf-8"))
    manifiesto[0]["archivo"] = "no-existe.svg"
    manifiesto_path.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")

    rc = IC.cmd_construir(raiz, types.SimpleNamespace(titulo=None))
    assert rc != 0


def test_mutacion_construir_no_deterministico_se_detectaria(tmp_path, monkeypatch):
    """Verificacion viva: si construir() insertara algo variable (un
    timestamp, un id aleatorio) el test de determinismo de arriba dejaria de
    pasar. Lo probamos parcheando temporalmente el CSS del modulo para que
    incluya algo distinto en cada llamada, confirmamos el fallo, y
    restauramos EXACTO (monkeypatch ya lo hace solo, pero forzamos la
    comparacion aca mismo dentro del test para no depender de otro test)."""
    raiz = _clonar_conjunto(tmp_path)
    monkeypatch.setattr(IC, "RAIZ_REPO", tmp_path)
    css_original = IC.CSS

    monkeypatch.setattr(IC, "CSS", css_original + "/* build-1 */")
    IC.cmd_construir(raiz, types.SimpleNamespace(titulo=None))
    html1 = (raiz / "galeria.html").read_text(encoding="utf-8")
    monkeypatch.setattr(IC, "CSS", css_original + "/* build-2 */")
    IC.cmd_construir(raiz, types.SimpleNamespace(titulo=None))
    html2 = (raiz / "galeria.html").read_text(encoding="utf-8")
    assert html1 != html2, "la mutacion no vario el output, ajustar el caso"
