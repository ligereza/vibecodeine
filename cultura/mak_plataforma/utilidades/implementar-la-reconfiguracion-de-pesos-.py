#!/usr/bin/env python3
"""
Módulo codex_reconfig.py
------------------------
Realiza tres acciones simultáneas:
  1. Reconfigura los pesos de los proveedores en la tabla de decisiones.
  2. Re‑encola todas las tareas de Codex que fueron fallidas por *groq*
     dándoles prioridad alta.
  3. Genera / actualiza una entrada de *cron* que lanza cada 15 min
     el health‑check de *groq*.

Autor: Departamento Codex de MAK
Versión: 1.0.0
"""

import os
import subprocess
from typing import Dict, List, Optional

# ----------------------------------------------------------------------
# Constante para la línea de cron
# ----------------------------------------------------------------------
CRON_LINE = (
    "*/15 * * * * /usr/local/bin/groq_healthcheck >> /var/log/groq_hc.log 2>&1"
)


# ----------------------------------------------------------------------
# 1. Reconfiguración de pesos
# ----------------------------------------------------------------------
def reconfigure_weights(config: Dict[str, float]) -> Dict[str, float]:
    """
    Ajusta los pesos según la decisión de la junta:
        - Priorizar ollama y cerebras (aumentar su peso en +0.20)
        - Reducir groq (disminuir su peso en -0.15)
    Los valores resultantes se normalizan para que la suma sea 1.0.

    Parámetros
    ----------
    config : dict
        Diccionario con los pesos actuales de los proveedores.
        Ejemplo: {"ollama": 0.30, "cerebras": 0.30, "groq": 0.40}

    Retorna
    -------
    dict
        Nuevo diccionario con los pesos ajustados y normalizados.
    """
    # Copiamos para no mutar el argumento externo
    nuevos_pesos = config.copy()

    # Aplicamos los deltas definidos por la junta
    ajustes = {
        "ollama": 0.20,
        "cerebras": 0.20,
        "groq": -0.15,
    }
    for proveedor, delta in ajustes.items():
        valor_actual = nuevos_pesos.get(proveedor, 0.0)
        nuevos_pesos[proveedor] = max(valor_actual + delta, 0.0)

    # Normalizamos para que la suma sea exactamente 1.0
    suma_total = sum(nuevos_pesos.values())
    if suma_total == 0:
        raise ValueError("Todos los pesos son cero después del ajuste.")

    pesos_normalizados = {
        clave: round(valor / suma_total, 4)
        for clave, valor in nuevos_pesos.items()
    }
    return pesos_normalizados


# ----------------------------------------------------------------------
# 2. Re‑encolado de tareas fallidas por groq
# ----------------------------------------------------------------------
def requeue_failed_tasks(tasks: List[Dict]) -> List[Dict]:
    """
    Filtra las tareas cuyo campo `error_provider == "groq"` y
    les asigna `priority = "high"`.  Devuelve la lista completa
    (tareas válidas modificadas + las que no fallaron).

    Parámetros
    ----------
    tasks : list[dict]
        Lista de tareas. Cada tarea es un diccionario que puede contener
        el campo `error_provider`.

    Retorna
    -------
    list[dict]
        Lista de tareas procesadas. Las que fallaron por groq ahora tienen
        prioridad "high" y se les ha eliminado el campo `error_provider`.
    """
    tareas_procesadas: List[Dict] = []

    for tarea in tasks:
        # Clonamos siempre para no mutar la entrada original
        tarea_clonada = tarea.copy()

        if tarea_clonada.get("error_provider") == "groq":
            # Asignamos prioridad alta
            tarea_clonada["priority"] = "high"
            # Eliminamos la señal de error para que la cola la vuelva a procesar
            tarea_clonada.pop("error_provider", None)

        tareas_procesadas.append(tarea_clonada)

    return tareas_procesadas


# ----------------------------------------------------------------------
# 3. Programación del health‑check de groq cada 15 min
# ----------------------------------------------------------------------
def schedule_groq_healthcheck(cron_file: str = None) -> str:
    """
    Inserta (o actualiza) la línea `CRON_LINE` en el crontab del usuario.
    Si `cron_file` es *None* se usa `crontab -l`/`crontab -` vía subprocess.
    Devuelve el contenido completo del crontab después de la operación.

    Parámetros
    ----------
    cron_file : str, opcional
        Ruta a un archivo de crontab. Si es None, se opera sobre el crontab
        real del usuario mediante el comando `crontab`.

    Retorna
    -------
    str
        Contenido completo del crontab después de la inserción/actualización.
    """
    # 1) Leer crontab actual
    if cron_file is None:
        # Usamos el crontab real del usuario
        resultado = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
        )
        lineas_actuales = (
            resultado.stdout.splitlines() if resultado.returncode == 0 else []
        )
    else:
        # Leemos desde un archivo (útil para pruebas)
        if os.path.exists(cron_file):
            with open(cron_file, "r", encoding="utf-8") as archivo:
                lineas_actuales = archivo.read().splitlines()
        else:
            lineas_actuales = []

    # 2) Eliminar cualquier línea previa relacionada con groq_healthcheck
    lineas_filtradas = [
        linea for linea in lineas_actuales if "groq_healthcheck" not in linea
    ]

    # 3) Añadir la nueva línea de cron
    lineas_filtradas.append(CRON_LINE)

    # 4) Construir el nuevo contenido
    nuevo_contenido = "\n".join(lineas_filtradas) + "\n"

    # 5) Escribir de vuelta
    if cron_file is None:
        # Escribimos en el crontab real
        subprocess.run(
            ["crontab", "-"],
            input=nuevo_contenido,
            text=True,
            check=True,
        )
    else:
        # Escribimos en el archivo de pruebas
        with open(cron_file, "w", encoding="utf-8") as archivo:
            archivo.write(nuevo_contenido)

    return nuevo_contenido


