#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_iconos_conjunto.py -- tools/iconos_conjunto.py: validador y
generador de galeria para un CONJUNTO de iconos (docs/cultura/ensayos/<tema>/).

El caso real es docs/cultura/ensayos/rave: 16 iconos escritos a mano, medido
en 0 errores / 0 avisos (2026-07-30). El validador atrapa 7 clases de error
sobre archivos editados a mano; la mas importante es var(--x) usada y no
declarada, porque fue la que atrapo el bug del propio autor del validador
(una refactorizacion convirtio "3.4s" en "3.var(--vel)").
"""
import shutil
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import iconos_conjunto as IC  # noqa: E402

RAVE = REPO / "docs" / "cultura" / "ensayos" / "rave"
ICONO_REAL = RAVE / "iconos" / "07-berlin-muro-techno.svg"


# ---------------------------------------------------------------------------
# validar: el conjunto real
# ---------------------------------------------------------------------------
def test_los_16_iconos_reales_no_tienen_errores():
    archivos = sorted((RAVE / "iconos").glob("*.svg"))
    assert len(archivos) == 16
    total_errores = 0
    for f in archivos:
        errores, _avisos = IC.revisar(f)
        total_errores += len(errores)
        assert errores == [], (f.name, errores)
    assert total_errores == 0


def test_mutacion_rompiendo_un_icono_real_lo_detectaria(tmp_path):
    """Verificacion viva de la asercion anterior: si un icono real se
    rompiera (le falta el viewBox), revisar() debe dejar de devolver []."""
    roto = tmp_path / "roto.svg"
    txt = ICONO_REAL.read_text(encoding="utf-8")
    roto.write_text(txt.replace('viewBox="0 0 120 120"', ""), encoding="utf-8")
    errores, _ = IC.revisar(roto)
    assert errores, "la mutacion no se detecto: el guard no prueba nada"
    assert any("viewBox" in e for e in errores)


# ---------------------------------------------------------------------------
# validar: las 7 clases de error, inyectadas sobre una copia de un icono real
# ---------------------------------------------------------------------------
def _copia_mutada(tmp_path, transformar):
    txt = ICONO_REAL.read_text(encoding="utf-8")
    mutado = transformar(txt)
    destino = tmp_path / "mutado.svg"
    destino.write_text(mutado, encoding="utf-8")
    return destino


def test_var_usada_sin_declarar(tmp_path):
    # la refactorizacion real que motivo esta clase: se borra la declaracion
    # de --vel-muro pero el CSS la sigue usando via var(--vel-muro)
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace("--vel-muro: 5s;\n", ""))
    errores, _ = IC.revisar(ruta)
    assert any("var(--vel-muro)" in e and "NO declarada" in e for e in errores)


def test_xml_mal_formado(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace('<rect width="120" height="120"',
                                      '<rect width="120 height="120"'))
    errores, _ = IC.revisar(ruta)
    assert any("XML mal formado" in e for e in errores)


def test_viewbox_faltante(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace('viewBox="0 0 120 120" ', ""))
    errores, _ = IC.revisar(ruta)
    assert any("falta viewBox" in e for e in errores)


def test_animation_apunta_a_keyframes_inexistente(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace("animation:i7l var(--vel-muro)",
                                      "animation:i7l_fantasma var(--vel-muro)"))
    errores, _ = IC.revisar(ruta)
    assert any("i7l_fantasma" in e and "no existe @keyframes" in e for e in errores)


def test_id_duplicado(tmp_path):
    ruta = _copia_mutada(
        tmp_path, lambda t: t.replace(
            '<rect width="120" height="120" fill="var(--fondo)"/>',
            '<rect id="dup" width="120" height="120" fill="var(--fondo)"/>'
            '<circle id="dup" r="1"/>'))
    errores, _ = IC.revisar(ruta)
    assert any('id="dup" duplicado' in e for e in errores)


def test_url_colgante(tmp_path):
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
    """Copia el conjunto real rave a tmp_path/docs/cultura/ensayos/rave, para
    que la resolucion de ruta relativa hacia docs/cultura/lib (que se calcula
    contra RAIZ_REPO) siga funcionando bajo un RAIZ_REPO parcheado a tmp_path."""
    destino = tmp_path / "docs" / "cultura" / "ensayos" / "rave"
    shutil.copytree(RAVE, destino)
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
    assert "Berlín: cae el muro, sale el techno" in html
    assert "Berlin: cae el muro" not in html


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


# --------------------------------------------------------------------------
# La animacion: coherencia entre lo que el archivo declara y lo que hace
# --------------------------------------------------------------------------
import re as _re

sys.path.insert(0, str(REPO / "cultura" / "mak_codex"))
from motor_semantico import rasterizador as _ras  # noqa: E402

# El guarda pregunta por la capacidad EXACTA que este test usa, no por una
# parecida. Preguntaba `backend_disponible()` a secas y en ubuntu la respuesta
# era cairosvg, que rasteriza y no ejecuta una sola animacion CSS: los 16
# iconos salieron acusados de estar quietos con la matriz de CI en rojo. Lo que
# estaba muerto era el instrumento.
_requiere_backend = pytest.mark.skipif(
    _ras.backend_disponible(anima=True) is None,
    reason="sin backend que ejecute animaciones CSS (hace falta un navegador)")


def _ciclo_ms(svg: str) -> int:
    """El ciclo mas largo que el propio archivo declara, en ms.

    Muestrear una ventana fija seria injusto con un icono de ciclo lento: no se
    moveria dentro de la ventana y el test lo llamaria muerto sin que lo este.
    Se le pregunta al archivo cuanto dura su animacion mas larga.
    """
    duraciones = [float(x) * (1000 if u == "s" else 1)
                  for x, u in _re.findall(r"animation:[^;}]*?([\d.]+)(m?s)", svg)]
    return int(max(duraciones)) if duraciones else 0


def _diagnostico(svg: str, ciclo: int) -> str:
    """Que backend midio, y que devolvio. Se arma solo cuando algo falla."""
    b = _ras.backend_disponible(anima=True)
    partes = ["backend=%s (rasteriza: %s)" % (b, _ras.backend_disponible())]
    try:
        a = _ras.rasterizar(svg, tam=96, backend=b, anima=True)
        z = _ras.rasterizar(svg, tam=96, avance_ms=ciclo // 2, backend=b,
                            anima=True)
        partes.append("PNG cuadro0=%d B, medio ciclo=%d B, %s"
                      % (len(a), len(z),
                         "IGUALES" if a == z else "distintos"))
        sq = _ras.rasterizar(_ras._SONDA_ANIMA, tam=_ras._TAM_SONDA,
                             backend=b, anima=True)
        sm = _ras.rasterizar(_ras._SONDA_ANIMA, tam=_ras._TAM_SONDA,
                             avance_ms=500, backend=b, anima=True)
        partes.append("sonda %dpx: %d/%d B, %s; perfil=%s"
                      % (_ras._TAM_SONDA, len(sq), len(sm),
                         "IGUALES" if sq == sm else "distintos",
                         _ras._perfil_navegador()))
    except Exception as e:  # el diagnostico no puede tapar el fallo real
        partes.append("diagnostico incompleto: %r" % (e,))
    return "; ".join(partes)


@_requiere_backend
@pytest.mark.parametrize("svg_path", sorted((RAVE / "iconos").glob("*.svg")),
                         ids=lambda p: p.stem)
def test_un_icono_que_declara_animacion_se_mueve_en_su_propio_ciclo(svg_path):
    """La regla es de COHERENCIA, no un umbral: si el archivo declara
    `@keyframes`, muestrear su propio ciclo tiene que dar cuadros distintos. Un
    icono que dice animarse y no cambia nada le miente al lector -- y es la
    clase de defecto que ningun chequeo estatico ve, porque el XML es valido.

    Un icono SIN keyframes no entra: no declara nada, no debe nada.
    """
    svg = IC.resolver_vars(svg_path.read_text(encoding="utf-8"))
    if "@keyframes" not in svg:
        pytest.skip("no declara animacion")
    ciclo = _ciclo_ms(svg)
    assert ciclo > 0, "declara @keyframes y ninguna duracion: nada lo dispara"

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _, cuadros, distintos = _ras.animar(
                svg, Path(tmp) / "x.gif", cuadros=4,
                ciclo_ms=ciclo, tam=96)
        except _ras.BackendNoDibujaError as e:
            # Se dice en voz alta y se sigue: un instrumento que no dibuja la
            # pieza no tiene nada que declarar SOBRE la pieza. Acusarla seria
            # exactamente el error que costo tres matrices rojas.
            pytest.skip("instrumento incapaz, no defecto del archivo: %s" % e)
    # El mensaje NOMBRA al instrumento. Sin eso, una acusacion al archivo y un
    # instrumento ciego se leen igual, y esta suite ya gasto dos vueltas de CI
    # aprendiendo la diferencia.
    assert distintos > 1, (
        "declara animacion de %d ms y los %d cuadros de su propio ciclo son "
        "identicos: o el archivo afirma un movimiento que no ocurre, o el "
        "instrumento no lo ve. %s" % (ciclo, cuadros, _diagnostico(svg, ciclo)))
