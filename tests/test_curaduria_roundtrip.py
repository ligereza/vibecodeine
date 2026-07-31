# -*- coding: utf-8 -*-
"""The whole curation chain, closed in one loop.

Three parties speak curaduria.json: the panel writes it
(`iskvw/editor.html`, construirCuraduria), the validator judges it
(`tools/validar_curaduria.py`) and the consumer obeys it
(`cultura/mak_plataforma/contrato_archivo.aplicar_curaduria`, via
tools/gen_archivo_iskvw.py). Each already had its own tests; nothing pinned
that they speak the SAME dialect, and that is exactly where a silent fork
would start -- the panel exporting a shape the consumer half-reads.

Method, same as tests/test_iskvw_semilla.py: the page is static with no
build, so the real functions are EXTRACTED from editor.html and run in node
with seeded state. What node prints is fed to the Python validator and then
to the Python consumer. If any of the three drifts, this goes red.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
EDITOR = RAIZ / "iskvw" / "editor.html"
sys.path.insert(0, str(RAIZ / "tools"))
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

import contrato_archivo  # noqa: E402
import validar_curaduria as vc  # noqa: E402

requiere_node = pytest.mark.skipif(shutil.which("node") is None,
                                   reason="node no esta en el PATH")


def _extraer_funcion(nombre: str) -> str:
    """One function's body out of the real HTML, braces balanced."""
    texto = EDITOR.read_text(encoding="utf-8")
    inicio = texto.index("function %s(" % nombre)
    i = texto.index("{", inicio)
    nivel = 0
    for j in range(i, len(texto)):
        if texto[j] == "{":
            nivel += 1
        elif texto[j] == "}":
            nivel -= 1
            if nivel == 0:
                return texto[inicio:j + 1]
    raise AssertionError("no pude aislar %s()" % nombre)


def _extraer_campos() -> str:
    """The CAMPOS constant, the list of fields the panel edits."""
    m = re.search(r"const CAMPOS = \[[^\]]*\];",
                  EDITOR.read_text(encoding="utf-8"))
    assert m, "editor.html perdio la constante CAMPOS"
    return m.group(0)


def _exportar(ediciones: dict, base: dict, regimen: str) -> dict:
    """Run the panel's real construirCuraduria() in node over seeded state
    and return what the artist would download."""
    guion = """
%s
%s
const EDICIONES = new Map(Object.entries(%s));
const BASE = %s;
const REGIMEN_GLOBAL = %s;
console.log(JSON.stringify(construirCuraduria()));
""" % (_extraer_campos(), _extraer_funcion("construirCuraduria"),
       json.dumps(ediciones, ensure_ascii=False),
       json.dumps(base, ensure_ascii=False), json.dumps(regimen))
    r = subprocess.run(["node", "--input-type=module", "-e", guion],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


EDICIONES = {
    # untouched-in-substance: every value IS the default -> must not travel
    "zeta": {"titulo": "", "mostrar": True, "abstraccion": 0, "svg": "",
             "regimen": ""},
    # a real curation, diacritics and all, plus a field the panel does not
    # know (a future agent's) that must survive untouched
    "alfa": {"titulo": "Diseño y daño — el año", "abstraccion": 0.351,
             "peso": 2.5, "serie": "raíces", "nota": "Ésta abre la serie.",
             "orden_ritual": 3},
    "beta": {"mostrar": False},
}
BASE = {"_doc": "La mano del artista.", "version": 1,
        "regimen": "semantico", "piezas": {}}


def _datos():
    return {
        "piezas": [
            {"id": "alfa", "titulo": None, "clase": "obra", "extra": {}},
            {"id": "beta", "titulo": None, "clase": "obra", "extra": {}},
            {"id": "zeta", "titulo": None, "clase": "obra", "extra": {}},
        ],
        "vinculos": [{"de": "alfa", "a": "beta", "peso": 0.5,
                      "clase": "semantico"}],
    }


@requiere_node
def test_lo_que_el_panel_exporta_es_lo_que_el_consumidor_lee():
    salida = _exportar(EDICIONES, BASE, "industrial")

    # the export shape: defaults do not travel, decisions do
    assert sorted(salida["piezas"]) == ["alfa", "beta"]
    assert salida["regimen"] == "industrial"
    assert salida["_doc"] == BASE["_doc"]
    alfa = salida["piezas"]["alfa"]
    assert alfa["titulo"] == "Diseño y daño — el año"
    assert alfa["abstraccion"] == 0.35          # rounded to 2 decimals
    assert alfa["orden_ritual"] == 3            # unknown field, preserved
    assert salida["piezas"]["beta"] == {"mostrar": False}

    # the validator accepts it: zero errors (the unknown field is an AVISO)
    hallazgos = vc.validar_curaduria(
        json.dumps(salida, ensure_ascii=False),
        {"alfa", "beta", "zeta"}, existe=lambda s: True)
    errores = [h for h in hallazgos if h[0] == "ERROR"]
    assert errores == [], errores

    # the consumer obeys it: the same file, read by aplicar_curaduria()
    r = contrato_archivo.aplicar_curaduria(_datos(), salida,
                                           existe=lambda s: True)
    ids = {p["id"] for p in r["piezas"]}
    assert ids == {"alfa", "zeta"}              # beta out, with its links
    assert r["vinculos"] == []
    a = next(p for p in r["piezas"] if p["id"] == "alfa")
    assert a["titulo"] == "Diseño y daño — el año"   # diacritics intact
    assert a["extra"]["titulo_firmado"] is True
    assert a["peso"] == 2.5
    assert a["extra"]["serie"] == "raíces"
    assert a["extra"]["nota"] == "Ésta abre la serie."
    assert "orden_ritual" not in a and "orden_ritual" not in a["extra"]


@requiere_node
def test_importar_y_reexportar_no_destruye_lo_que_el_panel_no_entiende():
    """The tablero's own rule, applied to the curation: a per-piece field a
    future agent added by hand must survive a load -> download cycle even
    though no control edits it. Before 2026-07-31 construirCuraduria() only
    copied the fields it knew, so continuing an edited file silently stripped
    everyone else's data."""
    base = {"version": 1, "regimen": "semantico",
            "piezas": {"alfa": {"titulo": "Año nuevo", "orden_ritual": 3},
                       "beta": {"capa_extra": "fondo"}}}
    guion = """
%s
%s
%s
const document = {getElementById: () => ({})};
let BASE = null;
let REGIMEN_GLOBAL = "semantico";
const EDICIONES = new Map();
sembrarBase(%s);
console.log(JSON.stringify(construirCuraduria()));
""" % (_extraer_campos(), _extraer_funcion("construirCuraduria"),
       _extraer_funcion("sembrarBase"), json.dumps(base, ensure_ascii=False))
    r = subprocess.run(["node", "--input-type=module", "-e", guion],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    salida = json.loads(r.stdout.strip().splitlines()[-1])
    assert salida["piezas"] == base["piezas"]


@requiere_node
def test_el_script_entero_del_editor_parsea():
    """The two tests above extract single functions, so a syntax error in the
    page's wiring (listeners, import, guard) would slip past them while the
    panel dies on load. node parses the WHOLE inline script."""
    texto = EDITOR.read_text(encoding="utf-8")
    inicio = texto.index("<script>") + len("<script>")
    fin = texto.index("</script>")
    r = subprocess.run(["node", "--input-type=module", "--check", "-"],
                       input=texto[inicio:fin], capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, r.stderr
