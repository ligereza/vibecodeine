"""
Tests de la base de datos RD (src/flujo/rd/database.py).

La DB es una proyeccion regenerable de fuentes canonicas: estos tests fijan que
build_rd_db es idempotente/deterministico, que las 6 tablas cargan datos reales,
que las queries cruzan bien (reactivo x familia, evento -> pack por voluntarios)
y que el disclaimer presuntivo viaja con los datos.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from flujo.rd import database as db


@pytest.fixture()
def rd_db(tmp_path: Path) -> Path:
    return db.build_rd_db(tmp_path / "rd.db")


def _tables(path: Path) -> dict[str, int]:
    conn = db.connect(path)
    try:
        return {
            t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
            for t in ("meta", "reactivos", "packs", "inclusiones", "suplementos", "productoras", "eventos")
        }
    finally:
        conn.close()


def test_build_crea_las_6_tablas_con_datos(rd_db: Path):
    n = _tables(rd_db)
    assert n["reactivos"] >= 20        # 21 reacciones en la carta canonica
    assert n["packs"] == 3             # INFO / TESTEO / COMPLETO
    assert n["inclusiones"] >= 12
    assert n["suplementos"] >= 8
    assert n["productoras"] >= 1       # The Grid
    # >=1: eventos incluye fuentes en jobs/ que son gitignored (no estan en un
    # checkout limpio/CI); el piso garantizado es el ejemplo TRACKED de plano.
    assert n["eventos"] >= 1
    assert n["meta"] == 1              # disclaimer


def test_build_es_idempotente(tmp_path: Path):
    p = tmp_path / "rd.db"
    db.build_rd_db(p)
    antes = _tables(p)
    db.build_rd_db(p)  # reconstruye sobre si misma sin duplicar
    assert _tables(p) == antes


def test_reactivos_por_familia_cruza(rd_db: Path):
    filas = db.reactivos_por_familia("MDMA", rd_db)
    assert len(filas) >= 3
    assert any(f["reactivo"] == "Marquis" for f in filas)
    # todos matchean la familia pedida
    assert all("mdma" in f["familia"].lower() for f in filas)


def test_reactivos_por_reactivo(rd_db: Path):
    filas = db.reactivos_por_reactivo("Marquis", rd_db)
    assert filas and all(f["reactivo"] == "Marquis" for f in filas)


def test_pack_precio_e_inclusiones(rd_db: Path):
    ps = {p["id"]: p for p in db.packs(rd_db)}
    assert ps["TESTEO"]["precio"] == 300_000
    assert ps["INFO"]["precio"] == 100_000
    assert ps["COMPLETO"]["precio"] == 500_000
    assert len(ps["COMPLETO"]["inclusiones"]) >= 1


def test_precios_derivan_de_packs_py_no_hardcode(rd_db: Path):
    """La DB no inventa precios: coinciden con el modulo canonico plano.packs."""
    from flujo.plano.packs import PACKS

    for p in db.packs(rd_db):
        assert p["precio"] == PACKS[p["id"]]["precio"]
        assert p["voluntarios"] == PACKS[p["id"]]["voluntarios"]


def test_pack_por_voluntarios_mapea_o_none():
    """Logica evento->pack, unitaria (sin depender de eventos gitignored):
    coincide por numero de voluntarios; None si ninguno matchea, sin crash."""
    assert db._pack_por_voluntarios(2) == "INFO"
    assert db._pack_por_voluntarios(6) == "TESTEO"
    assert db._pack_por_voluntarios(15) == "COMPLETO"
    assert db._pack_por_voluntarios(7) is None
    assert db._pack_por_voluntarios(None) is None


def test_evento_tracked_trae_pack_sugerido(rd_db: Path):
    """El ejemplo TRACKED (projects/plano/ejemplos, 7 vol) siempre esta y su
    pack_sugerido queda None (7 no matchea INFO/TESTEO/COMPLETO)."""
    evs = db.eventos(rd_db)
    assert evs, "debe haber al menos el evento ejemplo tracked"
    ej = [e for e in evs if e["voluntarios"] == 7]
    assert ej and ej[0]["pack_sugerido"] is None


def test_productora_trae_aliases_deserializados(rd_db: Path):
    ps = db.productoras(rd_db)
    grid = [p for p in ps if p["slug"] == "thegrid"]
    assert grid
    assert isinstance(grid[0]["aliases"], list)
    assert "GRID" in grid[0]["aliases"]


def test_disclaimer_presuntivo_presente(rd_db: Path):
    d = db.disclaimer(rd_db)
    assert "PRESUNTIVO" in d.upper()


def test_lookup_familia_cruza_reactivos_y_packs(rd_db: Path):
    """El JOIN que justifica la DB: familia -> panel reactivos + packs con
    testeo + disclaimer, en una llamada."""
    res = db.lookup_familia("MDMA", rd_db)
    assert res["familia"] == "MDMA"
    assert len(res["reactivos"]) >= 3
    assert any(r["reactivo"] == "Marquis" for r in res["reactivos"])
    # 'testeo' se detecta en las inclusiones canonicas; TESTEO y COMPLETO al menos
    ids = {p["id"] for p in res["packs_con_testeo"]}
    assert {"TESTEO", "COMPLETO"} <= ids
    assert "PRESUNTIVO" in res["disclaimer"].upper()


def test_lookup_familia_desconocida_no_revienta(rd_db: Path):
    res = db.lookup_familia("sustancia-inexistente", rd_db)
    assert res["reactivos"] == []
    # los packs con testeo no dependen de la familia -> siguen apareciendo
    assert res["packs_con_testeo"]


def test_connect_autoconstruye_si_no_existe(tmp_path: Path):
    p = tmp_path / "nueva.db"
    assert not p.exists()
    conn = db.connect(p)  # debe construirla al vuelo
    try:
        assert conn.execute("SELECT count(*) FROM reactivos").fetchone()[0] >= 20
    finally:
        conn.close()
    assert p.exists()


# --- Perfil de productora: logos + venues + tipos de fecha (vocab controlado) ---

def test_vocab_normaliza_tipos_y_fallback():
    from flujo.rd.vocab import normalize_tipo, normalize_tipos, TIPOS_FECHA

    assert normalize_tipo("rave") == "RAVE"
    assert normalize_tipo("after party") == "AFTER"
    assert normalize_tipo("underground") == "UNDERGROUND"
    assert normalize_tipo("cosa-inexistente") == "OTRO"   # nunca se pierde
    # dedup + orden canonico deterministico
    got = normalize_tipos(["rave", "festival", "rave", "after"])
    assert got == [t for t in TIPOS_FECHA if t in {"FESTIVAL", "RAVE", "AFTER"}]


def test_venues_canonicos_desde_yaml(rd_db: Path):
    vs = {v["nombre"]: v for v in db.venues(rd_db)}
    assert "Espacio Riesco" in vs
    er = vs["Espacio Riesco"]
    assert er["preset_reco"] == "mainstream"
    assert er["voluntarios_min"] == 8
    assert isinstance(er["requisitos"], dict)   # requirements_defaults deserializado


def test_perfil_productora_trae_tipos_logos_venues(rd_db: Path):
    p = db.productora("creamfields", rd_db)
    assert p is not None
    assert set(p["tipos_fecha"]) >= {"FESTIVAL", "HEADLINERS", "RAVE"}
    assert p["logos"] and p["logos"][0]["knowledge"].endswith("creamfields.yaml")
    assert p["venue_preferido"] == "Espacio Riesco"
    # el venue matchea el canonico -> venue_id resuelto
    ven = p["venues"][0]
    assert ven["venue_id"] == "espacio_riesco"


def test_productora_inexistente_es_none(rd_db: Path):
    assert db.productora("no-existe", rd_db) is None


def test_productoras_por_tipo(rd_db: Path):
    assert "creamfields" in db.productoras_por_tipo("FESTIVAL", rd_db)
    assert set(db.productoras_por_tipo("rave", rd_db)) >= {"creamfields", "thegrid"}
    assert db.productoras_por_tipo("PRIVADO", rd_db) == []   # nadie, sin crash


def test_venue_preferido_via_fixture_sintetica(tmp_path: Path):
    """La maquinaria venue-preferido + enlace canonico, con una productora
    sintetica (no contamina el store real): 2 venues, el segundo preferido y
    enlazado al venue canonico Espacio Riesco."""
    import json as _json

    pdir = tmp_path / "prods"
    pdir.mkdir()
    (pdir / "acme.json").write_text(_json.dumps({
        "name": "Acme Fiestas",
        "tipos_fecha": ["club", "after"],
        "venues": [
            {"nombre": "Galpon X", "preferido": False, "estado": "confirmado"},
            {"nombre": "Espacio Riesco", "venue_id": "espacio_riesco", "preferido": True, "estado": "confirmado"},
        ],
    }, ensure_ascii=False), encoding="utf-8")

    p = tmp_path / "syn.db"
    db.build_rd_db(p, productoras_dir=pdir)   # venues_dir default -> canonicos reales
    prof = db.productora("acme", p)
    assert prof["venue_preferido"] == "Espacio Riesco"
    assert set(prof["tipos_fecha"]) == {"CLUB", "AFTER"}
    pref = [v for v in prof["venues"] if v["preferido"]][0]
    assert pref["venue_id"] == "espacio_riesco"   # enlazado al canonico
