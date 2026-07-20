#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resumir_jobs.py — Procesa archivo JSONL de jobs y genera resumen.

Uso:
    python resumir_jobs.py [--top N] archivo.jsonl
    python resumir_jobs.py           # ejecuta pruebas unitarias
"""

import argparse
import collections
import datetime
import heapq
import io
import json
import sys
import tempfile
import unittest


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------

def parse_job_line(line: str) -> dict:
    """
    Parsea una línea JSON y valida que contenga los campos requeridos:
    'id', 'estado', 'ts' (ISO‑8601 parseable).

    Retorna el diccionario del job si es válido.
    Lanza ValueError o json.JSONDecodeError si la línea es corrupta.
    """
    # 1. Parseo JSON
    job = json.loads(line)
    if not isinstance(job, dict):
        raise ValueError("La línea JSON no es un objeto")

    # 2. Presencia de campos obligatorios
    for campo in ("id", "estado", "ts"):
        if campo not in job:
            raise ValueError(f"Falta el campo obligatorio '{campo}'")

    # 3. Validación de timestamp ISO‑8601
    datetime.datetime.fromisoformat(job["ts"])

    return job


def process_jobs(path: str, top: int = 5) -> tuple[dict, list, int]:
    """
    Procesa un archivo JSONL (una línea por objeto).

    Parámetros:
        path: ruta al archivo .jsonl (acepta '-' para stdin).
        top : cantidad de jobs más recientes a retornar.

    Retorna:
        counts       : dict {estado: cantidad}
        top_jobs     : lista de dicts (id, estado, ts) ordenados por ts descendente
        corrupt_count: número de líneas corruptas encontradas
    """
    # Abrir archivo o stdin
    if path == "-":
        fh = sys.stdin
    else:
        fh = open(path, "r", encoding="utf-8")

    counts = collections.defaultdict(int)
    corrupt_count = 0
    # Usamos un heap de tamaño máximo 'top' para mantener los más recientes.
    # Guardamos tuplas (ts_epoch, job_dict) para ordenar por timestamp.
    heap_top = []  # min‑heap sobre ts_epoch

    try:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue  # líneas vacías se ignoran sin contar como corruptas

            try:
                job = parse_job_line(linea)
            except (json.JSONDecodeError, ValueError):
                corrupt_count += 1
                continue

            estado = job["estado"]
            counts[estado] += 1

            # Convertir ts a epoch para ordenamiento numérico
            ts_dt = datetime.datetime.fromisoformat(job["ts"])
            ts_epoch = ts_dt.timestamp()

            # Mantener heap con los 'top' más recientes (mayor timestamp)
            heapq.heappush(heap_top, (ts_epoch, job))
            if len(heap_top) > top:
                heapq.heappop(heap_top)  # descarta el más antiguo (menor epoch)

    finally:
        if path != "-":
            fh.close()

    # Extraer jobs del heap y ordenarlos descendente por timestamp
    top_jobs_raw = [item[1] for item in heap_top]
    top_jobs_raw.sort(key=lambda j: datetime.datetime.fromisoformat(j["ts"]),
                      reverse=True)

    return dict(counts), top_jobs_raw, corrupt_count


# ---------------------------------------------------------------------------
# Interfaz de línea de comandos
# ---------------------------------------------------------------------------

def main() -> None:
    """Punto de entrada CLI."""
    parser = argparse.ArgumentParser(
        description="Resume jobs desde un archivo JSONL."
    )
    parser.add_argument(
        "archivo",
        help="Ruta al archivo .jsonl (usa '-' para stdin)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Cantidad de jobs más recientes a mostrar (defecto: 5)"
    )
    args = parser.parse_args()

    counts, top_jobs, corrupt = process_jobs(args.archivo, args.top)

    # Salida para consumo humano
    print("Conteo por estado:")
    for estado, num in sorted(counts.items()):
        print(f"  {estado}: {num}")

    print(f"\nTOP {args.top} más recientes:")
    for job in top_jobs:
        print(f"  {job['id']}  {job['ts']}")

    if corrupt:
        print(f"\n⚠️  Líneas corruptas encontradas: {corrupt}")


# ---------------------------------------------------------------------------
# Suite de pruebas unitarias
# ---------------------------------------------------------------------------

class TestProcessJobs(unittest.TestCase):
    """Pruebas para process_jobs con archivos temporales."""

    def _crear_archivo_temporal(self, contenido: str) -> str:
        """Crea un archivo temporal con el contenido dado y retorna su ruta."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, suffix=".jsonl"
        )
        tmp.write(contenido)
        tmp.close()
        return tmp.name

    def test_valid_multiple(self):
        """Caso A: múltiples líneas válidas, top=3."""
        contenido = (
            '{"id":"a","estado":"done","ts":"2021-09-01T10:00:00"}\n'
            '{"id":"b","estado":"running","ts":"2021-09-01T10:05:00"}\n'
            '{"id":"c","estado":"done","ts":"2021-09-01T09:59:59"}\n'
            '{"id":"d","estado":"queued","ts":"2021-09-01T10:10:00"}\n'
            '{"id":"e","estado":"running","ts":"2021-09-01T10:02:00"}\n'
        )
        path = self._crear_archivo_temporal(contenido)
        counts, top_jobs, corrupt = process_jobs(path, top=3)

        esperado_counts = {"done": 2, "running": 2, "queued": 1}
        esperado_top = [
            {"id": "d", "estado": "queued", "ts": "2021-09-01T10:10:00"},
            {"id": "b", "estado": "running", "ts": "2021-09-01T10:05:00"},
            {"id": "e", "estado": "running", "ts": "2021-09-01T10:02:00"},
        ]

        self.assertEqual(counts, esperado_counts)
        self.assertEqual(top_jobs, esperado_top)
        self.assertEqual(corrupt, 0)

    def test_with_corrupt_line(self):
        """Caso B: una línea corrupta entre dos válidas."""
        contenido = (
            '{"id":"x","estado":"done","ts":"2022-01-01T00:00:00"}\n'
            'not-a-json-line\n'
            '{"id":"y","estado":"failed","ts":"2022-01-01T01:00:00"}\n'
        )
        path = self._crear_archivo_temporal(contenido)
        counts, top_jobs, corrupt = process_jobs(path, top=5)

        esperado_counts = {"done": 1, "failed": 1}
        esperado_top = [
            {"id": "y", "estado": "failed", "ts": "2022-01-01T01:00:00"},
            {"id": "x", "estado": "done", "ts": "2022-01-01T00:00:00"},
        ]

        self.assertEqual(counts, esperado_counts)
        self.assertEqual(top_jobs, esperado_top)
        self.assertEqual(corrupt, 1)

    def test_empty_file(self):
        """Caso C: archivo vacío."""
        path = self._crear_archivo_temporal("")
        counts, top_jobs, corrupt = process_jobs(path, top=5)

        self.assertEqual(counts, {})
        self.assertEqual(top_jobs, [])
        self.assertEqual(corrupt, 0)

    def test_ts_invalido_cuenta_corrupto(self):
        """Cobertura adicional: timestamp no parseable cuenta como corrupto."""
        contenido = (
            '{"id":"z","estado":"done","ts":"2022-13-01T00:00:00"}\n'  # mes 13
        )
        path = self._crear_archivo_temporal(contenido)
        _, _, corrupt = process_jobs(path, top=5)
        self.assertEqual(corrupt, 1)


# ---------------------------------------------------------------------------
# Punto de entrada dual: CLI o pruebas
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Si se invoca sin argumentos (o con argumentos que no parecen de CLI),
    # ejecutamos las pruebas unitarias.
    # Detección simple: si no hay argumentos o el primero no es un archivo
    # existente ni '-', corremos unittest.
    if len(sys.argv) == 1 or (
        len(sys.argv) >= 2
        and sys.argv[1] not in ("-h", "--help")
        and sys.argv[1] != "-"
        and not any(arg.startswith("--top") for arg in sys.argv[1:])
        and not any(arg == "-" for arg in sys.argv[1:])
    ):
        # Ejecutar suite de pruebas
        unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False)
        print("\nPRUEBAS OK")
    else:
        main()
