#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codex_manager.py - Gestor de tareas Codex
Actualiza configuración, reintenta tareas fallidas y revisa automáticamente tareas de baja complejidad.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ----------------------------------------------------------------------
# Constantes y rutas
# ----------------------------------------------------------------------
CONFIG_FILE = "ajustes_junta.json"
TASKS_FILE = "tareas_codex.json"

CONFIG_DEFAULT = {
    "codex": {
        "providers": {
            "primary": "groq",
            "secondary": "ollama",
            "max_retries": 2,
            "retry_delay_s": 60,
            "auto_review_confidence": 0.85
        }
    }
}

# ----------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------
def _cargar_tareas() -> list:
    """Carga la lista de tareas desde el archivo JSON."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _guardar_tareas(tareas: list) -> None:
    """Guarda la lista de tareas en el archivo JSON."""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=2, ensure_ascii=False)

def _cargar_config() -> dict:
    """Carga la configuración desde el archivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        return CONFIG_DEFAULT.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _guardar_config(config: dict) -> None:
    """Guarda la configuración en el archivo JSON."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# ----------------------------------------------------------------------
# Funciones principales
# ----------------------------------------------------------------------
def update_config() -> None:
    """
    Actualiza el archivo ajustes_junta.json con los ajustes proporcionados.
    En esta implementación se escribe la configuración por defecto.
    """
    _guardar_config(CONFIG_DEFAULT)
    print("Configuración actualizada correctamente.")

def retry_tasks() -> None:
    """
    Selecciona hasta 10 tareas con estado 'failed' o 'pending_generate',
    re-encola usando routing (simulado) y actualiza el contador de reintentos.
    """
    config = _cargar_config()
    max_retries = config["codex"]["providers"]["max_retries"]
    tareas = _cargar_tareas()
    candidatos = [t for t in tareas if t.get("estado") in ("failed", "pending_generate")]
    # Ordenar por prioridad (opcional) y limitar a 10
    candidatos.sort(key=lambda t: t.get("prioridad", 0), reverse=True)
    seleccionados = candidatos[:10]

    for tarea in seleccionados:
        # Simular re-encolado: cambiar estado a 'pending' y decrementar reintentos
        tarea["estado"] = "pending"
        reintentos = tarea.get("reintentos", max_retries)
        if reintentos > 0:
            tarea["reintentos"] = reintentos - 1
        else:
            # Si ya no quedan reintentos, se marca como 'failed_permanent'
            tarea["estado"] = "failed_permanent"
        # Simular routing: asignar proveedor alternativo si es necesario
        if tarea.get("proveedor") == config["codex"]["providers"]["primary"]:
            tarea["proveedor"] = config["codex"]["providers"]["secondary"]
        else:
            tarea["proveedor"] = config["codex"]["providers"]["primary"]

    _guardar_tareas(tareas)
    print(f"Reintentos ejecutados para {len(seleccionados)} tareas.")

def autoreview_tasks() -> None:
    """
    Selecciona hasta 10 tareas con etiqueta 'low_complexity',
    ejecuta pipeline de mejora (simulado) y actualiza el estado de la tarea.
    """
    config = _cargar_config()
    confianza_minima = config["codex"]["providers"]["auto_review_confidence"]
    tareas = _cargar_tareas()
    candidatos = [t for t in tareas if "low_complexity" in t.get("etiquetas", [])]
    candidatos.sort(key=lambda t: t.get("prioridad", 0), reverse=True)
    seleccionados = candidatos[:10]

    for tarea in seleccionados:
        # Simular pipeline de mejora: generar una puntuación aleatoria
        import random
        puntuacion = random.uniform(0.0, 1.0)
        if puntuacion >= confianza_minima:
            tarea["estado"] = "approved"
            tarea["revision_automatica"] = True
            tarea["puntuacion"] = round(puntuacion, 4)
        else:
            tarea["estado"] = "needs_review"
            tarea["revision_automatica"] = False
            tarea["puntuacion"] = round(puntuacion, 4)

    _guardar_tareas(tareas)
    print(f"Revisión automática completada para {len(seleccionados)} tareas.")

# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Gestor de tareas Codex")
    parser.add_argument("--update-config", action="store_true", help="Actualizar configuración")
    parser.add_argument("--retry-tasks", action="store_true", help="Reintentar tareas fallidas")
    parser.add_argument("--autoreview-tasks", action="store_true", help="Revisar automáticamente tareas de baja complejidad")
    args = parser.parse_args()

    if args.update_config:
        update_config()
    elif args.retry_tasks:
        retry_tasks()
    elif args.autoreview_tasks:
        autoreview_tasks()
    else:
        parser.print_help()

# ----------------------------------------------------------------------
# Casos de prueba (autoverificación)
# ----------------------------------------------------------------------
def _test_update_config() -> None:
    """Caso 1: Actualización de configuración."""
    # Preparar: eliminar archivo si existe
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    update_config()
    assert os.path.exists(CONFIG_FILE), "El archivo de configuración no se creó"
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    assert data == CONFIG_DEFAULT, "El contenido de configuración no coincide"
    print("Caso 1 OK: update_config")

def _test_retry_tasks() -> None:
    """Caso 2: Reintentos de tareas."""
    # Preparar tareas de prueba
    tareas_prueba = [
        {"id": 1, "estado": "failed", "reintentos": 2, "proveedor": "groq", "prioridad": 5},
        {"id": 2, "estado": "pending_generate", "reintentos": 1, "proveedor": "ollama", "prioridad": 3},
        {"id": 3, "estado": "completed", "reintentos": 0, "proveedor": "groq", "prioridad": 1},
        {"id": 4, "estado": "failed", "reintentos": 0, "proveedor": "groq", "prioridad": 2},
    ]
    _guardar_tareas(tareas_prueba)
    retry_tasks()
    tareas_actualizadas = _cargar_tareas()
    # Verificar que las tareas 1 y 2 se procesaron
    t1 = next(t for t in tareas_actualizadas if t["id"] == 1)
    assert t1["estado"] == "pending", f"Tarea 1 debería estar pending, está {t1['estado']}"
    assert t1["reintentos"] == 1, f"Tarea 1 reintentos debería ser 1, es {t1['reintentos']}"
    t2 = next(t for t in tareas_actualizadas if t["id"] == 2)
    assert t2["estado"] == "pending", f"Tarea 2 debería estar pending, está {t2['estado']}"
    assert t2["reintentos"] == 0, f"Tarea 2 reintentos debería ser 0, es {t2['reintentos']}"
    # Tarea 4 con reintentos 0 debería pasar a failed_permanent
    t4 = next(t for t in tareas_actualizadas if t["id"] == 4)
    assert t4["estado"] == "failed_permanent", f"Tarea 4 debería ser failed_permanent, es {t4['estado']}"
    print("Caso 2 OK: retry_tasks")

def _test_autoreview_tasks() -> None:
    """Caso 3: Revisión automática de tareas."""
    # Preparar tareas de prueba
    tareas_prueba = [
        {"id": 10, "estado": "pending", "etiquetas": ["low_complexity"], "prioridad": 5},
        {"id": 11, "estado": "pending", "etiquetas": ["high_complexity"], "prioridad": 3},
        {"id": 12, "estado": "pending", "etiquetas": ["low_complexity", "urgent"], "prioridad": 4},
    ]
    _guardar_tareas(tareas_prueba)
    autoreview_tasks()
    tareas_actualizadas = _cargar_tareas()
    # Verificar que las tareas con low_complexity se procesaron
    t10 = next(t for t in tareas_actualizadas if t["id"] == 10)
    assert t10["estado"] in ("approved", "needs_review"), f"Tarea 10 estado inesperado: {t10['estado']}"
    assert "puntuacion" in t10, "Tarea 10 debería tener puntuacion"
    t12 = next(t for t in tareas_actualizadas if t["id"] == 12)
    assert t12["estado"] in ("approved", "needs_review"), f"Tarea 12 estado inesperado: {t12['estado']}"
    # Tarea 11 no debería haber cambiado
    t11 = next(t for t in tareas_actualizadas if t["id"] == 11)
    assert t11["estado"] == "pending", "Tarea 11 no debería haber sido revisada"
    print("Caso 3 OK: autoreview_tasks")

def run_tests() -> None:
    """Ejecuta todos los casos de prueba."""
    # Limpiar archivos de prueba previos
    for f in [CONFIG_FILE, TASKS_FILE]:
        if os.path.exists(f):
            os.remove(f)
    _test_update_config()
    _test_retry_tasks()
    _test_autoreview_tasks()
    # Limpiar después de pruebas
    for f in [CONFIG_FILE, TASKS_FILE]:
        if os.path.exists(f):
            os.remove(f)
    print("\nPRUEBAS OK")

# ----------------------------------------------------------------------
# Punto de entrada
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        # Sin argumentos: ejecutar pruebas
        run_tests()
