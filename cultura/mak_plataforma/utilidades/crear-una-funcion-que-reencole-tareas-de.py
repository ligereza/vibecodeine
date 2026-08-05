#!/usr/bin/env python3
"""
Módulo para reencolar tareas fallidas del proveedor groq hacia pools de inferencia
ponderados (ollama, cerebras, azure).

Uso como módulo:
    from requeue_failed_tasks import requeue_failed_tasks
    resultado = requeue_failed_tasks("fallidas.json")

Uso como CLI:
    python -m requeue_failed_tasks <ruta_json>
"""

import json
import logging
import os
import random
import sys
import tempfile
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Pesos preferenciales para la selección de pool
# ---------------------------------------------------------------------------
_POOL_WEIGHTS: Dict[str, float] = {
    "ollama": 0.35,
    "cerebras": 0.45,
    "azure": 0.15,
}

# Nombres de los pools en el orden usado por random.choices
_POOL_NAMES = list(_POOL_WEIGHTS.keys())
_POOL_WEIGHT_VALUES = [_POOL_WEIGHTS[n] for n in _POOL_NAMES]


def _select_pool(rng: random.Random) -> str:
    """
    Selecciona un pool (ollama, cerebras, azure) según los pesos
    preferenciales definidos en _POOL_WEIGHTS.

    Parámetros
    ----------
    rng : random.Random
        Generador de números aleatorios inyectable (para facilitar pruebas).

    Retorna
    -------
    str
        Nombre del pool seleccionado.
    """
    return rng.choices(_POOL_NAMES, weights=_POOL_WEIGHT_VALUES, k=1)[0]


def requeue_failed_tasks(
    source: str,
    *,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, List[str]]:
    """
    Lee una lista de tareas fallidas desde un archivo JSON y las reencola
    en los pools ollama, cerebras y azure según los pesos preferenciales.

    Parámetros
    ----------
    source : str
        Ruta al archivo JSON con las tareas fallidas.
        Formato esperado: [{"id": "<uid>", "payload": {...}}, ...]
    logger : logging.Logger, opcional
        Logger a utilizar. Si no se provee, se crea uno con el nombre
        "codex.requeue".

    Retorna
    -------
    dict
        Diccionario con la forma:
        {"ollama": [...], "cerebras": [...], "azure": [...]}
        donde cada lista contiene los IDs de las tareas asignadas a ese pool.
    """
    # Configurar logger si no se proporcionó uno
    if logger is None:
        logger = logging.getLogger("codex.requeue")
        if not logger.handlers:
            # Configuración básica solo si no tiene manejadores previos
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

    # Leer el archivo JSON de entrada
    try:
        with open(source, "r", encoding="utf-8") as fh:
            tareas: List[Dict[str, Any]] = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.error("Error al leer el archivo fuente '%s': %s", source, exc)
        raise

    # Inicializar el acumulador de resultados
    resultado: Dict[str, List[str]] = {
        "ollama": [],
        "cerebras": [],
        "azure": [],
    }

    # Generador de randomizado para la selección de pool
    rng = random.Random()

    # Procesar cada tarea
    for tarea in tareas:
        id_tarea = tarea.get("id")
        if id_tarea is None:
            logger.warning("Tarea sin 'id' encontrada, se omite: %s", tarea)
            continue

        pool_seleccionado = _select_pool(rng)
        resultado[pool_seleccionado].append(id_tarea)
        logger.info("Task %s → %s", id_tarea, pool_seleccionado)

    return resultado


# ======================================================================
# 2. Interfaz de línea de comandos
# ======================================================================
def _main_cli() -> None:
    """Punto de entrada para ejecución desde línea de comandos."""
    if len(sys.argv) != 2:
        print("Uso: python -m requeue_failed_tasks <ruta_json>", file=sys.stderr)
        sys.exit(1)

    ruta_json = sys.argv[1]
    # Configurar logging para CLI
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logger = logging.getLogger("codex.requeue.cli")

    try:
        resultado = requeue_failed_tasks(ruta_json, logger=logger)
        # Imprimir resumen JSON en stdout
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as exc:
        logger.error("Error durante la ejecución: %s", exc)
        sys.exit(1)


# ----------------------------------------------------------------------
# 3. Casos de prueba auto-verificados
# ----------------------------------------------------------------------
def _ejecutar_prueba(
    contenido_json: str,
    semilla: int,
    esperado: Dict[str, List[str]],
) -> None:
    """
    Crea un archivo JSON temporal, ejecuta requeue_failed_tasks con una
    semilla fija y verifica que el resultado coincida con el esperado.

    Parámetros
    ----------
    contenido_json : str
        Contenido JSON que se escribirá en el archivo temporal.
    semilla : int
        Semilla para el generador randomizado.
    esperado : dict
        Diccionario con la asignación esperada.
    """
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, suffix=".json", encoding="utf-8"
    ) as f:
        f.write(contenido_json)
        f.flush()
        ruta = f.name

    # Guardar referencia a la función original
    original_select_pool = _select_pool

    # Crear un generador con la semilla deseada
    rng_prueba = random.Random(semilla)

    # Parchear la función interna para usar nuestro rng
    def _select_pool_patched(_: random.Random) -> str:
        return original_select_pool(rng_prueba)

    # Aplicar el parche en el espacio de nombres del módulo
    import requeue_failed_tasks as modulo_actual

    modulo_actual._select_pool = _select_pool_patched  # type: ignore[attr-defined]

    try:
        # Ejecutar la función bajo prueba
        logger_prueba = logging.getLogger("test.requeue")
        logger_prueba.setLevel(logging.WARNING)  # Silenciar logs durante pruebas
        resultado = requeue_failed_tasks(ruta, logger=logger_prueba)

        # Verificar aserción
        assert (
            resultado == esperado
        ), f"FALLO: esperado {esperado}, obtenido {resultado}"
    finally:
        # Restaurar la función original
        modulo_actual._select_pool = original_select_pool
        # Eliminar el archivo temporal
        os.unlink(ruta)


if __name__ == "__main__":
    # Caso de prueba 1
    _ejecutar_prueba(
        '[{"id":"t1"},{"id":"t2"},{"id":"t3"}]',
        semilla=0,
        esperado={"ollama": ["t1"], "cerebras": ["t2"], "azure": ["t3"]},
    )

    # Caso de prueba 2
    _ejecutar_prueba(
        '[{"id":"a"},{"id":"b"},{"id":"c"},{"id":"d"}]',
        semilla=42,
        esperado={"ollama": ["a", "d"], "cerebras": ["b"], "azure": ["c"]},
    )

    # Caso de prueba 3
    _ejecutar_prueba(
        "[]",
        semilla=123,
        esperado={"ollama": [], "cerebras": [], "azure": []},
    )

    print("PRUEBAS OK")
