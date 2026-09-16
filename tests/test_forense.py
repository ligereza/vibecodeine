"""Tests de `cultura/mak_forense` -- procedencia de un registro.

El test que justifica el modulo es `test_lote_contiguo_no_se_cuenta_como_copia`:
contar filas identicas y llamarlas duplicadas fue el error que inflo el daño
en el analisis de `Testeo 2025`. La geometria -- no el contenido -- es lo que
separa un bloque pegado de una tanda real de muestras iguales.
"""
from __future__ import annotations

import datetime
import sqlite3

import pytest

from cultura.mak_forense.patrones import (
    analizar,
    anacronismos,
    periodo_dominante,
    rafagas,
    repeticiones,
    tramos_ajenos,
)
from cultura.mak_forense.registro import Registro
from cultura.mak_forense import fuentes

_HORA = 3600.0


def _r(id_, grupo, orden, contenido, **kw):
    return Registro(id=str(id_), grupo=grupo, orden=orden,
                    contenido=tuple(contenido), **kw)


def _bloque(grupo, base, filas, copias, periodo):
    """`filas` anotaciones distintas, pegadas `copias` veces cada `periodo`."""
    salida = []
    for c in range(copias):
        for i, contenido in enumerate(filas):
            orden = base + c * periodo + i
            salida.append(_r(f"{grupo}-{orden}", grupo, orden, contenido))
    return salida


def _patrones(hallazgos):
    return {h.patron for h in hallazgos}


# --------------------------------------------------------------------------
# la distincion central

def test_bloque_pegado_se_detecta_por_su_periodo():
    filas = [("mdma", "pastilla", "marquis", "negro"),
             ("ket", "polvo", "morris", "morado"),
             ("coca", "polvo", "scott", "azul")]
    hallazgos = repeticiones(_bloque("Mamisonga", 1, filas, copias=6, periodo=3))
    bloque = [h for h in hallazgos if h.patron == "bloque_periodico"]
    assert bloque, "un bloque pegado seis veces tiene que verse"
    assert bloque[0].evidencia["periodo"] == 3
    assert bloque[0].certeza == "confirmado"


def test_lote_contiguo_no_se_cuenta_como_copia():
    """Cinco ketaminas seguidas con el mismo resultado son cinco muestras.

    `DAME 1503` tiene 37 de sus 39 repeticiones asi. Llamarlas duplicadas
    borraria testeos reales.
    """
    misma = ("ket", "polvo", "morris", "morado")
    filas = [_r(f"x{i}", "DAME 1503", i, misma) for i in range(1, 6)]
    hallazgos = repeticiones(filas)
    assert "bloque_periodico" not in _patrones(hallazgos)
    contiguo = [h for h in hallazgos if h.patron == "lote_contiguo"]
    assert contiguo and contiguo[0].n == 4
    assert contiguo[0].certeza == "probable"
    assert "NO se descuenta" in contiguo[0].explicacion


def test_periodo_dominante_exige_que_el_patron_explique_al_grupo():
    """Una coincidencia suelta no convierte al grupo en un pegado."""
    assert periodo_dominante([[1, 40]]) is None
    assert periodo_dominante([[1, 6], [2, 7], [3, 8]], minimo=3) == 5


# --------------------------------------------------------------------------
# tramos que vienen de otra jornada

def _dos_jornadas(dias_entre=1):
    """Una jornada original de 12 anotaciones propias y una copia diluida."""
    propias = [(f"s{i}", "polvo", "marquis", f"c{i}") for i in range(12)]
    origen = [_r(f"o{i}", "DAME 1503", i, c, fecha_declarada="2024-03-15")
              for i, c in enumerate(propias)]
    fecha_copia = (datetime.date(2024, 3, 15)
                   + datetime.timedelta(days=dias_entre)).isoformat()
    copia = [_r(f"c{i}", "Psiquiatrico", i, c, fecha_declarada=fecha_copia)
             for i, c in enumerate(propias[:8])]
    copia += [_r(f"n{i}", "Psiquiatrico", 8 + i,
                 (f"nueva{i}", "pastilla", "morris", "negro"),
                 fecha_declarada=fecha_copia) for i in range(20)]
    return {"DAME 1503": origen, "Psiquiatrico": copia}


def test_la_copia_es_la_jornada_donde_el_tramo_pesa_menos():
    hallazgos = tramos_ajenos(_dos_jornadas())
    assert len(hallazgos) == 1, "el hallazgo se emite una sola vez, del lado de la copia"
    h = hallazgos[0]
    assert h.grupo == "Psiquiatrico" and h.origen == "DAME 1503"
    assert h.n == 8
    assert h.evidencia["peso_origen"] > h.evidencia["peso_grupo"]


def test_la_fecha_corrobora_y_el_hallazgo_queda_confirmado():
    h = tramos_ajenos(_dos_jornadas(dias_entre=1))[0]
    assert h.certeza == "confirmado"
    assert h.evidencia["veredicto_fecha"] == "coincide"
    assert h.evidencia["dias_entre"] == 1


def test_si_la_fecha_contradice_al_peso_nadie_decide_solo():
    """Copiar del futuro no existe: cuando las senales chocan, va a revision."""
    h = tramos_ajenos(_dos_jornadas(dias_entre=-28))[0]
    assert h.certeza == "pendiente"
    assert h.evidencia["veredicto_fecha"] == "contradice"
    assert "decide una persona" in h.explicacion


