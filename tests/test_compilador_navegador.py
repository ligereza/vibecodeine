#!/usr/bin/env python3
"""tests/test_compilador_navegador.py -- mide la equivalencia entre el
compilador Python del motor semantico (cultura/mak_codex/motor_semantico/
compilador.py) y su gemelo de NAVEGADOR (docs/cultura/lib/compilador.js,
sobre thi.ng/hiccup + hiccup-svg + color vendorizados, sin build step).

Esto es una MEDICION, no un smoke test: para cada spec compilable del lote
real (cultura/mak_codex/motor_semantico/lote.json) se compila con Python Y
con node, y se compara el SVG resultante NORMALIZADO -- no byte a byte,
porque el orden de atributos y el formato de floats difieren legitimamente
entre hiccup-svg y la f-string del compilador Python.

Requiere `node` en PATH; si no esta, se saltea todo el modulo (no hay Python
equivalente para correr JS ESM sin él, y no vamos a instalar un runtime en
CI solo para esta comparacion).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
RAIZ = TEST_DIR.parent
MAK_CODEX = RAIZ / "cultura" / "mak_codex"
LIB_JS = RAIZ / "docs" / "cultura" / "lib"
LOTE_JSON = MAK_CODEX / "motor_semantico" / "lote.json"
VOCAB_JSON = LIB_JS / "vocabulario.json"

NODE = shutil.which("node")
requiere_node = pytest.mark.skipif(NODE is None, reason="node no esta en PATH")

# se usa solo para resolver ritmo->segundos al calcular el data-ritmo
# ESPERADO desde el spec (el mismo dato que ya viaja en vocabulario.json,
# generado del Python real -- no una segunda tabla a mano).
_VOCAB = json.loads(VOCAB_JSON.read_text(encoding="utf-8"))

if str(MAK_CODEX) not in sys.path:
    sys.path.insert(0, str(MAK_CODEX))


def _cargar_lote():
    return json.loads(LOTE_JSON.read_text(encoding="utf-8"))


def _svg_a_uri(path: Path) -> str:
    # file:// URI con forward slashes -- Windows necesita el 3er slash antes
    # de la letra de unidad (file:///C:/...), si no node no resuelve el import.
    return path.resolve().as_posix()


_DRIVER_JS = """
import {{ compilar, ErrorSemantico }} from "file:///{compilador_uri}";

const vocab = JSON.parse(await (await import("node:fs/promises")).readFile("{vocab_path}", "utf8"));
const spec = JSON.parse(await (await import("node:fs/promises")).readFile("{spec_path}", "utf8"));

