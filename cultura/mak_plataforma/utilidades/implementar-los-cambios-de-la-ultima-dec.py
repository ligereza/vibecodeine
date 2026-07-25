#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codex_cron.py - Cron jobs para el sistema Codex.
Solo utiliza la biblioteca estándar de Python 3.11.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path


# ----------------------------------------------------------------------
# 1. actualización de ajustes_junta.json
# ----------------------------------------------------------------------
def update_settings(path: Path = Path("ajustes_junta.json")) -> None:
    """Actualiza el archivo JSON con la configuración de providers requerida."""
    settings = {
        "codex.providers": {
            "primary": "groq",
            "secondary": "ollama",
            "max_retries": 2,
            "retry_delay_s": 60,
            "auto_review_confidence": 0.85,
        }
    }
    data = {}
    if path.is_file():
        data = json.loads(path.read_text())
    data.update(settings)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ----------------------------------------------------------------------
# 2. retry_tasks()
# ----------------------------------------------------------------------
def retry_tasks(
    backlog_path: Path = Path("backlog_codex.json"),
    max_per_run: int = 10,
    primary_ratio: float = 0.8,
) -> list[dict]:
    """
    - Carga el backlog (lista de dicts). Cada elemento debe contener:
        { "id": str, "status": "failed"|"pending", "retries": int }
    - Selecciona hasta ``max_per_run`` entradas con estado "failed" o "pending".
    - Asigna provider según ratio 80 % primary / 20 % secondary.
    - Decrementa el contador de reintentos (``retries``) y vuelve a encolar
      (simulado con un campo ``queued_at``).
    - Devuelve la lista de tareas modificadas (para ser usada por tests).
    """
    backlog = json.loads(backlog_path.read_text()) if backlog_path.is_file() else []
    # filtro
    candidates = [
        t for t in backlog if t["status"] in ("failed", "pending") and t["retries"] > 0
    ][:max_per_run]

    for i, task in enumerate(candidates):
        # routing
        provider = "primary" if random.random() < primary_ratio else "secondary"
        task["provider"] = provider
        task["retries"] -= 1
        task["queued_at"] = int(time.time())
        task["status"] = "queued"

    # sobrescribe el archivo
    backlog_path.write_text(json.dumps(backlog, indent=2, ensure_ascii=False))
    return candidates


# ----------------------------------------------------------------------
# 3. auto_review()
# ----------------------------------------------------------------------
def auto_review(
    review_path: Path = Path("reviews_queue.json"),
    max_per_run: int = 10,
    confidence_threshold: float = 0.85,
) -> list[dict]:
    """
    - Cada registro tiene: { "id": str, "complexity": "low_complexity",
                              "confidence": float, "status": "pending" }
    - Procesa hasta ``max_per_run`` entradas con ``complexity == "low_complexity"``
      y ``status == "pending"``.
    - Si ``confidence >= threshold`` → marca ``status = "ready"``.
    - En caso contrario → mueve el registro a ``manual_review_needed.json``.
    - Devuelve la lista de registros procesados (para pruebas).
    """
    queue = json.loads(review_path.read_text()) if review_path.is_file() else []
    to_process = [
        r
        for r in queue
        if r["complexity"] == "low_complexity" and r["status"] == "pending"
    ][:max_per_run]

    ready = []
    manual = []

    for rec in to_process:
        if rec["confidence"] >= confidence_threshold:
            rec["status"] = "ready"
            ready.append(rec)
        else:
            rec["status"] = "manual_review_needed"
            manual.append(rec)

    # actualizar archivos
    remaining = [r for r in queue if r not in to_process]
    review_path.write_text(json.dumps(remaining + ready, indent=2, ensure_ascii=False))

    manual_path = Path("manual_review_needed.json")
    existing_manual = json.loads(manual_path.read_text()) if manual_path.is_file() else []
    manual_path.write_text(json.dumps(existing_manual + manual, indent=2, ensure_ascii=False))

    return ready + manual


# ----------------------------------------------------------------------
# 4. CLI
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Cron jobs de Codex")
    parser.add_argument(
        "--retry", action="store_true", help="Ejecutar ciclo de retry_tasks"
    )
    parser.add_argument(
        "--autoreview", action="store_true", help="Ejecutar ciclo de auto_review"
    )
    args = parser.parse_args()

    update_settings()  # siempre se asegura la última configuración

    if args.retry:
        changed = retry_tasks()
        print(f"[retry] Procesadas {len(changed)} tareas.")
    if args.autoreview:
        changed = auto_review()
        print(f"[autoreview] Procesadas {len(changed)} revisiones.")

    # si no se especifica nada, ejecutar ambas (pasada inmediata)
    if not (args.retry or args.autoreview):
        retry_tasks()
        auto_review()


# ----------------------------------------------------------------------
# 5. AUTOTESTS (se ejecutan al cargar el módulo)
# ----------------------------------------------------------------------
def _run_self_tests():
    # ---------- caso 1: update_settings ----------
    tmp_path = Path("tmp_ajustes.json")
    tmp_path.unlink(missing_ok=True)
    update_settings(tmp_path)
    data = json.loads(tmp_path.read_text())
    assert data["codex.providers"]["primary"] == "groq"
    assert data["codex.providers"]["max_retries"] == 2
    tmp_path.unlink()

    # ---------- caso 2: retry_tasks ----------
    backlog = [
        {"id": "t1", "status": "failed", "retries": 2},
        {"id": "t2", "status": "pending", "retries": 1},
        {"id": "t3", "status": "failed", "retries": 0},
    ]
    b_path = Path("tmp_backlog.json")
    b_path.write_text(json.dumps(backlog, indent=2))
    processed = retry_tasks(b_path, max_per_run=2, primary_ratio=1.0)  # fuerza primary
    assert len(processed) == 2
    assert all(t["provider"] == "primary" for t in processed)
    assert processed[0]["retries"] == 1
    assert processed[1]["retries"] == 0
    b_path.unlink()

    # ---------- caso 3: auto_review ----------
    reviews = [
        {"id": "r1", "complexity": "low_complexity", "confidence": 0.9, "status": "pending"},
        {"id": "r2", "complexity": "low_complexity", "confidence": 0.7, "status": "pending"},
        {"id": "r3", "complexity": "high_complexity", "confidence": 0.95, "status": "pending"},
    ]
    r_path = Path("tmp_reviews.json")
    r_path.write_text(json.dumps(reviews, indent=2))
    processed = auto_review(r_path, max_per_run=2, confidence_threshold=0.85)
    # r1 → ready, r2 → manual_review_needed
    assert any(p["id"] == "r1" and p["status"] == "ready" for p in processed)
    assert any(p["id"] == "r2" and p["status"] == "manual_review_needed" for p in processed)
    # r3 debe quedar sin tocar
    remaining = json.loads(r_path.read_text())
    assert any(r["id"] == "r3" for r in remaining)
    # fichero manual debe contener r2
    manual = json.loads(Path("manual_review_needed.json").read_text())
    assert any(m["id"] == "r2" for m in manual)
    # limpieza
    r_path.unlink()
    Path("manual_review_needed.json").unlink()

    print("PRUEBAS OK")


if __name__ == "__main__":
    # Ejecutar autopruebas antes de la lógica principal
    _run_self_tests()
    main()
