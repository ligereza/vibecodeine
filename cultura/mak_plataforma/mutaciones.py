#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quien movio esto: registro append-only de mutaciones de estado.

Por que existe, medido el 2026-07-30: 217 informes aparecieron movidos a un
`archive/` creado a las 16:28:34 y NADIE pudo atribuirlo. Se descarto al
capataz (habia elegido `vetear`, y llama a mantenimiento con `execute=False`
fijo), a una corrida en seco (el codigo solo mueve bajo `--apply`), al hub (no
lo expone) y al historial de shell.

No es un misterio forense: es la consecuencia esperada de que tres lazos
autonomos, una decena de crons y sesiones SSH compartan un filesystem sin
bitacora. "Nadie fue" es el estado por defecto de un sistema sin firma.

NO es una capa nueva ni un panel que nadie mire -- ese seria el mismo defecto
que este repo ya tiene de sobra. Es una PRECONDICION dentro de las herramientas
que ya existen: quien mueva o borre estado llama a `registrar()` antes. Su
consumidor esta garantizado: la proxima vez que alguien pregunte quien hizo
esto, el archivo contesta.

    from mutaciones import registrar
    registrar("archivar", "217 pares -> informes/archive", origen=__file__)
"""
from __future__ import annotations

import json
import os
import sys
import time

RUTA = os.path.join(os.path.expanduser("~"), "plataforma", "mutaciones.log")


def registrar(accion: str, detalle: str = "", origen: str | None = None,
              ruta: str | None = None) -> bool:
    """Anota una mutacion de estado. Devuelve True si quedo escrita.

    Nunca lanza: un registro que tumba al proceso que registra seria peor que
    no tener registro. Si falla, devuelve False y el llamador sigue.
    """
    linea = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "accion": accion,
        "detalle": detalle[:400],
        "origen": os.path.basename(origen or (sys.argv[0] or "?")),
        "pid": os.getpid(),
        "argv": " ".join(sys.argv[1:])[:200],
    }
    destino = ruta or RUTA
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "a", encoding="utf-8") as f:
            f.write(json.dumps(linea, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False


def leer(n: int = 20, ruta: str | None = None) -> list:
    """Las ultimas n mutaciones, mas nuevas primero. Para contestar la pregunta
    que hoy no se pudo contestar."""
    destino = ruta or RUTA
    try:
        with open(destino, encoding="utf-8") as f:
            lineas = f.readlines()[-n:]
    except OSError:
        return []
    salida = []
    for l in reversed(lineas):
        try:
            salida.append(json.loads(l))
        except ValueError:
            continue
    return salida


if __name__ == "__main__":
    for m in leer(int(sys.argv[1]) if len(sys.argv) > 1 else 20):
        print("%s  %-12s %-22s %s"
              % (m.get("ts"), m.get("origen"), m.get("accion"),
                 m.get("detalle", "")[:70]))
