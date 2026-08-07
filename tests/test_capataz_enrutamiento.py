#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The routing defect that produced 4,275 lines nobody runs.

Traced to `capataz.py`: the LLM picks the action `codificar` and writes requests
shaped like OPERATIONS -- "actualizar /etc/mak/ajustes_junta.json", "ejecutar
backlog_codex take 4", "implementar los cambios de la ultima decision". Those
enter a channel whose contract is a self-contained stdlib file that is NEVER
executed.

An operations request cannot be satisfied by a file nobody runs. So the coder,
forced to answer, writes the only thing it can: a script that WOULD do it if
someone ran it, inventing paths (`/etc/mak/` instead of `~/plataforma/`) and CLIs
it has no way to verify. None of it is hallucination or garbage -- it is an ops
action routed into a code generator.

The fixture is not invented: these are the REAL 32 requests, taken from the file
names in `cultura/mak_plataforma/utilidades/`, which is what the channel wrote
them as.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CAPATAZ = REPO / "cultura" / "mak_plataforma" / "capataz.py"
UTILIDADES = REPO / "cultura" / "mak_plataforma" / "utilidades"


def _capataz():
    spec = importlib.util.spec_from_file_location("capataz_mod", CAPATAZ)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Requests the channel CANNOT satisfy: they ask to act on the machine.
DE_OPERACIONES = [
    "actualizar /etc/mak/ajustes_junta.json con el nuevo umbral",
    "ejecutar /usr/local/bin/backlog_codex take 4 parallel 2",
    "implementar los cambios de la ultima decision de la junta",
    "procesar 4 tareas pendientes del backlog",
    "run backlog_codex take 4 parallel 2 provider cerebras",
    "reiniciar el servicio mak-hub",
]

# Requests it CAN satisfy: they describe an artifact, not an act.
DE_ARTEFACTO = [
    "una utilidad stdlib que lea un jobs.json y resuma su estado",
    "un formateador stdlib que tome un informe y lo deje en markdown",
    "escribe una funcion stdlib python que valide un esquema",
    "un visor stdlib que lea logs red.jsonl y muestre los cortes",
    "una utilidad stdlib que convierta un csv en jsonl",
]


@pytest.mark.parametrize("pedido", DE_OPERACIONES)
def test_un_pedido_de_operaciones_se_rechaza_con_su_motivo(pedido):
    motivo = _capataz().pedido_de_operaciones(pedido)
    assert motivo, "paso un pedido de operaciones: %r" % pedido
    assert isinstance(motivo, str) and motivo.strip()


@pytest.mark.parametrize("pedido", DE_ARTEFACTO)
def test_un_pedido_de_artefacto_pasa(pedido):
    assert _capataz().pedido_de_operaciones(pedido) is None, (
        "se rechazo un pedido que el canal SI puede cumplir: %r" % pedido)


def test_calibrado_contra_los_pedidos_reales_que_lo_causaron():
    """La medicion, no la intuicion.

    Los 32 nombres de `utilidades/` SON los pedidos. El detector tiene que
    partirlos en dos grupos y no en cualquier proporcion: si rechazara todo,
    el organo dejaria de producir utilidades legitimas; si no rechazara nada,
    no serviria de nada. Medido el 2026-07-30: 12 de operaciones, 20 de
    artefacto.
    """
    if not UTILIDADES.is_dir():
        pytest.skip("sin utilidades/ en este checkout")
    cap = _capataz()
    nombres = [p.stem.replace("-", " ") for p in sorted(UTILIDADES.glob("*.py"))]
    if not nombres:
        pytest.skip("utilidades/ vacio")
    rechazados = [n for n in nombres if cap.pedido_de_operaciones(n)]
    assert rechazados, "no detecto ninguno de los pedidos que causaron el defecto"
    assert len(rechazados) < len(nombres), (
        "rechazo TODOS: el canal dejaria de producir utilidades legitimas")
    # Check only operation verbs represented by the current checkout. Utility
    # files are historical evidence and may have been pruned after calibration.
    verbos_presentes = tuple(verbo for verbo in
                             ("actualizar", "ejecutar", "implementar")
                             if any(n.startswith(verbo) for n in nombres))
    for verbo in verbos_presentes:
        assert any(n.startswith(verbo) for n in rechazados), (
            "dejo pasar los pedidos que empiezan con %r" % verbo)


def test_el_menu_no_promete_operaciones_que_no_puede_cumplir():
    """La otra mitad del arreglo: hoy el unico verbo operativo del menu es
    `mantener`, y es dry-run. Mientras no exista uno real para "cambiar un
    ajuste en la caja", el menu no debe sugerir que `codificar` lo hace."""
    texto = CAPATAZ.read_text(encoding="utf-8")
    inicio = texto.index("MENU_TXT")
    menu = texto[inicio:texto.index("\n\n", inicio)]
    linea = [ln for ln in menu.splitlines() if "codificar:" in ln]
    assert linea, "el menu ya no describe `codificar`"
    assert "pieza de codigo" in linea[0], (
        "la descripcion de `codificar` dejo de decir que produce una PIEZA: si "
        "promete accion, el modelo le mandara operaciones")
