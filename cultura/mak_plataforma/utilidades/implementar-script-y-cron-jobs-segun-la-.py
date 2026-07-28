#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_automation.py – Módulo principal de automatización Codex.
Solo utiliza la biblioteca estándar de Python 3.11.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS: Dict[str, Any] = {
    "codex.providers": {
        "primary": "groq",
        "secondary": "ollama",
        "max_retries": 2,
        "retry_delay_s": 60,
        "auto_review_confidence": 0.85,
    }
}

SETTINGS_FILE = "ajustes_junta.json"

# ---------------------------------------------------------------------------
# Colas simuladas (para pruebas y ejecución en memoria)
# ---------------------------------------------------------------------------
_QUEUE: List[Dict[str, Any]] = []
_REVIEWS: List[Dict[str, Any]] = []

# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _cargar_ajustes() -> Dict[str, Any]:
    """Carga los ajustes desde el archivo JSON. Si no existe, crea los por defecto."""
    if not os.path.exists(SETTINGS_FILE):
        _guardar_ajustes(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_ajustes(settings: Dict[str, Any]) -> None:
    """Guarda los ajustes en el archivo JSON."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Comandos CLI
# ---------------------------------------------------------------------------

def update_settings() -> None:
    """Genera o actualiza el archivo de ajustes con los valores por defecto."""
    _guardar_ajustes(DEFAULT_SETTINGS)
    print(f"Ajustes guardados en {SETTINGS_FILE}")


def run_retry(limit: int = 10) -> None:
    """
    Procesa hasta `limit` tareas de la cola global _QUEUE cuyo estado sea
    'failed' o 'pending_generate'. Aplica routing 80% primary / 20% secondary,
    decrementa max_retries y actualiza retry_delay_s en el payload.
    """
    settings = _cargar_ajustes()
    providers = settings["codex.providers"]
    primary = providers["primary"]
    secondary = providers["secondary"]
    max_retries = providers["max_retries"]
    retry_delay_s = providers["retry_delay_s"]

    # Filtrar tareas elegibles
    elegibles = [t for t in _QUEUE if t.get("status") in ("failed", "pending_generate")]
    # Tomar hasta limit
    a_procesar = elegibles[:limit]

    for idx, tarea in enumerate(a_procesar):
        # Routing: 80% primary, 20% secondary
        if idx % 10 < 8:  # 0-7 -> primary, 8-9 -> secondary
            tarea["provider"] = primary
        else:
            tarea["provider"] = secondary

        # Decrementar max_retries (si existe, sino inicializar)
        tarea["retries"] = tarea.get("retries", 0) + 1
        # Actualizar retry_delay_s
        tarea["retry_delay_s"] = retry_delay_s

        # Opcional: cambiar estado a algo como "pending_retry" (no especificado)
        tarea["status"] = "pending_retry"

    print(f"run_retry: procesadas {len(a_procesar)} tareas.")


def run_autoreview(limit: int = 10) -> None:
    """
    Procesa hasta `limit` revisiones de la cola global _REVIEWS con complexity
    'low_complexity'. Si confidence >= auto_review_confidence, marca 'ready';
    de lo contrario 'manual_review_needed'.
    """
    settings = _cargar_ajustes()
    threshold = settings["codex.providers"]["auto_review_confidence"]

    elegibles = [r for r in _REVIEWS if r.get("complexity") == "low_complexity"]
    a_procesar = elegibles[:limit]

    for revision in a_procesar:
        if revision.get("confidence", 0.0) >= threshold:
            revision["status"] = "ready"
        else:
            revision["status"] = "manual_review_needed"

    print(f"run_autoreview: procesadas {len(a_procesar)} revisiones.")


def run_all() -> None:
    """Ejecuta run_retry y run_autoreview en una sola pasada."""
    run_retry()
    run_autoreview()


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def _cli() -> None:
    if len(sys.argv) < 2:
        print("Uso: python codex_automation.py <subcomando> [args]")
        print("Subcomandos: update_settings, run_retry, run_autoreview, run_all")
        sys.exit(1)

    subcomando = sys.argv[1]
    # Parsear límite opcional (para run_retry y run_autoreview)
    limit = 10
    if len(sys.argv) >= 3:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print(f"Error: el argumento debe ser un número entero, se recibió '{sys.argv[2]}'")
            sys.exit(1)

    if subcomando == "update_settings":
        update_settings()
    elif subcomando == "run_retry":
        run_retry(limit)
    elif subcomando == "run_autoreview":
        run_autoreview(limit)
    elif subcomando == "run_all":
        run_all()
    else:
        print(f"Subcomando desconocido: {subcomando}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pruebas autoverificadas
# ---------------------------------------------------------------------------

def _test_update_settings() -> None:
    """1️⃣ Test: update_settings crea el JSON correcto."""
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)
    update_settings()
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == DEFAULT_SETTINGS, f"Esperado {DEFAULT_SETTINGS}, obtenido {data}"
    # Limpiar
    os.remove(SETTINGS_FILE)


def _test_run_retry() -> None:
    """2️⃣ Test: run_retry procesa sólo 10 tareas y respeta routing."""
    global _QUEUE
    _QUEUE = [
        {"id": i, "status": "failed", "provider": None, "retries": 0}
        for i in range(15)
    ]
    # Asegurar que existe el archivo de ajustes
    if not os.path.exists(SETTINGS_FILE):
        _guardar_ajustes(DEFAULT_SETTINGS)
    run_retry(limit=10)
    # 8 deben haber sido asignados a primary (groq), 2 a secondary (ollama)
    primary = [t for t in _QUEUE[:10] if t["provider"] == "groq"]
    secondary = [t for t in _QUEUE[:10] if t["provider"] == "ollama"]
    assert len(primary) == 8, f"Esperados 8 primary, obtenidos {len(primary)}"
    assert len(secondary) == 2, f"Esperados 2 secondary, obtenidos {len(secondary)}"
    # Cada tarea procesada debe haber incrementado retries y tener retry_delay_s
    for t in _QUEUE[:10]:
        assert t["retries"] == 1, f"Esperado retries=1, obtenido {t['retries']}"
        assert t["retry_delay_s"] == 60, f"Esperado retry_delay_s=60, obtenido {t['retry_delay_s']}"
    # Las tareas no procesadas (índices 10-14) deben quedar sin cambios
    for t in _QUEUE[10:]:
        assert t["retries"] == 0
        assert t["provider"] is None
    # Limpiar
    _QUEUE.clear()
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)


def _test_run_autoreview() -> None:
    """3️⃣ Test: run_autoreview marca ready vs manual_review_needed."""
    global _REVIEWS
    _REVIEWS = [
        {"id": i, "complexity": "low_complexity", "confidence": 0.90, "status": None}
        for i in range(5)
    ] + [
        {"id": i + 5, "complexity": "low_complexity", "confidence": 0.80, "status": None}
        for i in range(5)
    ]
    # Asegurar ajustes
    if not os.path.exists(SETTINGS_FILE):
        _guardar_ajustes(DEFAULT_SETTINGS)
    run_autoreview(limit=10)
    ready = [r for r in _REVIEWS if r["status"] == "ready"]
    manual = [r for r in _REVIEWS if r["status"] == "manual_review_needed"]
    assert len(ready) == 5, f"Esperados 5 ready, obtenidos {len(ready)}"
    assert len(manual) == 5, f"Esperados 5 manual, obtenidos {len(manual)}"
    # Limpiar
    _REVIEWS.clear()
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Modo test
        _test_update_settings()
        _test_run_retry()
        _test_run_autoreview()
        print("PRUEBAS OK")
    else:
        _cli()
