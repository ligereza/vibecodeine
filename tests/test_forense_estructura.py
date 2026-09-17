"""Los detectores de FORMA de `mak_forense`.

Cada test fija un caso medido en `Testeo 2025` el 2026-09-16, y cada uno costo
un error en cifras ya reportadas. Lo que se protege no es el numero: es que el
detector siga distinguiendo el defecto del caso legitimo que se le parece.
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
    """El caso `1904 Team 1`: dos columnas vacias tras Sustancia.

    Leyendo por posicion, el formato entra donde va el resultado y el color
    donde va el reactivo. Son 52 muestras con su reactivo cambiado, asi que
    el hallazgo tiene que ser `confirmado` y decir QUE campos se corrieron.
    """
    enc = {f"hoja {i}": list(CANON) for i in range(3)}
    enc["1904 Team 1"] = ["Sustancia", "", "", "Formato", "Test 1", "Resultado Test 1"]

    h = columnas_divergentes(enc)
    assert len(h) == 1
    assert h[0].grupo == "1904 Team 1"
    assert h[0].certeza == "confirmado"
    assert "formato" in h[0].evidencia["campos_corridos"]


def test_un_encabezado_generico_no_se_acusa_de_corrido():
    """`Explicito 30082025` titula sus columnas `Column 1..11`.

    No hay campo en comun con la mayoria, asi que no se puede afirmar que
    algo este corrido: queda `probable`, no `confirmado`. Tratarlo igual que
    a una columna corrida mandaria a revisar una hoja que se lee bien.
    """
    enc = {f"hoja {i}": list(CANON) for i in range(3)}
    enc["Explicito"] = ["Column 1", "Column 2", "Column 3", "Column 4"]

    h = columnas_divergentes(enc)
    assert [x.certeza for x in h] == ["probable"]
    assert h[0].evidencia["campos_corridos"] == []


def test_sin_mayoria_no_se_acusa_a_nadie():
    """Con dos hojas distintas no hay forma canonica. Marcar una seria
    elegir al azar cual de las dos es la rara."""
    assert columnas_divergentes({"a": CANON, "b": ["X", "Y"]}) == []


def test_bloque_desprendido_separa_el_hueco_real_del_cosmetico():
    """`Mamisonga 8225` salta de la fila 11 a la 299. Una tabla con una linea
    en blanco cada tanto no es eso, y no debe marcarse."""
    h = bloques_desprendidos({
        "Mamisonga 8225": [2, 3, 4, 11, 299, 300, 301],
        "tabla con espacios": [2, 3, 4, 10, 16, 22],
    })
    assert [x.grupo for x in h] == ["Mamisonga 8225"]
    assert h[0].evidencia["cortes"] == [(11, 299)]


def test_rotulo_intercalado_es_titulo_y_no_dato_incompleto():
    """`Psiquiatrico 1603` lleva dos jornadas: la fila 221 solo dice
    «HABITACION DEL PANICO». Contarla suma una muestra inexistente y ademas
    esconde que ahi empieza otra jornada."""
    h = rotulos_intercalados({"Psiquiatrico 1603": [
        (2, ["MDMA", "pasti", "Marquis", "negro"]),
        (221, ["HABITACION DEL PANICO", "", "", ""]),
        (222, ["MDMA", "goomba", "Marquis", "negro"]),
    ]})
    assert len(h) == 1 and h[0].n == 1
    assert h[0].evidencia["filas"] == [221]


def test_una_fila_final_sin_datos_no_es_rotulo():
    """Al final de la tabla, una fila con un solo campo es una nota o un
    resto, no el titulo de otra jornada: no hay nada debajo que titule."""
    assert rotulos_intercalados({"hoja": [
        (2, ["MDMA", "pasti", "Marquis", "negro"]),
        (3, ["MDMA", "cupra", "Marquis", "negro"]),
        (9, ["revisar", "", "", ""]),
    ]}) == []


def test_grupo_duplicado_atrapa_lo_que_el_tramo_contiguo_no_ve():
    """`Copy of Copy of DAME 0911 A` traia las filas de `DAME 0911 A`, pero
    intercaladas entre repeticiones: ningun tramo contiguo llegaba al minimo
    y las 14 se contaban como muestras nuevas."""
    h = grupos_duplicados({
        "DAME 0911 A": {("a",), ("b",), ("c",), ("d",), ("e",)},
        "Copy of Copy of DAME 0911 A": {("a",), ("b",), ("c",), ("d",)},
    })
    assert len(h) == 1
    assert h[0].grupo == "Copy of Copy of DAME 0911 A"
    assert h[0].origen == "DAME 0911 A"
    assert h[0].certeza == "confirmado"


def test_dos_mesas_de_la_misma_fiesta_no_son_un_duplicado():
    """`Fiesta Dame 504 mesa 1` y `mesa 2` comparten a lo sumo un 29% de sus
    filas -- el mismo lote circulando esa noche. Marcarlas como copia
    borraria una mesa entera de personas atendidas."""
    assert grupos_duplicados({
        "mesa 1": {("a",), ("b",), ("c",), ("d",), ("e",)},
        "mesa 2": {("a",), ("x",), ("y",), ("z",), ("w",)},
    }) == []


def test_analizar_estructura_ordena_por_cuanta_lectura_invalida():
    """Una columna corrida arruina TODAS las filas de su grupo; un bloque
    desprendido solo pide mirar unas pocas. Lo primero que se lee tiene que
    ser lo que mas invalida."""
    enc = {f"h{i}": list(CANON) for i in range(3)}
    enc["corrida"] = ["Sustancia", "", "Formato", "Test 1", "Resultado Test 1"]
    h = analizar_estructura(
        encabezados=enc,
        posiciones={"suelta": [1, 2, 300]},
    )
    assert [x.patron for x in h] == ["columnas_divergentes", "bloque_desprendido"]


def test_nada_se_borra_solo_se_marca():
    """La regla del dominio: un hallazgo senala un grupo, nunca lo quita.
    La salida es una lista de marcas, no una fuente filtrada."""
    enc = {f"h{i}": list(CANON) for i in range(3)}
    enc["rara"] = ["Sustancia", "", "Formato"]
    h = analizar_estructura(encabezados=enc)
    assert all(isinstance(x.grupo, str) and x.explicacion for x in h)
    assert set(enc) == {"h0", "h1", "h2", "rara"}
