"""The artist's hand over the perceived, never under it.

curaduria.json is the human edit file (title = the artist's voice, mostrar,
abstraccion 0..1, signed svg override, regimen). aplicar_curaduria() runs
LAST over unir()'s result and wins over every source. These tests pin the
contract; the skin side is covered by the node smoke plus the browser checks
recorded in the PR.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cultura" / "mak_plataforma"))

import contrato_archivo  # noqa: E402


def _datos():
    return {
        "piezas": [
            {"id": "a", "titulo": None, "clase": "obra", "extra": {},
             "medio": {"tipo": "imagen", "src": "x/a.jpg"}},
            {"id": "b", "titulo": None, "clase": "obra", "extra": {}},
            {"id": "anim-a", "titulo": "anim-a", "clase": "pieza_grafica",
             "extra": {}, "medio": {"tipo": "imagen", "src": "gen/a.svg"}},
        ],
        "vinculos": [
            {"de": "anim-a", "a": "a", "peso": 1.0, "clase": "manual"},
            {"de": "a", "a": "b", "peso": 0.5, "clase": "semantico"},
        ],
    }


def test_titulo_firmado_y_abstraccion():
    cur = {"piezas": {"a": {"titulo": "VOLÁ — lo visible", "abstraccion": 0.7}}}
    r = contrato_archivo.aplicar_curaduria(_datos(), cur, existe=lambda s: True)
    a = next(p for p in r["piezas"] if p["id"] == "a")
    assert a["titulo"] == "VOLÁ — lo visible"
    assert a["extra"]["titulo_firmado"] is True
    assert a["extra"]["abstraccion"] == 0.7


def test_mostrar_false_saca_pieza_y_vinculos():
    cur = {"piezas": {"a": {"mostrar": False}}}
    r = contrato_archivo.aplicar_curaduria(_datos(), cur, existe=lambda s: True)
    assert "a" not in {p["id"] for p in r["piezas"]}
    assert all("a" not in (v["de"], v["a"]) for v in r["vinculos"])


def test_svg_firmado_desplaza_al_generado_solo_si_existe():
    cur = {"piezas": {"anim-a": {"svg": "firmadas/a.svg"}}}
    r = contrato_archivo.aplicar_curaduria(_datos(), cur,
                                           existe=lambda s: s == "firmadas/a.svg")
    p = next(x for x in r["piezas"] if x["id"] == "anim-a")
    assert p["medio"]["src"] == "firmadas/a.svg" and p["extra"]["firmada"] is True
    # y si NO existe, se conserva el generado: nunca un src que 404ea
    r2 = contrato_archivo.aplicar_curaduria(_datos(), cur, existe=lambda s: False)
    p2 = next(x for x in r2["piezas"] if x["id"] == "anim-a")
    assert p2["medio"]["src"] == "gen/a.svg" and "firmada" not in p2["extra"]


def test_abstraccion_se_acota_e_ids_desconocidos_se_ignoran():
    cur = {"piezas": {"a": {"abstraccion": 7}, "fantasma": {"titulo": "x"}}}
    r = contrato_archivo.aplicar_curaduria(_datos(), cur, existe=lambda s: True)
    a = next(p for p in r["piezas"] if p["id"] == "a")
    assert a["extra"]["abstraccion"] == 1.0
    assert len(r["piezas"]) == 3
