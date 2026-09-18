#!/usr/bin/env python3
"""Detectors over the SHAPE of a table, not the content of its rows.

`patrones.py` answers "does this annotation repeat, and where did it come
from?". This module answers something prior, and which turns everything
else into garbage if it fails: **does the table have the shape the reader
assumes?**

The four patterns here came out of measuring `Testeo 2025` on 2026-09-16,
and each one cost a real error in figures that had already been reported:

1. `columnas_divergentes` -- 68 sheets with EIGHT different header
   structures. The reader mapped columns by fixed position, so on sheets
   with one extra column the format landed where the result goes and the
   color where the reagent goes. 87 samples with their reagent swapped,
   and the vocabulary ended up with "reagents" called `azul` and
   `celeste`.

2. `bloques_desprendidos` -- a sheet with the session at the top and
   another block 288 rows further down. If that block doesn't match
   anything, it gets counted as real samples with nobody looking at it.

3. `rotulos_intercalados` -- a row that only carries the first field with
   the rest empty, in the middle of the table. It's not data: it's the
   title of ANOTHER session stuck inside the same sheet (`HABITACION DEL
   PANICO` inside `Psiquiatrico 1603`). Counting it adds a sample that
   doesn't exist and hides an entire session.

4. `grupos_duplicados` -- a group whose content is already almost
   entirely inside another one. `Copy of Copy of DAME 0911 A` carried the
   31 rows of `DAME 0911 A`, and 14 escaped the contiguous-run detector
   because they were interleaved among repetitions.

Everything here MARKS, never deletes: the decision to exclude is human,
same as in `patrones.py`.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict

from .registro import Hallazgo

# A row gap bigger than this separates two distinct blocks, not a blank
# row. Measured: the real detached blocks in the corpus jump 100 and 288
# rows; cosmetic gaps within a table jump 6 to 12.
SALTO_BLOQUE = 40

# How much of one group has to sit inside another to call it a duplicate.
# At 0.8, `Copy of Copy of DAME 0911 A` (100%) gets marked, and the pairs
# of tables from the same party, which share at most 29%, don't.
FRACCION_DUPLICADO = 0.8

# How many groups have to share a structure for it to count as THE
# structure. Below this there is no majority and nobody gets accused.
MINIMO_MAYORIA = 3


def _clave(valor: object) -> str:
    t = unicodedata.normalize("NFKD", str(valor or "").strip().lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def columnas_divergentes(encabezados: dict[str, list],
                         minimo_mayoria: int = MINIMO_MAYORIA) -> list[Hallazgo]:
    """Groups whose header row doesn't have the shape of the majority.

    `encabezados` is {group: [cell, cell, ...]} with the first row of each
    group. It doesn't judge the text of each cell but the POSITION of the
    fields: two sheets naming the same thing `Test 1` and `test_1` are
    equal; one with two empty columns in the middle is not.

    Returns one finding per divergent group, with the expected shape and
    the one it has, so it can be read without opening the file.
    """
    formas: dict[tuple, list[str]] = defaultdict(list)
    for grupo, fila in encabezados.items():
        formas[tuple(_clave(c) for c in fila)].append(grupo)
    if not formas:
        return []

    forma_mayor, grupos_mayor = max(formas.items(), key=lambda kv: len(kv[1]))
    if len(grupos_mayor) < minimo_mayoria:
        # With no clear majority there is no divergence to declare: it
        # would mean accusing one sheet of not looking like another
        # equally odd one.
        return []

    hallazgos = []
    for forma, grupos in formas.items():
        if forma == forma_mayor:
            continue
        posicion = {c: i for i, c in enumerate(forma) if c}
        esperado = {c: i for i, c in enumerate(forma_mayor) if c}
        corridos = sorted(c for c in posicion if c in esperado
                          and posicion[c] != esperado[c])
        for grupo in grupos:
            hallazgos.append(Hallazgo(
                patron="columnas_divergentes",
                # If there are shifted fields, the positional reader is
                # ALREADY reading it wrong: that is provable, not a
                # suspicion.
                certeza="confirmado" if corridos else "probable",
                grupo=grupo,
                n=len(corridos) or 1,
                explicacion=(
                    f"el encabezado no tiene la forma de las otras "
                    f"{len(grupos_mayor)}: "
                    + (f"{len(corridos)} campos corridos de columna "
                       f"({', '.join(corridos[:4])})" if corridos
                       else "campos con otro nombre o ausentes")),
                evidencia={"forma": list(forma), "forma_mayoritaria": list(forma_mayor),
                           "campos_corridos": corridos},
            ))
    return hallazgos


def bloques_desprendidos(posiciones: dict[str, list[int]],
                         salto: int = SALTO_BLOQUE) -> list[Hallazgo]:
    """Groups whose rows come in blocks separated by a large gap.

    `posiciones` is {group: [row_number, ...]} with the rows that carry
    data. A gap of dozens of rows is not a decorative blank line: it's
    another block, and it has to be looked at before adding it to the
    total.
    """
    hallazgos = []
    for grupo, filas in posiciones.items():
        orden = sorted(filas)
        cortes = [(a, b) for a, b in zip(orden, orden[1:]) if b - a > salto]
        if not cortes:
            continue
        hallazgos.append(Hallazgo(
            patron="bloque_desprendido",
            certeza="probable",
            grupo=grupo,
            n=len(cortes) + 1,
            explicacion=(
                f"las filas vienen en {len(cortes) + 1} bloques separados; "
                f"el hueco mayor salta {max(b - a for a, b in cortes)} filas"),
            evidencia={"cortes": cortes, "primera": orden[0], "ultima": orden[-1]},
        ))
    return hallazgos


def rotulos_intercalados(filas: dict[str, list[tuple[int, list]]]) -> list[Hallazgo]:
    """Rows that carry ONLY the first field, in the middle of a table with data.

    `filas` is {group: [(number, [cell, ...]), ...]}. A row like that is
    not incomplete data: it's a title. In the corpus it marked where
    another session started within the same sheet, so besides adding a
    nonexistent sample it hid an entire event.
    """
    hallazgos = []
    for grupo, filas_grupo in filas.items():
        if len(filas_grupo) < 3:
            continue
        sospechosas = [
            (n, celdas[0]) for n, celdas in filas_grupo
            if str(celdas[0] or "").strip()
            and not any(str(c or "").strip() for c in celdas[1:])
        ]
        # Only counts if there is data AFTER it: a label at the end is a note.
        ultima_con_datos = max(
            (n for n, celdas in filas_grupo
             if any(str(c or "").strip() for c in celdas[1:])), default=-1)
        sospechosas = [(n, t) for n, t in sospechosas if n < ultima_con_datos]
        if not sospechosas:
            continue
        hallazgos.append(Hallazgo(
            patron="rotulo_intercalado",
            certeza="probable",
            grupo=grupo,
            n=len(sospechosas),
            explicacion=(
                f"{len(sospechosas)} fila(s) traen solo el primer campo en "
                f"medio de la tabla: parecen titulo, no dato "
                f"({', '.join(str(t)[:24] for _, t in sospechosas[:3])})"),
            evidencia={"filas": [n for n, _ in sospechosas],
                       "textos": [str(t) for _, t in sospechosas]},
        ))
    return hallazgos


def grupos_duplicados(contenidos: dict[str, set],
                      fraccion: float = FRACCION_DUPLICADO) -> list[Hallazgo]:
    """Groups whose content already sits almost entirely inside another group.

    `contenidos` is {group: {comparable_content, ...}}. It complements
    `tramos_ajenos`, which requires a CONTIGUOUS run: when the copy was
    edited, the matches end up interleaved and no run reaches the
    minimum, but the set as a whole is still almost entirely repeated.
    """
    hallazgos = []
    for grupo, propio in contenidos.items():
        if not propio:
            continue
        for otro, ajeno in contenidos.items():
            if otro == grupo or not ajeno:
                continue
            comun = propio & ajeno
            if len(comun) < fraccion * len(propio):
                continue
            # The smaller one is the copy; at equal size, whichever name says so.
            if len(propio) > len(ajeno):
                continue
            if len(propio) == len(ajeno) and not _parece_copia(grupo, otro):
                continue
            hallazgos.append(Hallazgo(
                patron="grupo_duplicado",
                certeza="confirmado" if len(comun) == len(propio) else "probable",
                grupo=grupo,
                n=len(comun),
                explicacion=(
                    f"{len(comun)} de sus {len(propio)} registros "
                    f"({len(comun) / len(propio) * 100:.0f}%) ya estan en "
                    f"«{otro}»"),
                origen=otro,
                evidencia={"propios": len(propio), "en_el_otro": len(ajeno)},
            ))
            break
    return hallazgos


def _parece_copia(a: str, b: str) -> bool:
    """`Copy of X` / `Copia de X` declares itself a copy in its own name."""
    ka, kb = _clave(a), _clave(b)
    return (ka.startswith(("copy_of", "copia_de")) and not
            kb.startswith(("copy_of", "copia_de")))


def analizar_estructura(encabezados: dict[str, list] | None = None,
                        posiciones: dict[str, list[int]] | None = None,
                        filas: dict[str, list[tuple[int, list]]] | None = None,
                        contenidos: dict[str, set] | None = None) -> list[Hallazgo]:
    """Runs the four detectors with whatever was given to it.

    Every argument is optional: an area that only has the headers can run
    just that one. The output order puts first whatever invalidates the
    most reading -- a shifted column ruins every row in its group.
    """
    hallazgos: list[Hallazgo] = []
    if encabezados:
        hallazgos += columnas_divergentes(encabezados)
    if contenidos:
        hallazgos += grupos_duplicados(contenidos)
    if filas:
        hallazgos += rotulos_intercalados(filas)
    if posiciones:
        hallazgos += bloques_desprendidos(posiciones)
    orden = {"columnas_divergentes": 0, "grupo_duplicado": 1,
             "rotulo_intercalado": 2, "bloque_desprendido": 3}
    return sorted(hallazgos, key=lambda h: (orden.get(h.patron, 9), -h.n))
