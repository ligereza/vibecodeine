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
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
MAPA = RAIZ / "MAPA.md"
GENERADOR = RAIZ / "tools" / "gen_mapa_comandos.py"

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


def test_el_manifiesto_no_queda_desfasado_del_cli():
    """The same `--check` that keeps MAPA.md honest also covers the manifest.

    It lives here, and not in `tests/test_comandos_manifiesto.py`, since
    2026-09-02. The generator emits MAPA.md and `context/comandos.json` from
    the SAME tree, so one ratchet covers both. Ownership: `--check` spawns
    `python -m flujo --help`, and the CLI imports typer, declared only in
    `requirements-flujo.txt`. Measured in run 33670334244's install step:
    rich, pydantic and requests do reach the MAK profile transitively, and
    typer does not, so typer alone is the missing import. This file is
    declared
    `integration` -- the lane that composes both physical checkouts and
    installs `requirements-integration.txt` -- while the other file is
    `repo_hygiene`, a lane the MAK profile runs without the motor's CLI stack.
    There the check failed for an environment reason while passing on the box,
    and the classifier could not see it because the dependency goes through
    `subprocess`. A manifest nobody checks is documentation, and documentation
    rots: hence moved, not disabled.
    """
    r = subprocess.run([sys.executable, str(GENERADOR), "--check"],
                       capture_output=True, text=True, encoding="utf-8",
                       cwd=str(RAIZ), timeout=300)
    assert r.returncode == 0, (
        "context/comandos.json quedo desfasado del CLI real. "
        "Corre: py tools/gen_mapa_comandos.py\n" + r.stdout + r.stderr)


def test_el_mapa_conserva_los_marcadores_del_generador():
    texto = _mapa()
    for marca in ("<!-- COMANDOS:INICIO", "<!-- COMANDOS:FIN -->"):
        assert marca in texto, (
            f"MAPA.md perdio el marcador {marca}: sin el, "
            "tools/gen_mapa_comandos.py no puede regenerar la tabla y el mapa "
            "vuelve a ser prosa escrita a mano que envejece sola."
        )


# ---------------------------------------------------------------------------
# The documentation rule reached only src/flujo
# ---------------------------------------------------------------------------
#
# test_toda_variable_de_entorno_esta_documentada scans _env_leidas(), which
# walks ONLY src/flujo. Every variable read in cultura/ or tools/ escaped the
# rule entirely -- and cultura/ is where the Hub, Research and Codex live.
# Measured on 2026-08-21: 82 undocumented variables outside src/flujo, found the
# moment MAK_BLENDER was added to src/ and the narrower gate finally noticed it.
#
# Documenting 82 entries in one commit is not verification, and a gate that
# cannot pass gets disabled instead of obeyed. So the wider zones are held by a
# pin that may only shrink, the same shape the language ratchet already uses.


def _env_tool():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "env_baseline", RAIZ / "tools" / "env_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ninguna_variable_nueva_fuera_de_src_queda_sin_documentar():
    """The ratchet: the pin may shrink, never grow."""
    tool = _env_tool()
    pinned = tool.read_pin()
    assert pinned, (
        "el pin de variables sin documentar quedo vacio: o se documentaron las "
        "82 (celebremos y borremos este test) o el archivo se perdio y el "
        "ratchet dejo de medir")
    nuevas = sorted(set(tool.undocumented()) - pinned)
    assert not nuevas, (
        "variables de entorno nuevas leidas fuera de src/flujo y sin documentar "
        "en MAPA.md seccion 4: " + ", ".join(nuevas)
        + ". Documentalas, o si de verdad no son configurables agregalas a "
        "NOT_CONFIGURABLE en tools/env_baseline.py")


def test_el_pin_no_conserva_variables_ya_documentadas():
    """A pin that keeps solved entries stops measuring the real debt."""
    tool = _env_tool()
    resueltas = sorted(tool.read_pin() - set(tool.undocumented()))
    assert not resueltas, (
        "estas variables ya estan documentadas en MAPA.md pero siguen en el "
        "pin: bajalo con `python3 tools/env_baseline.py --write`. "
        + ", ".join(resueltas))


def test_el_escaneo_ancho_cubre_de_verdad_cultura_y_tools():
    """Guard against the scan silently narrowing back to nothing."""
    tool = _env_tool()
    encontradas = tool.scan()
    assert len(encontradas) > 50, (
        f"el escaneo ancho solo vio {len(encontradas)} variables: si cultura/ o "
        "tools/ se mueven, este ratchet pasa sin medir nada")
    assert "OLLAMA_BASE_URL" in encontradas, (
        "una variable conocida de cultura/ dejo de verse: el escaneo se angosto")
