"""Tests para metricas_capataz.py -- fixture sintetica + asserts de tasas."""
from __future__ import annotations

import datetime
import json
import tempfile
from pathlib import Path

import pytest

from cultura.mak_plataforma.metricas_capataz import (
    cargar_bitacora,
    render_md,
    tasas,
)


@pytest.fixture
def bitacora_sintetica(tmp_path: Path) -> Path:
    """Crea un archivo bitacora_capataz.jsonl sintetico con 10 entradas variadas.

    - 7 exitosas (fallback=False)
    - 3 con fallback (fallback=True)
    - 1 linea corrupta (JSON invalido, debe saltarse)
    - Entrada con accion/proveedor variados
    """
    bitacora_file = tmp_path / "bitacora_capataz.jsonl"

    # Timestamp base (hoy)
    base_ts = datetime.datetime.now()
    entries = [
        # Exitosas con cerebras
        {
            "ts": (base_ts - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "cerebras",
            "accion": "investigar",
            "razon": "backlog investigacion pendiente",
            "fallback_usado": False,
            "resultado_resumen": "http 200 ok",
            "estado_previo": {
                "backlog": {"investigacion": 5},
                "prs_abiertos": {"total_abiertos": 2, "capataz_abiertos": 1},
                "producidos_hoy": 1,
            },
        },
        # Fallback con groq
        {
            "ts": (base_ts - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "groq",
            "accion": "vetear",
            "razon": "fallback (accion invalida o ausente) -- crudo del modelo: {...}",
            "fallback_usado": True,
            "resultado_resumen": "rc=0",
            "estado_previo": {"backlog": {}, "prs_abiertos": {}, "producidos_hoy": 0},
        },
        # Exitosa codificar
        {
            "ts": (base_ts - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "cerebras",
            "accion": "codificar",
            "razon": "backlog codex listo",
            "fallback_usado": False,
            "resultado_resumen": "http 200 ok",
            "estado_previo": {"backlog": {"codex": 3}, "prs_abiertos": {}, "producidos_hoy": 0},
        },
        # Fallback LLM caido
        {
            "ts": (base_ts - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "ninguno",
            "accion": "vetear",
            "razon": "cerebro caido: Connection timeout",
            "fallback_usado": True,
            "resultado_resumen": "rc=0",
            "estado_previo": {},
        },
        # Reflexionar exitosa
        {
            "ts": (base_ts - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "azure",
            "accion": "reflexionar",
            "razon": "junta diaria programada",
            "fallback_usado": False,
            "resultado_resumen": "rc=0",
            "estado_previo": {"backlog": {}, "prs_abiertos": {}, "producidos_hoy": 2},
        },
        # Vigilar proveedores
        {
            "ts": (base_ts - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "cerebras",
            "accion": "vigilar_proveedores",
            "razon": "check salud LLM",
            "fallback_usado": False,
            "resultado_resumen": "groq rate-limited, expulsando",
            "estado_previo": {},
        },
        # Entregar
        {
            "ts": (base_ts - datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "groq",
            "accion": "entregar",
            "razon": "PR codex lista",
            "fallback_usado": False,
            "resultado_resumen": "rc=0",
            "estado_previo": {"backlog": {}, "prs_abiertos": {}, "producidos_hoy": 1},
        },
        # Mejora libre
        {
            "ts": (base_ts - datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "azure",
            "accion": "mejora_libre",
            "razon": "agente_libre propone refactoring",
            "fallback_usado": False,
            "resultado_resumen": "rc=0",
            "estado_previo": {},
        },
        # Descansar (raro)
        {
            "ts": (base_ts - datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "cerebras",
            "accion": "descansar",
            "razon": "sin backlog, sin PRs, sistema estable",
            "fallback_usado": False,
            "resultado_resumen": "ok (no-op)",
            "estado_previo": {},
        },
        # Entrada sin resultado_resumen (parse incompleto)
        {
            "ts": (base_ts - datetime.timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "proveedor_decisor": "ollama",
            "accion": "investigar",
            "razon": "fallback modelo local",
            "fallback_usado": True,
            # Sin resultado_resumen
            "estado_previo": {},
        },
    ]

    # Escribir entradas validas
    with bitacora_file.open("w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Agregar linea corrupta (debe saltarse)
        f.write("{ corrupted json no cierra bien\n")

    return bitacora_file


def test_cargar_bitacora_basico(bitacora_sintetica: Path) -> None:
    """Verifica que cargar_bitacora lee entradas validas."""
    entradas = cargar_bitacora(str(bitacora_sintetica), dias=7)
    # Debe tener 10 entradas (la linea corrupta se salta)
    assert len(entradas) == 10
    assert all(isinstance(e, dict) for e in entradas)


def test_cargar_bitacora_filtro_dias(bitacora_sintetica: Path) -> None:
    """Verifica que el filtro de dias funciona."""
    # Con dias=1, deberia incluir solo entradas del ultimo dia
    entradas_hoy = cargar_bitacora(str(bitacora_sintetica), dias=1)
    # Todas son de hoy en nuestra fixture
    assert len(entradas_hoy) >= 8  # Allow some slack

    # Con dias=100, deberia incluir todo
    entradas_100 = cargar_bitacora(str(bitacora_sintetica), dias=100)
    assert len(entradas_100) == 10


def test_cargar_bitacora_no_existe() -> None:
    """Verifica que archivo inexistente devuelve lista vacia."""
    entradas = cargar_bitacora("/ruta/inexistente/bitacora.jsonl", dias=7)
    assert entradas == []


def test_tasas_basico(bitacora_sintetica: Path) -> None:
    """Verifica que tasas() calcula correctamente metricas."""
    entradas = cargar_bitacora(str(bitacora_sintetica), dias=7)
    t = tasas(entradas)

    # Total debe ser 10
    assert t["total"] == 10

    # Fallback rate: 3 fallback de 10 = 30%
    assert t["fallback_rate"] == 30.0

    # Parse OK: 9 de 10 tienen resultado_resumen (1 sin el campo)
    assert t["parse_ok_rate"] == 90.0


def test_tasas_por_proveedor(bitacora_sintetica: Path) -> None:
    """Verifica distribucion por proveedor."""
    entradas = cargar_bitacora(str(bitacora_sintetica), dias=7)
    t = tasas(entradas)

    por_prov = t["por_proveedor"]

    # Debe tener cerebras, groq, azure, ninguno, ollama
    assert "cerebras" in por_prov
    assert "groq" in por_prov
    assert "azure" in por_prov
    assert "ninguno" in por_prov
    assert "ollama" in por_prov

    # Cerebras: 4 entradas (investigar, codificar, vigilar, descansar)
    # De las cuales 0 con fallback
    assert por_prov["cerebras"]["n"] == 4
    assert por_prov["cerebras"]["fallback_n"] == 0
    assert por_prov["cerebras"]["fallback_pct"] == 0.0

    # Groq: 2 entradas (vetear fallback, entregar)
    # De las cuales 1 con fallback
    assert por_prov["groq"]["n"] == 2
    assert por_prov["groq"]["fallback_n"] == 1
    assert por_prov["groq"]["fallback_pct"] == 50.0

    # Azure: 2 entradas (reflexionar, mejora_libre), 0 fallback
    assert por_prov["azure"]["n"] == 2
    assert por_prov["azure"]["fallback_n"] == 0

    # Ninguno: 1 entrada (fallback LLM caido)
    assert por_prov["ninguno"]["n"] == 1
    assert por_prov["ninguno"]["fallback_n"] == 1

    # Ollama: 1 entrada, fallback
    assert por_prov["ollama"]["n"] == 1
    assert por_prov["ollama"]["fallback_n"] == 1


def test_tasas_por_accion(bitacora_sintetica: Path) -> None:
    """Verifica distribucion por accion."""
    entradas = cargar_bitacora(str(bitacora_sintetica), dias=7)
    t = tasas(entradas)

    por_accion = t["por_accion"]

    # investigar: 2 entradas (cerebras exitosa, ollama fallback)
    assert por_accion["investigar"]["n"] == 2
    assert por_accion["investigar"]["fallback_n"] == 1
    assert por_accion["investigar"]["fallback_pct"] == 50.0

    # codificar: 1 (cerebras exitosa)
    assert por_accion["codificar"]["n"] == 1
    assert por_accion["codificar"]["fallback_n"] == 0

    # vetear: 2 (groq fallback, ninguno fallback)
    assert por_accion["vetear"]["n"] == 2
    assert por_accion["vetear"]["fallback_n"] == 2
    assert por_accion["vetear"]["fallback_pct"] == 100.0

    # reflexionar, vigilar_proveedores, entregar, mejora_libre, descansar
    # todas exitosas
    assert por_accion["reflexionar"]["fallback_pct"] == 0.0
    assert por_accion["vigilar_proveedores"]["fallback_pct"] == 0.0
    assert por_accion["entregar"]["fallback_pct"] == 0.0
    assert por_accion["mejora_libre"]["fallback_pct"] == 0.0
    assert por_accion["descansar"]["fallback_pct"] == 0.0


def test_tasas_vacio() -> None:
    """Verifica que tasas() maneja lista vacia."""
    t = tasas([])

    assert t["total"] == 0
    assert t["fallback_rate"] == 0.0
    assert t["parse_ok_rate"] == 0.0
    assert t["por_proveedor"] == {}
    assert t["por_accion"] == {}


def test_render_md_basico(bitacora_sintetica: Path) -> None:
    """Verifica que render_md() genera markdown valido."""
    entradas = cargar_bitacora(str(bitacora_sintetica), dias=7)
    t = tasas(entradas)
    md = render_md(t)

    # Debe tener headers
    assert "# Metricas del Capataz (FASE 0)" in md
    assert "## Resumen General" in md
    assert "## Decisiones por Proveedor" in md
    assert "## Decisiones por Accion" in md

    # Debe tener tablas markdown
    assert "| proveedor | decisiones | fallback_n | fallback_pct |" in md
    assert "| accion | total | fallback_n | fallback_pct |" in md

    # Debe mencionar las metricas
    assert "**Total de decisiones**: 10" in md
    assert "**Tasa de fallback**: 30.0%" in md
    assert "**Tasa parse OK**: 90.0%" in md

    # Debe tener proveedores
    assert "| cerebras |" in md
    assert "| groq |" in md


def test_render_md_vacio() -> None:
    """Verifica que render_md() maneja dict vacio."""
    t = {
        "total": 0,
        "fallback_rate": 0.0,
        "parse_ok_rate": 0.0,
        "por_proveedor": {},
        "por_accion": {},
    }
    md = render_md(t)

    # Debe tener los headers pero tablas vacias
    assert "# Metricas del Capataz (FASE 0)" in md
    assert "| — | 0 | 0 | 0% |" in md
