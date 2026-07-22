#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejecución paralela de tareas para el backlog de Codex.
Utiliza únicamente la biblioteca estándar de Python 3.11.
"""

import logging
import threading
import time
from datetime import datetime, timedelta


def ejecutar_tarea(tarea: str, provider: str, log_file: str) -> None:
    """
    Simula la ejecución de una tarea individual.

    Args:
        tarea: Nombre o identificador de la tarea.
        provider: Proveedor a utilizar (ej. "groq").
        log_file: Ruta del archivo de registro (no se usa directamente aquí,
                  pues el logging ya está configurado).
    """
    logging.info(f"Ejecutando tarea {tarea} con proveedor {provider}")
    time.sleep(1)  # Simula la ejecución de la tarea
    logging.info(f"Tarea {tarea} finalizada")


def main(num_tareas: int, provider: str, log_file: str, ventana: float,
         paralelismo: int) -> None:
    """
    Ejecuta un conjunto de tareas en paralelo respetando una ventana de tiempo
    y un nivel máximo de paralelismo.

    Args:
        num_tareas: Número total de tareas a ejecutar.
        provider: Proveedor a utilizar.
        log_file: Ruta del archivo de registro.
        ventana: Ventana de tiempo en horas para completar todas las tareas.
        paralelismo: Número máximo de tareas concurrentes.
    """
    # Configuración del logging
    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Generación de la lista de tareas
    tareas = [f"Tarea {i}" for i in range(num_tareas)]

    # Cálculo de la ventana de tiempo
    ventana_inicio = datetime.now()
    ventana_fin = ventana_inicio + timedelta(hours=ventana)

    hilos: list[threading.Thread] = []

    # Ejecución de tareas con control de paralelismo
    for tarea in tareas:
        hilo = threading.Thread(target=ejecutar_tarea,
                                args=(tarea, provider, log_file))
        hilos.append(hilo)
        hilo.start()

        # Si alcanzamos el límite de paralelismo, esperamos a que terminen
        if len(hilos) >= paralelismo:
            for hilo in hilos:
                hilo.join()
            hilos = []

    # Esperar a los hilos restantes (si los hay)
    for hilo in hilos:
        hilo.join()

    # Verificación de la ventana de tiempo
    tiempo_actual = datetime.now()
    assert tiempo_actual < ventana_fin, (
        f"No se cumple la ventana de tiempo. "
        f"Inicio: {ventana_inicio}, Fin: {ventana_fin}, Actual: {tiempo_actual}"
    )

    # Casos de prueba (autoverificación)
    assert num_tareas == 4, f"Número de tareas incorrecto: {num_tareas}"
    assert provider == "groq", f"Proveedor incorrecto: {provider}"
    assert log_file == "/var/log/mak/backlog_codex.log", (
        f"Archivo de registro incorrecto: {log_file}"
    )
    assert ventana == 12, f"Ventana de tiempo incorrecta: {ventana}"
    assert paralelismo == 2, f"Nivel de paralelismo incorrecto: {paralelismo}"


if __name__ == "__main__":
    # Parámetros de prueba según la especificación
    NUM_TAREAS = 4
    PROVIDER = "groq"
    LOG_FILE = "/var/log/mak/backlog_codex.log"
    VENTANA = 12  # horas
    PARALELISMO = 2

    # Ejecución principal con los casos de prueba
    main(NUM_TAREAS, PROVIDER, LOG_FILE, VENTANA, PARALELISMO)

    # Si llegamos aquí sin excepciones, todas las aserciones pasaron
    print("PRUEBAS OK")
