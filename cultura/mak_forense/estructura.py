#!/usr/bin/env python3
"""Detectores sobre la FORMA de una tabla, no sobre el contenido de sus filas.

`patrones.py` responde «¿esta anotacion se repite, y de donde vino?». Este
modulo responde algo anterior, y que si falla vuelve basura todo lo demas:
**¿la tabla tiene la forma que el lector supone?**

Los cuatro patrones de aca salieron de medir `Testeo 2025` el 2026-09-16, y
cada uno costo un error real en cifras que ya se habian reportado:

1. `columnas_divergentes` -- 68 hojas con OCHO estructuras de encabezado
   distintas. El lector mapeaba columnas por posicion fija, asi que en las
   hojas con una columna de mas el formato entraba donde va el resultado y el
   color donde va el reactivo. 87 muestras con su reactivo cambiado, y en el
   vocabulario aparecian «reactivos» llamados `azul` y `celeste`.

2. `bloques_desprendidos` -- una hoja con la jornada arriba y otro bloque 288
   filas mas abajo. Si ese bloque no coincide con nada, se cuenta como
   muestras reales sin que nadie lo mire.

3. `rotulos_intercalados` -- una fila que solo trae el primer campo y el resto
   vacio, en medio de la tabla. No es un dato: es el titulo de OTRA jornada
   metida en la misma hoja (`HABITACION DEL PANICO` dentro de `Psiquiatrico
   1603`). Contarla suma una muestra que no existe y esconde una jornada.

4. `grupos_duplicados` -- un grupo cuyo contenido ya esta casi entero en otro.
   `Copy of Copy of DAME 0911 A` traia las 31 filas de `DAME 0911 A`, y 14
   escapaban al detector de tramos contiguos porque estaban intercaladas
   entre repeticiones.

Todo lo de aca MARCA, nunca borra: la decision de excluir es humana, igual
que en `patrones.py`.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict

from .registro import Hallazgo

# Un salto de filas mayor a esto separa dos bloques distintos, no una fila en
# blanco. Medido: los bloques desprendidos reales del corpus saltan 100 y 288
# filas; las separaciones cosmeticas dentro de una tabla saltan 6 a 12.
SALTO_BLOQUE = 40

# Cuanto de un grupo tiene que estar dentro de otro para llamarlo duplicado.
# Con 0.8 se marca `Copy of Copy of DAME 0911 A` (100%) y no se marcan los
# pares de mesas de una misma fiesta, que comparten a lo sumo 29%.
FRACCION_DUPLICADO = 0.8

# Cuantos grupos tienen que compartir una estructura para que sea LA
# estructura. Por debajo de esto no hay mayoria y no se acusa a nadie.
MINIMO_MAYORIA = 3


def _clave(valor: object) -> str:
    t = unicodedata.normalize("NFKD", str(valor or "").strip().lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def columnas_divergentes(encabezados: dict[str, list],
                         minimo_mayoria: int = MINIMO_MAYORIA) -> list[Hallazgo]:
    """Grupos cuya fila de encabezado no tiene la forma de la mayoria.

    `encabezados` es {grupo: [celda, celda, ...]} con la primera fila de cada
    grupo. No se juzga el texto de cada celda sino la POSICION de los campos:
    dos hojas que llamen `Test 1` y `test_1` a lo mismo son iguales; una que
    tenga dos columnas vacias en medio, no.

    Devuelve un hallazgo por grupo divergente, con la forma esperada y la que
    trae, para que se pueda leer sin abrir el archivo.
    """
    formas: dict[tuple, list[str]] = defaultdict(list)
    for grupo, fila in encabezados.items():
        formas[tuple(_clave(c) for c in fila)].append(grupo)
    if not formas:
        return []

    forma_mayor, grupos_mayor = max(formas.items(), key=lambda kv: len(kv[1]))
    if len(grupos_mayor) < minimo_mayoria:
        # Sin mayoria clara no hay divergencia que declarar: seria acusar a
        # una hoja de no parecerse a otra igual de rara.
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
                # Si hay campos corridos, el lector posicional YA esta leyendo
                # mal: eso es comprobable, no una sospecha.
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
    """Grupos cuyas filas vienen en bloques separados por un hueco grande.

    `posiciones` es {grupo: [numero_de_fila, ...]} con las filas que traen
    dato. Un hueco de decenas de filas no es una linea en blanco de adorno:
    es otro bloque, y hay que mirarlo antes de sumarlo al total.
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
    """Filas que traen SOLO el primer campo, en medio de una tabla con datos.

    `filas` es {grupo: [(numero, [celda, ...]), ...]}. Una fila asi no es un
    dato incompleto: es un titulo. En el corpus marcaba donde empezaba otra
    jornada dentro de la misma hoja, asi que ademas de sumar una muestra
    inexistente escondia un evento entero.
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
        # Solo cuenta si hay datos DESPUES: un rotulo al final es una nota.
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
    """Grupos cuyo contenido ya esta casi entero dentro de otro grupo.

    `contenidos` es {grupo: {contenido_comparable, ...}}. Complementa a
    `tramos_ajenos`, que exige un tramo CONTIGUO: cuando la copia fue editada,
    las coincidencias quedan intercaladas y ningun tramo llega al minimo, pero
    el conjunto sigue estando repetido casi completo.
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
            # El mas chico es la copia; a igual tamano, el que lo dice.
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
    """`Copy of X` / `Copia de X` se declara copia en su propio nombre."""
    ka, kb = _clave(a), _clave(b)
    return (ka.startswith(("copy_of", "copia_de")) and not
            kb.startswith(("copy_of", "copia_de")))


def analizar_estructura(encabezados: dict[str, list] | None = None,
                        posiciones: dict[str, list[int]] | None = None,
                        filas: dict[str, list[tuple[int, list]]] | None = None,
                        contenidos: dict[str, set] | None = None) -> list[Hallazgo]:
    """Corre los cuatro detectores con lo que se le haya dado.

    Cada argumento es opcional: un area que solo tenga los encabezados puede
    correr solo ese. El orden de salida pone primero lo que invalida mas
    lectura -- una columna corrida arruina todas las filas de su grupo.
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
