#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codex_retry.py - Re‑encola tareas fallidas/pendientes y actualiza configuración.
Uso: python -m codex_retry [--backlog PATH] [--config PATH] [--self-test]
"""

import json
import pathlib
import time
import random
import sys
import argparse
import subprocess
import os
import textwrap

# ----------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------
DEFAULT_BACKLOG = "backlog_codex"
DEFAULT_CONFIG = "ajustes_junta.json"
MAX_TASKS = 10
GROQ_PROB = 0.8
MAX_RETRIES = 2
RETRY_DELAY_S = 60
CRON_INTERVAL_MIN = 10
CRON_COMMAND = f"python -m codex_retry --backlog {DEFAULT_BACKLOG} --config {DEFAULT_CONFIG}"

# ----------------------------------------------------------------------
# Funciones internas
# ----------------------------------------------------------------------
def load_backlog(path: str) -> list[dict]:
    """Carga el fichero JSON‑Lines y devuelve lista de diccionarios."""
    p = pathlib.Path(path)
    if not p.exists():
        print(f"Error: no se encuentra el backlog '{path}'", file=sys.stderr)
        sys.exit(1)
    tasks = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks

def select_tasks(tasks: list[dict]) -> list[dict]:
    """Filtra tareas con estado 'failed' o 'pending_generate' y devuelve hasta MAX_TASKS."""
    filtered = [t for t in tasks if t.get("state") in ("failed", "pending_generate")]
    return filtered[:MAX_TASKS]

def choose_provider() -> str:
    """Selecciona proveedor con probabilidad 80% groq, 20% ollama."""
    return "groq" if random.random() < GROQ_PROB else "ollama"

def requeue(task: dict, provider: str) -> dict:
    """Añade campos de re‑encolado a la tarea."""
    new_task = task.copy()
    new_task["provider"] = provider
    new_task["retry_count"] = task.get("retry_count", 0) + 1
    new_task["next_attempt_ts"] = int(time.time()) + RETRY_DELAY_S
    new_task["max_retries"] = MAX_RETRIES
    return new_task

def save_backlog(path: str, tasks: list[dict]) -> None:
    """Guarda la lista de tareas en formato JSON‑Lines."""
    p = pathlib.Path(path)
    with p.open("w", encoding="utf-8") as f:
        for task in tasks:
            f.write(json.dumps(task, ensure_ascii=False) + "\n")

def update_config(path: str) -> None:
    """Actualiza el fichero de configuración con el bloque codex.providers."""
    p = pathlib.Path(path)
    config = {}
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            config = json.load(f)
    config["codex.providers"] = {
        "primary": "groq",
        "secondary": "ollama",
        "max_retries": MAX_RETRIES,
        "retry_delay_s": RETRY_DELAY_S,
        "auto_review_confidence": 0.85,
    }
    with p.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def install_cron() -> None:
    """Añade tarea cron cada 10 minutos y la ejecuta inmediatamente."""
    cron_line = f"*/{CRON_INTERVAL_MIN} * * * * {CRON_COMMAND}\n"
    try:
        # Obtener crontab actual
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            check=False,
        )
        existing = result.stdout if result.returncode == 0 else ""
        # Evitar duplicados
        if cron_line not in existing:
            new_cron = existing + cron_line
            # Escribir nuevo crontab
            proc = subprocess.run(
                ["crontab", "-"],
                input=new_cron,
                text=True,
                capture_output=True,
                check=True,
            )
            print("Cron instalado: cada 10 minutos.")
        else:
            print("Cron ya existente.")
        # Ejecutar inmediatamente
        subprocess.Popen(
            CRON_COMMAND.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("Ejecución inmediata lanzada.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar cron: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: crontab no disponible en este sistema.", file=sys.stderr)
        sys.exit(1)

# ----------------------------------------------------------------------
# Pruebas (--self-test)
# ----------------------------------------------------------------------
def run_self_test() -> None:
    """Ejecuta los casos de prueba especificados."""
    # Preparación común
    tmp_backlog = pathlib.Path("tmp_backlog")
    tmp_conf = pathlib.Path("tmp_conf.json")
    tmp_backlog.write_text("\n".join([
        json.dumps({"id": 1, "state": "failed"}),
        json.dumps({"id": 2, "state": "pending_generate"}),
        json.dumps({"id": 3, "state": "done"}),
        json.dumps({"id": 4, "state": "failed"}),
        json.dumps({"id": 5, "state": "failed"}),
        json.dumps({"id": 6, "state": "pending_generate"}),
        json.dumps({"id": 7, "state": "failed"}),
        json.dumps({"id": 8, "state": "failed"}),
        json.dumps({"id": 9, "state": "failed"}),
        json.dumps({"id": 10, "state": "failed"}),
        json.dumps({"id": 11, "state": "failed"}),
    ]))
    tmp_conf.write_text("{}")

    # 1️⃣ Selección máxima de 10 tareas
    tasks = load_backlog(str(tmp_backlog))
    sel = select_tasks(tasks)
    assert len(sel) == 10, "Debe devolver exactamente 10 tareas"
    assert all(t["state"] in ("failed", "pending_generate") for t in sel)

    # 2️⃣ Distribución probabilística de proveedores (prueba determinística)
    random.seed(0)  # fuerza reproducibilidad
    providers = [choose_provider() for _ in range(1000)]
    groq_cnt = providers.count("groq")
    ollama_cnt = providers.count("ollama")
    assert 750 <= groq_cnt <= 850, "Groq debe aparecer ~80 % de las veces"
    assert 150 <= ollama_cnt <= 250, "Ollama debe aparecer ~20 % de las veces"

    # 3️⃣ Re‑encolado respeta límites de reintentos y delay
    task = {"id": 42, "state": "failed", "retry_count": 0}
    requeued = requeue(task, "groq")
    assert requeued["provider"] == "groq"
    assert requeued["retry_count"] == 1
    assert requeued["next_attempt_ts"] == int(time.time()) + 60
    assert requeued["max_retries"] == 2

    # 4️⃣ Actualización de configuración
    update_config(str(tmp_conf))
    conf = json.loads(tmp_conf.read_text())
    expected = {
        "primary": "groq",
        "secondary": "ollama",
        "max_retries": 2,
        "retry_delay_s": 60,
        "auto_review_confidence": 0.85,
    }
    assert conf.get("codex.providers") == expected, "Configuración no coincide"

    # Limpiar archivos temporales
    tmp_backlog.unlink(missing_ok=True)
    tmp_conf.unlink(missing_ok=True)

    print("PRUEBAS OK")
    sys.exit(0)

# ----------------------------------------------------------------------
# Punto de entrada principal
# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Re‑encola tareas fallidas/pendientes.")
    parser.add_argument("--backlog", default=DEFAULT_BACKLOG, help="Ruta al fichero backlog_codex")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Ruta al fichero ajustes_junta.json")
    parser.add_argument("--self-test", action="store_true", help="Ejecuta pruebas internas y sale")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    # Lógica principal
    try:
        tasks = load_backlog(args.backlog)
        selected = select_tasks(tasks)
        if not selected:
            print("No hay tareas pendientes para re‑encolar.")
            sys.exit(0)

        # Re‑encolar cada tarea seleccionada
        for i, task in enumerate(selected):
            provider = choose_provider()
            updated = requeue(task, provider)
            # Reemplazar en la lista original (por si se necesita guardar todo)
            # Buscar por id (asumiendo que son únicos)
            for j, t in enumerate(tasks):
                if t.get("id") == updated["id"]:
                    tasks[j] = updated
                    break
            print(f"Tarea {updated['id']} re‑encolada con {provider} (intento {updated['retry_count']})")

        save_backlog(args.backlog, tasks)
        update_config(args.config)
        install_cron()
        print("Proceso completado exitosamente.")
        sys.exit(0)
    except Exception as e:
        print(f"Error crítico: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