try {{
  const {{ svg, avisos }} = compilar(spec, vocab, spec.slug || "icono");
  process.stdout.write(JSON.stringify({{ ok: true, svg, avisos }}));
}} catch (e) {{
  if (e instanceof ErrorSemantico) {{
    process.stdout.write(JSON.stringify({{ ok: false, rechazado: true, mensaje: e.message }}));
  }} else {{
    process.stdout.write(JSON.stringify({{ ok: false, rechazado: false, mensaje: String(e.stack || e) }}));
  }}
}}
"""


def _compilar_js(tmp_path: Path, spec: dict):
    """Corre compilador.js en node para UN spec, via un driver descartable en
    tmp_path (no se puede pasar el spec como argv sin pelear con quoting de
    PowerShell/cmd, un archivo JSON es la via limpia)."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    driver = tmp_path / "driver.mjs"
    driver.write_text(
        _DRIVER_JS.format(
            compilador_uri=_svg_a_uri(LIB_JS / "compilador.js"),
            vocab_path=_svg_a_uri(VOCAB_JSON),
            spec_path=_svg_a_uri(spec_path),
        ),
        encoding="utf-8",
    )
    r = subprocess.run([NODE, str(driver)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"node fallo: stdout={r.stdout!r} stderr={r.stderr!r}"
    return json.loads(r.stdout)


# -- normalizacion para comparar los dos SVG -------------------------------
NS = "{http://www.w3.org/2000/svg}"


def _tag(el):
    return el.tag.replace(NS, "")


def _recolectar(svg_text: str):
    """Parsea el SVG y extrae la forma comparable: secuencia de tags, fills
    en orden, cantidad de <g>, transforms en orden, y el set de
    @keyframes/clases animadas del <style>."""
    root = ET.fromstring(svg_text)
    tags = [_tag(el) for el in root.iter()]
    fills = [el.get("fill") for el in root.iter() if el.get("fill") is not None]
    grupos = sum(1 for el in root.iter() if _tag(el) == "g")
    transforms = [el.get("transform") for el in root.iter() if el.get("transform") is not None]
    style_el = root.find(f"{NS}style")
    css = style_el.text or "" if style_el is not None else ""
    keyframes = set(__import__("re").findall(r"@keyframes\s+([\w-]+)", css))
    clases = set(__import__("re").findall(r"\.([\w-]+)\{animation", css))
    view_box = root.get("viewBox")
    # capas doublecup: cada grupo `capa-{i}-{rol}` tiene que poder responder
    # por su propio dato -- rol, gesto, ritmo, figura -- via atributos
    # data-*, mas un <title> no vacio (el nombre que ve Illustrator/Inkscape).
    capas = {}
    for el in root.iter():
        if _tag(el) != "g":
            continue
        gid = el.get("id")
        if not gid or not gid.startswith("capa-"):
            continue
        titulo_el = el.find(f"{NS}title")
        capas[gid] = {
            "data-rol": el.get("data-rol"),
            "data-gesto": el.get("data-gesto"),
            "data-ritmo": el.get("data-ritmo"),
            "data-figura": el.get("data-figura"),
            "titulo": (titulo_el.text if titulo_el is not None else None),
        }
    return {
        "tags": tags,
        "fills": fills,
        "grupos": grupos,
        "transforms": transforms,
        "keyframes": keyframes,
        "clases": clases,
        "view_box": view_box,
        "capas": capas,
    }


@requiere_node
@pytest.mark.parametrize("spec", _cargar_lote(), ids=lambda s: s["slug"])
def test_equivalencia_python_navegador(spec, tmp_path):
    from motor_semantico import ErrorSemantico as ErrorSemanticoPy
    from motor_semantico import compilar as compilar_py

    slug = spec["slug"]
    es_el_rechazado = slug == "10-inclusividad"  # a la spec 10 le falta 'protagonista' a proposito

    # -- lado Python --------------------------------------------------------
    rechazado_py = False
    svg_py = None
    try:
        svg_py, _avisos_py = compilar_py(spec, slug)
    except ErrorSemanticoPy:
        rechazado_py = True

    # -- lado navegador -------------------------------------------------------
    resultado_js = _compilar_js(tmp_path, spec)
    rechazado_js = not resultado_js["ok"] and resultado_js.get("rechazado")

    if es_el_rechazado:
        # INVARIANTE: ambos lados rechazan la misma spec por la misma razon
        # semantica (protagonista faltante). No comparamos SVG porque no hay.
        assert rechazado_py, "Python debia rechazar 10-inclusividad (falta protagonista)"
        assert rechazado_js, f"JS debia rechazar 10-inclusividad, respondio: {resultado_js}"
        assert "protagonista" in resultado_js["mensaje"]
        return

    assert not rechazado_py, f"Python rechazo una spec que debia compilar: {slug}"
    assert resultado_js["ok"], f"node rechazo/fallo una spec que debia compilar: {resultado_js}"
    svg_js = resultado_js["svg"]

    # ambos deben ser XML bien formado y cargar el viewBox fijo (INVARIANTE 1)
    forma_py = _recolectar(svg_py)
    forma_js = _recolectar(svg_js)
    assert forma_py["view_box"] == "0 0 120 120"
    assert forma_js["view_box"] == "0 0 120 120"

    # misma secuencia de tags -- misma forma de arbol, aunque un lado la
    # arme con hiccup-svg y el otro con f-strings
    assert forma_py["tags"] == forma_js["tags"], (
        f"secuencia de tags distinta en {slug}:\n py={forma_py['tags']}\n js={forma_js['tags']}"
    )
    # mismos fill en el mismo orden (colores resueltos identicos)
    assert forma_py["fills"] == forma_js["fills"], f"fills distintos en {slug}"
    # misma cantidad de agrupadores <g>
    assert forma_py["grupos"] == forma_js["grupos"], f"cantidad de <g> distinta en {slug}"
    # mismos transforms, mismo orden (translate/scale con enteros identicos:
    # ni Python ni el compilador JS pasan cx/cy/esc por un formateador de
    # punto flotante, los toman tal cual vienen del vocabulario)
    assert forma_py["transforms"] == forma_js["transforms"], (
        f"transforms distintos en {slug}:\n py={forma_py['transforms']}\n js={forma_js['transforms']}"
    )
    # mismo set de @keyframes declarados y mismas clases animadas
    assert forma_py["keyframes"] == forma_js["keyframes"], f"@keyframes distintos en {slug}"
    assert forma_py["clases"] == forma_js["clases"], f"clases animadas distintas en {slug}"

    # -- doublecup: cada capa declara lo que codifica (orden 2026-07-30) ----
    # cada capa del spec produce EXACTAMENTE un grupo con id="capa-{i}-{rol}",
    # mismo conjunto de ids en los dos lados.
    ids_esperados = {f"capa-{i}-{c['rol']}" for i, c in enumerate(spec["capas"])}
    assert set(forma_py["capas"]) == ids_esperados, (
        f"ids de capa (Python) no coinciden con el spec en {slug}: {sorted(forma_py['capas'])}"
    )
    assert set(forma_js["capas"]) == ids_esperados, (
        f"ids de capa (JS) no coinciden con el spec en {slug}: {sorted(forma_js['capas'])}"
    )

    ritmos = _VOCAB["ritmos"]
    for i, capa in enumerate(spec["capas"]):
        gid = f"capa-{i}-{capa['rol']}"
        gesto_esperado = capa.get("gesto", "quieto")
        ritmo_esperado = ritmos[capa.get("ritmo", "medio")]
        figura_esperada = capa["figura"] if capa.get("figura") else "texto"
        for lado, forma in (("python", forma_py), ("js", forma_js)):
            datos = forma["capas"][gid]
            # un elemento que no puede responder por su propio dato es el
            # defecto que esta asercion existe para impedir: rol, gesto,
            # ritmo (RESUELTO, no la palabra del vocabulario) y figura
            # tienen que coincidir con lo que dice el spec.
            assert datos["data-rol"] == capa["rol"], f"{lado}/{slug}/{gid}: data-rol"
            assert datos["data-gesto"] == gesto_esperado, f"{lado}/{slug}/{gid}: data-gesto"
            assert datos["data-ritmo"] == ritmo_esperado, f"{lado}/{slug}/{gid}: data-ritmo"
            assert datos["data-figura"] == figura_esperada, f"{lado}/{slug}/{gid}: data-figura"
            # cada grupo capa-* tiene un <title> no vacio (Illustrator/Inkscape
            # muestran la capa con nombre; el icono queda editable y reintegrable)
            assert datos["titulo"], f"{lado}/{slug}/{gid}: <title> vacio o ausente"


@requiere_node
def test_vocabulario_json_sincronizado():
    """El JSON que el navegador consume tiene que venir del Python real, no
    de una copia a mano -- tools/gen_vocabulario_motor.py --verificar es el
    chequeo que ya existe para eso. Lo corremos aca como subprocess porque
    es la MISMA garantia que necesita este archivo: si el vocabulario del
    navegador queda desactualizado, esta comparacion entera deja de servir
    para nada."""
    r = subprocess.run(
        [sys.executable, "tools/gen_vocabulario_motor.py", "--verificar"],
        cwd=RAIZ, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"vocabulario.json desincronizado:\n{r.stdout}\n{r.stderr}"
