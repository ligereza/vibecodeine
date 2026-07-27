# -*- coding: utf-8 -*-
"""Las librerias vendorizadas de la piel de iskvw: que existan y que CORRAN.

Un bundle que esta en disco no es un bundle que funciona, y este repo ya se
quemo con eso: 6 de 24 archivos autogenerados compilaban con un NameError
latente. Asi que aca se importan de verdad en node y se les pide trabajo.

Lo que ademas fija este test, medido el 2026-07-27: `@thi.ng/tsne` devuelve las
posiciones en la MISMA dimension que la entrada y no tiene opcion de dimension
de salida (`DEFAULT_OPTS` no la trae). O sea NO reemplaza a scikit-learn para
bajar 768 dimensiones a 2, que es lo que yo mismo habia afirmado sin medirlo. Si
algun dia la libreria gana esa opcion, este test se cae y hay que celebrarlo.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
LIB = _REPO / "iskvw" / "piel" / "lib"
MANIFIESTO = _REPO / "data" / "iskvw_librerias.json"
sys.path.insert(0, str(_REPO / "tools"))

import vendorizar_iskvw as V  # noqa: E402

_NODE = shutil.which("node")
necesita_node = pytest.mark.skipif(not _NODE, reason="node no esta instalado")


def _node(script: str) -> str:
    """Corre un modulo ESM dentro de la carpeta de las librerias."""
    tmp = LIB / "_prueba_pytest.mjs"
    tmp.write_text(script, encoding="utf-8")
    try:
        r = subprocess.run([_NODE, str(tmp)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
    finally:
        tmp.unlink(missing_ok=True)
    assert r.returncode == 0, r.stderr[-1500:]
    return r.stdout


def test_el_manifiesto_declara_para_que_sirve_cada_una():
    """Sin `para`, la libreria no entra. Es la regla del archivo."""
    libs = V.leer(MANIFIESTO)
    assert libs
    for e in libs:
        assert e["para"].strip(), e["nombre"]
        assert e["version"], f"{e['nombre']} sin version fijada"


def test_una_entrada_incompleta_se_dice(tmp_path):
    p = tmp_path / "m.json"
    p.write_text(json.dumps({"librerias": [{"nombre": "x", "paquete": "@a/b"}]}),
                 encoding="utf-8")
    with pytest.raises(ValueError, match="version"):
        V.leer(p)


def test_nombres_repetidos_se_dicen(tmp_path):
    p = tmp_path / "m.json"
    e = {"nombre": "x", "paquete": "@a/b", "version": "1", "para": "algo"}
    p.write_text(json.dumps({"librerias": [e, dict(e)]}), encoding="utf-8")
    with pytest.raises(ValueError, match="repetidos"):
        V.leer(p)


def test_todo_lo_declarado_esta_vendorizado_con_su_README():
    """El README viaja al lado del bundle porque el minificado no dice como se
    llama a nada, y adivinar la firma produce codigo que corre y no hace lo que
    se cree."""
    for e in V.leer(MANIFIESTO):
        js = LIB / f"{e['nombre']}.js"
        assert js.is_file(), f"falta {js.name}: corre py tools/vendorizar_iskvw.py"
        assert js.stat().st_size > 500, f"{js.name} sospechosamente vacio"
        assert (LIB / f"{e['nombre']}.README.md").is_file(), e["nombre"]


def test_no_hay_bundles_huerfanos():
    assert V.huerfanos(V.leer(MANIFIESTO), LIB) == []


@necesita_node
def test_las_cuatro_importan_y_exportan_lo_suyo():
    salida = _node("""
const esperado = {
  './tsne.js': 'TSNE',
  './trazo.js': 'extractSegmentsX',
  './gestos.js': 'gestureStream',
  './distancia.js': 'distanceTransform',
};
for (const [mod, nombre] of Object.entries(esperado)) {
  const m = await import(mod);
  console.log(mod, typeof m[nombre] === 'undefined' ? 'FALTA' : 'ok');
}
""")
    for linea in salida.strip().splitlines():
        assert linea.endswith("ok"), linea


@necesita_node
def test_tsne_corre_y_el_costo_baja():
    """No alcanza con que importe: tiene que converger."""
    salida = _node("""
const {TSNE} = await import('./tsne.js');
const data = [];
for (let i = 0; i < 24; i++) {
  const v = []; for (let j = 0; j < 6; j++) v.push(Math.sin(i * 0.7 + j));
  data.push(v);
}
const t = new TSNE(data, {perplexity: 5, maxIter: 400});
let primero = null, ultimo = null;
for (let i = 0; i < 200; i++) { const c = t.update(); if (i === 4) primero = c; ultimo = c; }
console.log(JSON.stringify({primero, ultimo, dimSalida: t.points[0].length,
                            n: t.points.length}));
""")
    d = json.loads(salida.strip().splitlines()[-1])
    assert d["n"] == 24
    assert d["ultimo"] < d["primero"], f"el costo no bajo: {d}"


@necesita_node
def test_tsne_devuelve_la_dimension_de_la_ENTRADA():
    """Medido 2026-07-27, y corrige una afirmacion que hice sin medir.

    No hay opcion de dimension de salida, asi que esta libreria NO baja 768
    dimensiones a 2 y NO reemplaza a scikit-learn en `gen_campo_iskvw.py`. Sirve
    para datos que ya son de pocas dimensiones. Si algun dia gana la opcion,
    este test falla y hay que rehacer la conclusion.
    """
    salida = _node("""
const {TSNE, DEFAULT_OPTS} = await import('./tsne.js');
const filas = [];
for (const D of [3, 6, 12]) {
  const data = [];
  for (let i = 0; i < 20; i++) {
    const v = []; for (let j = 0; j < D; j++) v.push(Math.sin(i * 0.7 + j));
    data.push(v);
  }
  const t = new TSNE(data, {perplexity: 4, maxIter: 60});
  for (let i = 0; i < 30; i++) t.update();
  filas.push([D, t.points[0].length]);
}
console.log(JSON.stringify({filas, opciones: Object.keys(DEFAULT_OPTS)}));
""")
    d = json.loads(salida.strip().splitlines()[-1])
    for entrada, salida_dim in d["filas"]:
        assert entrada == salida_dim, d["filas"]
    assert "dim" not in d["opciones"], (
        "ahora SI hay opcion de dimension: rehacer la conclusion del handoff")
