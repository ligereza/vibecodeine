#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codex_maintenance.py - Script de mantenimiento para Codex.
Actualiza configuración, reintenta tareas fallidas y revisa tareas de baja complejidad.
Solo utiliza biblioteca estándar de Python ≥3.9.
"""

import json
import logging
import os
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("codex_maintenance")


def update_config(path: Path = Path("ajustes_junta.json")) -> None:
    """
    Actualiza el archivo de configuración con la nueva sección codex.providers.
    Si el archivo no existe, lo crea con la estructura completa.
    """
    providers_config = {
        "primary": "groq",
        "secondary": "ollama",
        "max_retries": 2,
        "retry_delay_s": 60,
        "auto_review_confidence": 0.85,
    }

    # Leer configuración existente o empezar con un diccionario vacío
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}

    # Asegurar que exista la clave "codex"
    if "codex" not in config:
        config["codex"] = {}
    config["codex"]["providers"] = providers_config

    # Escribir de vuelta
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    logger.info("Configuración actualizada en %s", path)


def retry_tasks(limit: int = 10, path: Path = Path("backlog_codex.json")) -> List[Dict[str, Any]]:
    """
    Lee el backlog, selecciona hasta `limit` tareas con estado 'failed' o 'pending_generate',
    asigna proveedor (80% primary, 20% secondary), decrementa retries_left,
    cambia estado a 'queued' y registra en log.
    Devuelve la lista de tareas modificadas.
    """
    if not path.exists():
        logger.warning("Archivo backlog %s no encontrado.", path)
        return []

    with open(path, "r", encoding="utf-8") as f:
        try:
            backlog = json.load(f)
        except json.JSONDecodeError:
            logger.error("Error al decodificar %s", path)
            return []

    # Filtrar tareas candidatas
    candidatas = [
        t for t in backlog
        if t.get("status") in ("failed", "pending_generate")
    ]

    # Seleccionar hasta `limit` (sin mezclar, orden original)
    seleccionadas = candidatas[:limit]
    modificadas = []

    for tarea in seleccionadas:
        # Asignar proveedor según distribución 80/20
        if random.random() < 0.8:
            tarea["provider"] = "groq"
        else:
            tarea["provider"] = "ollama"

        # Decrementar retries_left (si existe)
        retries = tarea.get("retries_left", 0)
        tarea["retries_left"] = max(retries - 1, 0)

        # Cambiar estado a queued
        tarea["status"] = "queued"

        modificadas.append(tarea)
        logger.info(
            "Tarea %d: estado -> queued, provider -> %s, retries_left -> %d",
            tarea.get("id"),
            tarea["provider"],
            tarea["retries_left"],
        )

    # Escribir backlog actualizado
    with open(path, "w", encoding="utf-8") as f:
        json.dump(backlog, f, indent=2, ensure_ascii=False)

    return modificadas


def autoreview_tasks(limit: int = 10, path: Path = Path("backlog_codex.json")) -> List[Dict[str, Any]]:
    """
    Lee el backlog, selecciona hasta `limit` ítems con estado 'revisar' y etiqueta 'low_complexity',
    ejecuta pipeline simulado (compara confidence con umbral 0.85),
    actualiza estado a 'ready' o asigna bucket 'manual_review_needed'.
    Devuelve la lista de tareas modificadas.
    """
    if not path.exists():
        logger.warning("Archivo backlog %s no encontrado.", path)
        return []

    with open(path, "r", encoding="utf-8") as f:
        try:
            backlog = json.load(f)
        except json.JSONDecodeError:
            logger.error("Error al decodificar %s", path)
            return []

    # Filtrar tareas candidatas
    candidatas = [
        t for t in backlog
        if t.get("status") == "revisar" and "low_complexity" in t.get("tags", [])
    ]

    seleccionadas = candidatas[:limit]
    modificadas = []

    umbral = 0.85

    for tarea in seleccionadas:
        confidence = tarea.get("confidence", 0.0)
        # Pipeline simulado: no se modifica confidence, solo se evalúa
        if confidence >= umbral:
            tarea["status"] = "ready"
            # Aseguramos que no tenga bucket conflictivo
            tarea.pop("bucket", None)
            logger.info(
                "Tarea %d: confidence %.2f >= umbral -> ready",
                tarea.get("id"),
                confidence,
            )
        else:
            tarea["bucket"] = "manual_review_needed"
            # No cambiamos status, se mantiene 'revisar' (o se podría cambiar, pero la spec no lo dice)
            # La spec dice: "sino → bucket manual_review_needed". No menciona cambio de status.
            # En el test se espera que el segundo ítem tenga bucket="manual_review_needed" y status no se modifica.
            # Así que no tocamos status.
            logger.info(
                "Tarea %d: confidence %.2f < umbral -> manual_review_needed",
                tarea.get("id"),
                confidence,
            )
        modificadas.append(tarea)

    # Escribir backlog actualizado
    with open(path, "w", encoding="utf-8") as f:
        json.dump(backlog, f, indent=2, ensure_ascii=False)

    return modificadas


def main() -> None:
    """Función principal: ejecuta las tres rutinas en orden."""
    update_config()
    retry_tasks()
    autoreview_tasks()


if __name__ == "__main__":
    # Auto-tests si la variable de entorno está presente
    if os.getenv("CODEX_SELFTEST") == "1":
        # ------------------------------------------------------------------
        # 1️⃣ Test update_config
        # ------------------------------------------------------------------
        cfg_path = Path("tmp_ajustes.json")
        cfg_path.write_text("{}")  # archivo vacío
        update_config(cfg_path)  # aplica cambios
        cfg = json.loads(cfg_path.read_text())
        assert cfg["codex"]["providers"] == {
            "primary": "groq",
            "secondary": "ollama",
            "max_retries": 2,
            "retry_delay_s": 60,
            "auto_review_confidence": 0.85,
        }, "La actualización del JSON no coincide con la decisión de la junta"

        # ------------------------------------------------------------------
        # 2️⃣ Test retry_tasks
        # ------------------------------------------------------------------
        backlog_path = Path("tmp_backlog.json")
        backlog = [
            {"id": 1, "status": "failed", "retries_left": 2},
            {"id": 2, "status": "pending_generate", "retries_left": 1},
            {"id": 3, "status": "ready", "retries_left": 0},
        ]
        backlog_path.write_text(json.dumps(backlog))
        random.seed(0)  # reproducibilidad
        modified = retry_tasks(limit=10, path=backlog_path)

        # Se esperan 2 tareas modificadas; provider asignado debe seguir
        # la distribución 80/20 (seed 0 → primary).
        assert len(modified) == 2
        assert all(t["status"] == "queued" for t in modified)
        assert modified[0]["provider"] == "groq"
        assert modified[1]["provider"] == "groq"
        assert modified[0]["retries_left"] == 1  # 2->1
        assert modified[1]["retries_left"] == 0  # 1->0

        # ------------------------------------------------------------------
        # 3️⃣ Test autoreview_tasks
        # ------------------------------------------------------------------
        backlog = [
            {"id": 10, "status": "revisar", "tags": ["low_complexity"], "confidence": 0.90},
            {"id": 11, "status": "revisar", "tags": ["low_complexity"], "confidence": 0.70},
            {"id": 12, "status": "ready", "tags": ["low_complexity"], "confidence": 0.95},
        ]
        backlog_path.write_text(json.dumps(backlog))
        random.seed(1)  # aunque el pipeline es simulado, mantenemos consistencia
        modified = autoreview_tasks(limit=10, path=backlog_path)

        # Deben procesarse solo los 2 ítems con status "revisar"
        assert len(modified) == 2
        # El primero supera el umbral → ready
        assert modified[0]["status"] == "ready"
        # El segundo no supera → bucket manual_review_needed
        assert modified[1]["bucket"] == "manual_review_needed"
        # Confidences deben mantenerse sin alteración
        assert modified[0]["confidence"] == 0.90
        assert modified[1]["confidence"] == 0.70

        print("✅ Todos los auto‑tests pasaron correctamente.")
        exit(0)  # evita la ejecución posterior del script real

    # Parseo de argumentos CLI
    parser = argparse.ArgumentParser(description="Mantenimiento de Codex")
    parser.add_argument("--update-config", action="store_true", help="Actualizar configuración")
    parser.add_argument("--retry", action="store_true", help="Reintentar tareas fallidas")
    parser.add_argument("--autoreview", action="store_true", help="Revisión automática de tareas")
    args = parser.parse_args()

    # Si no se especifican flags, ejecutar todo
    if not any([args.update_config, args.retry, args.autoreview]):
        main()
    else:
        if args.update_config:
            update_config()
        if args.retry:
            retry_tasks()
        if args.autoreview:
            autoreview_tasks()
