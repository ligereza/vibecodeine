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