# ==============================================================================
# Bloque principal: ejecución de pruebas y demostración
# ==============================================================================
if __name__ == "__main__":
    # ------------------------------------------------------------------
    # PRUEBAS AUTOMÁTICAS CON ASSERT
    # ------------------------------------------------------------------

    # ---------- TEST 1: reconfigure_weights ----------
    print("Ejecutando prueba 1: reconfigure_weights...")
    config_entrada = {"ollama": 0.25, "cerebras": 0.25, "groq": 0.50}
    config_salida = reconfigure_weights(config_entrada)

    # Cálculo manual esperado:
    #   ollama:   0.25 + 0.20 = 0.45
    #   cerebras: 0.25 + 0.20 = 0.45
    #   groq:     0.50 - 0.15 = 0.35
    #   suma total = 1.25
    #   normalizado:
    #     ollama:   0.45 / 1.25 = 0.36
    #     cerebras: 0.45 / 1.25 = 0.36
    #     groq:     0.35 / 1.25 = 0.28
    esperado = {
        "ollama": round(0.45 / 1.25, 4),
        "cerebras": round(0.45 / 1.25, 4),
        "groq": round(0.35 / 1.25, 4),
    }
    assert config_salida == esperado, (
        f"Prueba 1 FALLÓ: se esperaba {esperado}, pero se obtuvo {config_salida}"
    )
    print("  ✓ Prueba 1 pasó correctamente.")

    # ---------- 2: requeue_failed_tasks ----------
    print("Ejecutando prueba 2: requeue_failed_tasks...")
    tareas_entrada = [
        {"id": 10, "payload": "A", "error_provider": "groq", "priority": "low"},
        {"id": 11, "payload": "B", "error_provider": "openai"},
        {"id": 12, "payload": "C"},
    ]
    tareas_salida = requeue_failed_tasks(tareas_entrada)
    tareas_esperadas = [
        {"id": 10, "payload": "A", "priority": "high"},
        {"id": 11, "payload": "B", "error_provider": "openai"},
        {"id": 12, "payload": "C"},
    ]
    assert tareas_salida == tareas_esperadas, (
        f"Prueba 2 FALLÓ: se esperaba {tareas_esperadas}, se obtuvo {tareas_salida}"
    )
    print("  Prueba 2 pasó correctamente.")

    # ---------- Test 3: schedule_groq_healthcheck ----------
    print("Ejecutando prueba 3: schedule_groq_healthcheck...")
    archivo_temporal = "/tmp/cron_test_codex.txt"

    # Inicializamos con una línea cualquiera
    with open(archivo_temporal, "w", encoding="utf-8") as f:
        f.write("0 0 * * * /usr/bin/backup\n")

    cron_despues = schedule_groq_healthcheck(archivo_temporal)

    # Verificamos que la línea de groq_healthcheck esté presente
    assert CRON_LINE in cron_despues, (
        "Prueba 3 FALLÓ: la línea de cron no fue encontrada en el crontab."
    )
    # Verificamos que no haya duplicados
    ocurrencias = cron_despues.count("groq_healthcheck")
    assert ocurrencias == 1, (
        f"Prueba 3 FALLÓ: se encontraron {ocurrencias} ocurrencias de "
        f"groq_healthcheck, se esperaba exactamente 1."
    )
    print("  Prueba 3 pasó correctamente.")

    # Limpieza del archivo temporal de prueba
    if os.path.exists(archivo_temporal):
        os.remove(archivo_temporal)

    # ------------------------------------------------------------------
    # DEMOSTRACIÓN RÁPIDA (solo si todas las pruebas pasaron)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS PASARON CORRECTAMENTE.")
    print("=" * 60)

    print("\n--- Demostración de reconfigure_weights ---")
    ejemplo_cfg = {"ollama": 0.30, "cerebras": 0.30, "groq": 0.40}
    print(f"Pesos antes:    {ejemplo_cfg}")
    print(f"Pesos después:  {reconfigure_weights(ejemplo_cfg)}")

    print("\n--- Demostración de requeue_failed_tasks ---")
    ejemplo_tareas = [
        {"id": 1, "payload": "tarea_1", "priority": "low"},
        {"id": 2, "payload": "tarea_2", "error_provider": "groq"},
        {"id": 3, "payload": "tarea_3", "error_provider": "anthropic"},
    ]
    print(f"Tareas originales:  {ejemplo_tareas}")
    print(f"Tareas reencoladas: {requeue_failed_tasks(ejemplo_tareas)}")

    print("\n--- Demostración de schedule_groq_healthcheck ---")
    archivo_demo = "/tmp/cron_demo.txt"
    contenido = schedule_groq_healthcheck(archivo_demo)
    print(f"Archivo de cron generado en: {archivo_demo}")
    print(f"Contenido:\n{contenido}")
    # Limpieza
    if os.path.exists(archivo_demo):
        os.remove(archivo_demo)

    print("\nPRUEBAS OK")
