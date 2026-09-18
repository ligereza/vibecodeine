"""The SHAPE detectors of `mak_forense`.

Each test pins a case measured on `Testeo 2025` on 2026-09-16, and each
one cost an error in already-reported figures. What's being protected
isn't the number: it's that the detector keeps distinguishing the defect
from the legitimate case that looks like it.
"""
from __future__ import annotations

import pytest

from cultura.mak_forense import (
    analizar_estructura,
    bloques_desprendidos,
    columnas_divergentes,
    grupos_duplicados,
    rotulos_intercalados,
)

pytestmark = pytest.mark.mak

CANON = ["Sustancia", "Formato", "Test 1", "Resultado Test 1"]


def test_columna_corrida_se_confirma_y_nombra_los_campos():
    """The `1904 Team 1` case: two empty columns after Sustancia.

    Reading by position, the format lands where the result goes and the
    color where the reagent goes. That's 52 samples with their reagent
    swapped, so the finding has to be `confirmado` and say WHICH fields
    were shifted.
    """
    enc = {f"hoja {i}": list(CANON) for i in range(3)}
    enc["1904 Team 1"] = ["Sustancia", "", "", "Formato", "Test 1", "Resultado Test 1"]

    h = columnas_divergentes(enc)
    assert len(h) == 1
    assert h[0].grupo == "1904 Team 1"
    assert h[0].certeza == "confirmado"
    assert "formato" in h[0].evidencia["campos_corridos"]


def test_un_encabezado_generico_no_se_acusa_de_corrido():
    """`Explicito 30082025` titles its columns `Column 1..11`.

    There's no field in common with the majority, so nothing can be
    asserted about a shift: it stays `probable`, not `confirmado`.
    Treating it the same as a shifted column would send a perfectly
    readable sheet to review.
    """
    enc = {f"hoja {i}": list(CANON) for i in range(3)}
    enc["Explicito"] = ["Column 1", "Column 2", "Column 3", "Column 4"]

    h = columnas_divergentes(enc)
    assert [x.certeza for x in h] == ["probable"]
    assert h[0].evidencia["campos_corridos"] == []


def test_sin_mayoria_no_se_acusa_a_nadie():
    """With two distinct sheets there's no canonical shape. Marking one
    would mean randomly choosing which of the two is the odd one out."""
    assert columnas_divergentes({"a": CANON, "b": ["X", "Y"]}) == []


def test_bloque_desprendido_separa_el_hueco_real_del_cosmetico():
    """`Mamisonga 8225` jumps from row 11 to row 299. A table with an
    occasional blank line is not that, and must not be flagged."""
    h = bloques_desprendidos({
        "Mamisonga 8225": [2, 3, 4, 11, 299, 300, 301],
        "tabla con espacios": [2, 3, 4, 10, 16, 22],
    })
    assert [x.grupo for x in h] == ["Mamisonga 8225"]
    assert h[0].evidencia["cortes"] == [(11, 299)]


def test_rotulo_intercalado_es_titulo_y_no_dato_incompleto():
    """`Psiquiatrico 1603` carries two sessions: row 221 only says
    "HABITACION DEL PANICO". Counting it adds a nonexistent sample and
    also hides that another session starts there."""
    h = rotulos_intercalados({"Psiquiatrico 1603": [
        (2, ["MDMA", "pasti", "Marquis", "negro"]),
        (221, ["HABITACION DEL PANICO", "", "", ""]),
        (222, ["MDMA", "goomba", "Marquis", "negro"]),
    ]})
    assert len(h) == 1 and h[0].n == 1
    assert h[0].evidencia["filas"] == [221]


def test_una_fila_final_sin_datos_no_es_rotulo():
    """At the end of the table, a row with a single field is a note or
    leftover, not the title of another session: there's nothing below it to title."""
    assert rotulos_intercalados({"hoja": [
        (2, ["MDMA", "pasti", "Marquis", "negro"]),
        (3, ["MDMA", "cupra", "Marquis", "negro"]),
        (9, ["revisar", "", "", ""]),
    ]}) == []


def test_grupo_duplicado_atrapa_lo_que_el_tramo_contiguo_no_ve():
    """`Copy of Copy of DAME 0911 A` carried the rows of `DAME 0911 A`, but
    interleaved among repetitions: no contiguous run reached the minimum
    and the 14 were counted as new samples."""
    h = grupos_duplicados({
        "DAME 0911 A": {("a",), ("b",), ("c",), ("d",), ("e",)},
        "Copy of Copy of DAME 0911 A": {("a",), ("b",), ("c",), ("d",)},
    })
    assert len(h) == 1
    assert h[0].grupo == "Copy of Copy of DAME 0911 A"
    assert h[0].origen == "DAME 0911 A"
    assert h[0].certeza == "confirmado"


def test_dos_mesas_de_la_misma_fiesta_no_son_un_duplicado():
    """`Fiesta Dame 504 mesa 1` and `mesa 2` share at most 29% of their
    rows -- the same batch circulating that night. Marking them as a
    copy would erase an entire table of people served."""
    assert grupos_duplicados({
        "mesa 1": {("a",), ("b",), ("c",), ("d",), ("e",)},
        "mesa 2": {("a",), ("x",), ("y",), ("z",), ("w",)},
    }) == []


def test_analizar_estructura_ordena_por_cuanta_lectura_invalida():
    """A shifted column ruins ALL the rows in its group; a detached block
    only asks to look at a few. The first thing read has to be whatever
    invalidates the most."""
    enc = {f"h{i}": list(CANON) for i in range(3)}
    enc["corrida"] = ["Sustancia", "", "Formato", "Test 1", "Resultado Test 1"]
    h = analizar_estructura(
        encabezados=enc,
        posiciones={"suelta": [1, 2, 300]},
    )
    assert [x.patron for x in h] == ["columnas_divergentes", "bloque_desprendido"]


def test_nada_se_borra_solo_se_marca():
    """The domain rule: a finding points at a group, never removes it.
    The output is a list of marks, not a filtered source."""
    enc = {f"h{i}": list(CANON) for i in range(3)}
    enc["rara"] = ["Sustancia", "", "Formato"]
    h = analizar_estructura(encabezados=enc)
    assert all(isinstance(x.grupo, str) and x.explicacion for x in h)
    assert set(enc) == {"h0", "h1", "h2", "rara"}
