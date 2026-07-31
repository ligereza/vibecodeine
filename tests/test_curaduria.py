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

# ── The three optional fields (2026-07-31): peso, serie, nota ──────────
# The curation grows by fields that change NOTHING until the artist writes
# them: a new default would be an aesthetic decision that is not ours.


def test_peso_serie_y_nota_viajan_cuando_se_escriben():
    cur = {"piezas": {"a": {"peso": 2.5, "serie": "raíces",
                            "nota": "Ésta abre la serie — el daño y el año."}}}
    r = contrato_archivo.aplicar_curaduria(_datos(), cur, existe=lambda s: True)
    a = next(p for p in r["piezas"] if p["id"] == "a")
    assert a["peso"] == 2.5
    assert a["extra"]["serie"] == "raíces"
    # human-read value: the diacritics survive the whole pass, verbatim
    assert a["extra"]["nota"] == "Ésta abre la serie — el daño y el año."


def test_campos_opcionales_son_inertes_si_no_se_escriben():
    """A piece the curation does not name keeps exactly what its source
    measured: no peso appears, no serie, no nota. Optional means inert."""
    cur = {"piezas": {"a": {"titulo": "sólo el título"}}}
    r = contrato_archivo.aplicar_curaduria(_datos(), cur, existe=lambda s: True)
    a = next(p for p in r["piezas"] if p["id"] == "a")
    assert "peso" not in a
    assert "serie" not in a["extra"] and "nota" not in a["extra"]
    b = next(p for p in r["piezas"] if p["id"] == "b")
    assert b["extra"] == {} and "peso" not in b


def test_peso_no_positivo_no_desplaza_al_medido():
    """peso <= 0 says nothing (a piece with no matter is `mostrar: false`,
    not weight zero), so the source's own peso survives."""
    datos = _datos()
    datos["piezas"][0]["peso"] = 3
    cur = {"piezas": {"a": {"peso": 0}}}
    r = contrato_archivo.aplicar_curaduria(datos, cur, existe=lambda s: True)
    a = next(p for p in r["piezas"] if p["id"] == "a")
    assert a["peso"] == 3
