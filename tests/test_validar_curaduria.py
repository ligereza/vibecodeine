# -*- coding: utf-8 -*-
"""The loud counterpart of a consumer that obeys in silence.

aplicar_curaduria() is right to swallow an unknown id or a missing signed
svg on the published site -- and wrong at editing time, when that silence
means an edit the artist made never happens and nobody says so.
tools/validar_curaduria.py reports exactly those swallowed findings, plus the
one defect class this repo treats as firing-level: mangled diacritics in a
human-read value. These tests pin what is an ERROR, what is an AVISO, and
that the real files in the repo validate clean (the CLI run at the end is the
CI hook).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))

import validar_curaduria as vc  # noqa: E402


def _niveles(hallazgos, codigo):
    return [n for n, c, _ in hallazgos if c == codigo]


def _cur(piezas, regimen="semantico"):
    return json.dumps({"version": 1, "regimen": regimen, "piezas": piezas},
                      ensure_ascii=False)


CONOCIDOS = {"a", "b", "anim-a"}


def test_archivo_limpio_no_reporta_nada():
    cur = _cur({"a": {"titulo": "El daño y el año — diseño", "abstraccion": 0.4,
                      "peso": 2, "serie": "raíces", "nota": "Va acá."}})
    assert vc.validar_curaduria(cur, CONOCIDOS, existe=lambda s: True) == []


def test_json_roto_y_forma_no_objeto_son_error():
    assert _niveles(vc.validar_curaduria("{no json", CONOCIDOS), "json") == ["ERROR"]
    assert _niveles(vc.validar_curaduria("[1,2]", CONOCIDOS), "forma") == ["ERROR"]


def test_id_duplicado_es_error_porque_json_se_queda_con_uno():
    # json.loads keeps the LAST duplicate silently: two decisions, one vanishes
    crudo = '{"piezas": {"a": {"titulo": "uno"}, "a": {"titulo": "dos"}}}'
    h = vc.validar_curaduria(crudo, CONOCIDOS, existe=lambda s: True)
    assert _niveles(h, "clave-duplicada") == ["ERROR"]


def test_id_desconocido_es_aviso_no_error():
    """The consumer ignores unknown ids BY DESIGN (the curation may name
    works today's filter left out), so it cannot be an ERROR -- but a typo'd
    id is an edit that never happens, so it must be SAID."""
    h = vc.validar_curaduria(_cur({"fantasma": {"titulo": "x"}}),
                             CONOCIDOS, existe=lambda s: True)
    assert _niveles(h, "id-desconocido") == ["AVISO"]
    assert not any(n == "ERROR" for n, _, _ in h)


def test_regimen_desconocido_es_error_global_y_por_pieza():
    h = vc.validar_curaduria(_cur({}, regimen="vaporwave"), CONOCIDOS)
    assert _niveles(h, "regimen") == ["ERROR"]
    h2 = vc.validar_curaduria(_cur({"a": {"regimen": "brutalista"}}),
                              CONOCIDOS, existe=lambda s: True)
    assert _niveles(h2, "regimen") == ["ERROR"]


def test_diacriticos_mutilados_son_error():
    """The 'reduciendo ano' defect class, measured: mojibake in a value a
    human reads is never a style."""
    for malo in ("DiseÃ±o de campo", "El aÃ±o pasado", "raro�texto"):
        h = vc.validar_curaduria(_cur({"a": {"titulo": malo}}),
                                 CONOCIDOS, existe=lambda s: True)
        assert _niveles(h, "diacriticos") == ["ERROR"], malo
    # correct Spanish with diacritics passes untouched
    h = vc.validar_curaduria(_cur({"a": {"nota": "Ñandú — el diseño del daño"}}),
                             CONOCIDOS, existe=lambda s: True)
    assert h == []


def test_nfd_es_aviso():
    # "n" + combining tilde renders fine but breaks equality searches
    h = vc.validar_curaduria(_cur({"a": {"titulo": "año nuevo"}}),
                             CONOCIDOS, existe=lambda s: True)
    assert _niveles(h, "no-nfc") == ["AVISO"]


def test_svg_ausente_es_aviso_porque_el_consumidor_lo_ignora():
    h = vc.validar_curaduria(_cur({"a": {"svg": "firmadas/no-esta.svg"}}),
                             CONOCIDOS, existe=lambda s: False)
    assert _niveles(h, "svg-ausente") == ["AVISO"]
    h2 = vc.validar_curaduria(_cur({"a": {"svg": "firmadas/si.svg"}}),
                              CONOCIDOS, existe=lambda s: True)
    assert h2 == []


def test_valores_invalidos_de_cada_campo():
    h = vc.validar_curaduria(_cur({
        "a": {"mostrar": "no"},
        "b": {"abstraccion": "mucha", "peso": -1},
        "anim-a": {"titulo": ""},
    }), CONOCIDOS, existe=lambda s: True)
    assert _niveles(h, "mostrar") == ["ERROR"]
    assert _niveles(h, "abstraccion") == ["ERROR"]
    assert _niveles(h, "peso") == ["ERROR"]
    assert _niveles(h, "texto-invalido") == ["ERROR"]


def test_ruido_y_rango_son_aviso():
    h = vc.validar_curaduria(_cur({"a": {"mostrar": True, "abstraccion": 7}}),
                             CONOCIDOS, existe=lambda s: True)
    assert _niveles(h, "mostrar-true") == ["AVISO"]
    assert _niveles(h, "abstraccion-rango") == ["AVISO"]


def test_campo_desconocido_es_aviso_de_compatibilidad():
    h = vc.validar_curaduria(_cur({"a": {"orden_ritual": 3}}),
                             CONOCIDOS, existe=lambda s: True)
    assert _niveles(h, "campo-desconocido") == ["AVISO"]


def test_tablero_interruptores():
    ok = json.dumps({"version": 1, "mejoras": {"venue3d": False}})
    assert vc.validar_tablero(ok) == []
    h = vc.validar_tablero(json.dumps({"version": 1,
                                       "mejoras": {"umbral": 0.5}}))
    assert _niveles(h, "no-booleana") == ["AVISO"]
    h2 = vc.validar_tablero(json.dumps({"version": 1, "mejoras": []}))
    assert _niveles(h2, "forma") == ["ERROR"]


def test_ids_conocidos_lee_las_fuentes_reales():
    ids, fuente = vc.ids_conocidos()
    assert len(ids) >= 219, "the measured campo alone carries 219 pieces"
    assert fuente


def test_cli_sobre_los_archivos_reales_del_repo():
    """The CI hook: the versioned curaduria.json and tablero.json validate
    clean, exit code 0. If an edit lands a lie, this goes red."""
    r = subprocess.run([sys.executable, str(RAIZ / "tools" / "validar_curaduria.py")],
                       capture_output=True, text=True, timeout=120, cwd=RAIZ)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 errores" in r.stdout


def test_cli_exit_1_con_un_error(tmp_path):
    malo = tmp_path / "curaduria.json"
    malo.write_text(json.dumps({"regimen": "vaporwave", "piezas": {}}),
                    encoding="utf-8")
    r = subprocess.run([sys.executable, str(RAIZ / "tools" / "validar_curaduria.py"),
                        "--curaduria", str(malo)],
                       capture_output=True, text=True, timeout=120, cwd=RAIZ)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "regimen" in r.stdout