def test_un_tramo_corto_no_alcanza():
    """Tres filas genericas compartidas fueron un falso positivo real."""
    comunes = [("mdma", "tesla rosada", "marquis", "negro")] * 3
    a = [_r(f"a{i}", "Fiesta Dame", i, c) for i, c in enumerate(comunes)]
    b = [_r(f"b{i}", "Cachorros 35", i, c) for i, c in enumerate(comunes)]
    assert tramos_ajenos({"Fiesta Dame": a, "Cachorros 35": b}) == []


def test_las_replicas_internas_no_multiplican_el_tramo_ajeno():
    """El tramo se trajo UNA vez; lo que pasa despues lo explica `repeticiones`."""
    filas = [(f"s{i}", "polvo", "marquis", f"c{i}") for i in range(8)]
    origen = [_r(f"o{i}", "Cachorros", i, c) for i, c in enumerate(filas)]
    copia = _bloque("Mamisonga", 0, filas, copias=10, periodo=8)
    hallazgos = tramos_ajenos({"Cachorros": origen, "Mamisonga": copia})
    assert sum(h.n for h in hallazgos) == 8


# --------------------------------------------------------------------------
# el tiempo: lo que XIO-RD puede detectar y una planilla no

def _instante(iso):
    return datetime.datetime.fromisoformat(iso).replace(
        tzinfo=datetime.timezone.utc).timestamp()


def test_muestra_cargada_en_un_evento_que_todavia_no_ocurre():
    filas = [_r("m1", "evt", 1, ("mdma",), fecha_declarada="2026-10-10",
                instante_registro=_instante("2026-09-16T22:00:00"))]
    h = anacronismos(filas)
    assert [x.patron for x in h] == ["registro_en_evento_futuro"]
    assert h[0].certeza == "confirmado"


def test_muestra_cargada_en_un_evento_ya_pasado():
    filas = [_r("m1", "evt", 1, ("mdma",), fecha_declarada="2026-01-10",
                instante_registro=_instante("2026-09-16T22:00:00"))]
    assert [x.patron for x in anacronismos(filas)] == ["registro_en_evento_pasado"]


def test_la_carga_dentro_de_su_jornada_no_se_marca():
    """Una fiesta termina de madrugada y los datos se suben despues."""
    filas = [_r("m1", "evt", 1, ("mdma",), fecha_declarada="2026-09-15",
                instante_registro=_instante("2026-09-16T06:30:00"))]
    assert anacronismos(filas) == []


def test_una_rafaga_no_se_tipeo_a_esa_hora():
    base = _instante("2026-09-15T23:00:00")
    filas = [_r(f"m{i}", "evt", i, (f"s{i}",), instante_registro=base + i * 0.4)
             for i in range(8)]
    h = rafagas(filas)
    assert h and h[0].n == 8 and h[0].patron == "rafaga_no_humana"


def test_registro_sin_instante_no_se_marca_ni_se_absuelve():
    filas = [_r("m1", "evt", 1, ("mdma",), fecha_declarada="2020-01-01")]
    assert anacronismos(filas) == []
    assert rafagas(filas) == []
    cobertura = analizar(filas).cobertura
    assert cobertura.sin_instante_registro == 1
    assert any("sin instante de carga" in l for l in cobertura.limites)


# --------------------------------------------------------------------------
# el contrato del modulo

def test_el_analisis_declara_lo_que_no_pudo_ver():
    analisis = analizar(sum(_dos_jornadas().values(), []))
    limites = analisis.cobertura.limites
    assert any("grupos de esta corrida" in l for l in limites), (
        "el punto ciego que hizo invisible el copiado entre años tiene que "
        "estar escrito en el informe, no solo en el codigo")
    assert any("repeticion contigua" in l for l in limites)
    assert analisis.cobertura.pares_comparados == 2


def test_nada_se_borra():
    registros = sum(_dos_jornadas().values(), [])
    analisis = analizar(registros)
    assert analisis.cobertura.registros == len(registros)
    marcados = {r for h in analisis.hallazgos for r in h.registros}
    assert marcados.issubset({r.id for r in registros})
    assert "nunca lo borra" in analisis.como_dict()["principio"]


def test_certeza_desconocida_es_un_error_no_un_campo_libre():
    from cultura.mak_forense.registro import Hallazgo
    with pytest.raises(ValueError):
        Hallazgo(patron="x", certeza="casi", grupo="g", n=1, explicacion="")


def test_fuente_xio_usa_timestamp_de_captura_y_no_fecha_del_evento(tmp_path):
    db = tmp_path / "rd.db"
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE muestras (
            id INTEGER PRIMARY KEY, fecha TEXT, evento_ref TEXT,
            evento_origen TEXT, codigo_muestra TEXT,
            sustancia_declarada TEXT, tipo_muestra TEXT, color TEXT,
            textura TEXT, logo_o_marca TEXT, peso_mg REAL, descartada INTEGER
        );
        CREATE TABLE muestra_capturas (
            id INTEGER PRIMARY KEY, muestra_id INTEGER,
            capture_key TEXT, captured_at_epoch INTEGER
        );
    """)
    conn.execute(
        "INSERT INTO muestras VALUES (1, '2026-10-10', 'evt-futuro', "
        "'xio', 'm-1', 'mdma', 'pastilla', 'azul', 'lisa', 'x', 100, 0)"
    )
    conn.execute(
        "INSERT INTO muestra_capturas VALUES (1, 1, 'cap-1', 1790200800)"
    )
    conn.commit()
    conn.close()

    registros, limites = fuentes.desde_muestras_rd(db)

    assert len(registros) == 1
    assert registros[0].fecha_declarada is None
    assert registros[0].instante_registro == 1790200800.0
    assert any("0 muestras sin captura" in limite for limite in limites)
