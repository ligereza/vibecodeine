# -*- coding: utf-8 -*-
"""Ratchet de higiene del repo (2026-07-25).

Dos reglas que evitan repetir el problema medido en la sesion de
orquestacion: el handoff crecio a 1554 lineas sin tope, y tools/ acumula
scripts sin registro de si estan vivos o muertos. Ninguna de las dos
reglas se relaja "arreglando" el archivo que la dispara con contenido
falso: se comprime/archiva (handoff) o se declara en el registro
(tools/), nunca se edita el test.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LAST_HANDOFF = REPO_ROOT / "context" / "LAST_HANDOFF.md"
CAPACIDADES = REPO_ROOT / "CAPACIDADES.md"
TOOLS_DIR = REPO_ROOT / "tools"

MAX_HANDOFF_LINES = 350


def test_handoff_dentro_del_tope():
    contenido = LAST_HANDOFF.read_text(encoding="utf-8")
    lineas = contenido.splitlines()
    assert len(lineas) <= MAX_HANDOFF_LINES, (
        "LAST_HANDOFF.md excede 350 lineas: comprimir y archivar a "
        "docs/handoffs/archive/ (regla 2026-07-25, causa: llego a 1554 "
        "lineas; retiro: cuando el handoff viva en un sistema con "
        "rotacion automatica)"
    )


def test_tools_en_registro():
    capacidades = CAPACIDADES.read_text(encoding="utf-8")
    archivos = sorted(p for p in TOOLS_DIR.glob("*.py") if p.is_file())
    faltantes = [
        p.name for p in archivos if p.name not in capacidades
    ]
    assert not faltantes, (
        "tools/<x>.py sin entrada en registro VIVO/MUERTO de "
        "CAPACIDADES.md: toda herramienta declara consumidor o no entra "
        "(regla 2026-07-25). Faltan: " + ", ".join(faltantes)
    )


# Configuracion que el usuario edita a mano y que el codigo declara "fuente
# unica". Si un archivo asi no viaja en el repo, el codigo cae a su respaldo
# interno y NADIE se entera salvo por una linea en stderr.
CONFIG_DEL_USUARIO = (
    "data/rd_packs.json",
    "data/plano_simbolos.json",
    "data/cotizacion_servicios.json",
    "data/svg_estados.json",
)


def test_config_del_usuario_versionada():
    """Regresion medida: `data/rd_packs.json` se declaro fuente unica de la
    tarifa RD el 2026-07-26 y quedo fuera del repo, porque .gitignore ignora
    `data/*.json`. En cualquier otro checkout el rider cotizaba con la copia de
    respaldo del codigo. Un archivo de configuracion que no viaja no es una
    fuente de verdad."""
    import subprocess

    salida = subprocess.run(
        ["git", "ls-files", "--", *CONFIG_DEL_USUARIO],
        cwd=REPO_ROOT, capture_output=True, encoding="utf-8", errors="replace",
    )
    if salida.returncode != 0:  # sin git disponible no hay nada que medir
        return
    versionados = set(salida.stdout.split())
    faltantes = [p for p in CONFIG_DEL_USUARIO if p not in versionados]
    assert not faltantes, (
        "config editable por el usuario fuera del repo (revisa .gitignore, "
        "necesita una linea `!<ruta>`): " + ", ".join(faltantes)
    )
