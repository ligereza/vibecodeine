# -*- coding: utf-8 -*-
"""Ratchet: MAPA.md no puede quedarse atras del programa.

Regla (2026-07-25). Causa concreta: tres auditorias externas seguidas se
equivocaron sobre lo que el repo tiene porque leyeron documentacion vieja en
vez de medir, y un agente que entra sin contexto no tiene como saber que le
estan mintiendo. MAPA.md es la puerta de entrada universal -- para una persona
que no programa y para un agente gratis -- asi que no puede omitir un comando
ni una variable de configuracion.

Que exige:
  1. Todo comando invocable del CLI aparece en MAPA.md.
  2. Toda variable de entorno que el codigo lee esta documentada en MAPA.md.

Lo que NO exige (a proposito): que la descripcion sea buena. Eso no lo puede
medir un test; para eso esta el generador tools/gen_mapa_comandos.py, que la
copia del propio --help.

Condicion de retiro: cuando MAPA.md se genere entero desde el codigo y no
quede prosa escrita a mano que pueda contradecirlo.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
MAPA = RAIZ / "MAPA.md"

# Variables que el repo lee pero que NO son configuracion del usuario: las
# pone el entorno de ejecucion, no una persona. Documentarlas confundiria.
ENV_NO_CONFIGURABLES = {
    "PATH", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP",
    "COMSPEC", "SYSTEMROOT", "PYTHONPATH", "PYTHONIOENCODING", "PYTHONUTF8",
    "VIRTUAL_ENV", "CI", "GITHUB_ACTIONS", "COLUMNS", "TERM", "NO_COLOR",
    "OLLAMA_HOST", "BLENDER", "BLENDER_EXE",
}

LECTURA_ENV = re.compile(
    r"""os\.(?:environ\.get|getenv)\(\s*["']([A-Z][A-Z0-9_]{2,})["']"""
    r"""|os\.environ\[\s*["']([A-Z][A-Z0-9_]{2,})["']\s*\]"""
)


def _mapa() -> str:
    if not MAPA.exists():
        pytest.fail("falta MAPA.md: es la puerta de entrada del repo")
    return MAPA.read_text(encoding="utf-8")


def _comandos_del_cli() -> list[str]:
    """Camina el objeto Typer real. No lanza subprocesos: es rapido y exacto."""
    from flujo.cli import app

    def caminar(a, prefijo: str = "") -> list[str]:
        nombres: list[str] = []
        for cmd in a.registered_commands:
            nombre = cmd.name or (cmd.callback.__name__.replace("_", "-")
                                  if cmd.callback else "")
            if nombre:
                nombres.append((prefijo + nombre).strip())
        for grupo in a.registered_groups:
            hijo = grupo.typer_instance
            if hijo is None:
                continue
            nombre = grupo.name or (hijo.info.name or "")
            if nombre:
                nombres += caminar(hijo, f"{prefijo}{nombre} ")
        return nombres

    return sorted(set(caminar(app)))


def _env_leidas() -> set[str]:
    encontradas: set[str] = set()
    for py in (RAIZ / "src" / "flujo").rglob("*.py"):
        try:
            texto = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for a, b in LECTURA_ENV.findall(texto):
            encontradas.add(a or b)
    return {v for v in encontradas if v not in ENV_NO_CONFIGURABLES}


def test_todo_comando_del_cli_esta_en_el_mapa():
    texto = _mapa()
    comandos = _comandos_del_cli()
    assert comandos, "no se pudo leer el arbol de comandos del CLI"

    faltan = [c for c in comandos if f"flujo {c}`" not in texto]
    assert not faltan, (
        "Comandos que existen y MAPA.md no menciona. Quien lea el mapa no se va "
        "a enterar de que existen.\n"
        "Corre: py tools/gen_mapa_comandos.py\n"
        "Faltan: " + ", ".join(faltan)
    )


def test_toda_variable_de_entorno_esta_documentada():
    texto = _mapa()
    faltan = sorted(v for v in _env_leidas() if v not in texto)
    assert not faltan, (
        "Variables de entorno que el codigo lee y MAPA.md no documenta. Quien "
        "instale el repo en otra maquina no va a saber que existen ni que pasa "
        "si no las define (seccion 4 del mapa).\n"
        "Faltan: " + ", ".join(faltan)
    )


def test_el_mapa_conserva_los_marcadores_del_generador():
    texto = _mapa()
    for marca in ("<!-- COMANDOS:INICIO", "<!-- COMANDOS:FIN -->"):
        assert marca in texto, (
            f"MAPA.md perdio el marcador {marca}: sin el, "
            "tools/gen_mapa_comandos.py no puede regenerar la tabla y el mapa "
            "vuelve a ser prosa escrita a mano que envejece sola."
        )
