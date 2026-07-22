#!/usr/bin/env python3
"""
Verificador de puertos TCP con autoverificación integrada.
Comprueba si los puertos 8890, 8891 y 8900 responden en un host dado.
"""

import argparse
import json
import socket
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


def check_port(host: str, port: int, timeout: float) -> dict:
    """
    Verifica si un puerto TCP está accesible y mide la latencia de conexión.

    Args:
        host: Dirección del host a verificar.
        port: Número de puerto TCP.
        timeout: Tiempo máximo de espera en segundos.

    Returns:
        Diccionario con puerto, estado de accesibilidad y latencia en ms.
    """
    resultado = {"port": port, "reachable": False, "latency_ms": None}

    try:
        inicio = time.perf_counter()
        with socket.create_connection((host, port), timeout=timeout):
            fin = time.perf_counter()
            resultado["reachable"] = True
            resultado["latency_ms"] = (fin - inicio) * 1000.0
    except (socket.timeout, ConnectionRefusedError, OSError):
        # Puerto no accesible o timeout
        pass

    return resultado


def check_all(host: str, ports: List[int], timeout: float) -> dict:
    """
    Verifica todos los puertos especificados y genera un informe completo.

    Args:
        host: Dirección host a verificar.
        ports: Lista de puertos a comprobar.
        timeout: Tiempo máximo de espera en segundos para cada puerto.

    Returns:
        Diccionario con host, timestamp, estado de puertos y salud general.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    resultados_puertos: Dict[str, dict] = {}
    todos_alcanzables = True

    for puerto in ports:
        resultado = check_port(host, puerto, timeout)
        clave = str(puerto)
        puertos_info = {
            "reachable": resultado["reachable"],
            "latency_ms": resultado["latency_ms"],
        }
        resultados_puertos[clave] = puertos_info
        if not resultado["reachable"]:
            todos_alcanzables = False

    return {
        "host": host,
        "timestamp": timestamp,
        "ports": resultados_puertos,
        "healthy": todos_alcanzables,
    }


def _servidor_efimero(puerto: int, evento_parada: threading.Event) -> None:
    """
    Inicia un servidor TCP efímero en el puerto dado para pruebas.

    Args:
        puerto: Puerto en el que escuchar.
        evento_parada: Evento para detener el servidor.
    """
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        servidor.bind(("127.0.0.1", puerto))
        servidor.listen(1)
        servidor.settimeout(0.5)
        while not evento_parada.is_set():
            try:
                conn, _ = servidor.accept()
                conn.close()
            except socket.timeout:
                continue
    finally:
        servidor.close()


def ejecutar_pruebas() -> None:
    """
    Ejecuta los tres casos de prueba con servidores efímeros y aserciones.
    """
    print("Iniciando pruebas de autoverificación...")

    # --- Caso A: Todos los puertos abiertos ---
    print("  Caso A: Todos los puertos abiertos")
    evento_paro = threading.Event()
    hilos_servidores = []
    for puerto in [8890, 8891, 8900]:
        hilo = threading.Thread(
            target=_servidor_efimero, args=(puerto, evento_paro), daemon=True
        )
        hilo.start()
        hilos_servidores.append(hilo)

    time.sleep(0.1)  # Dar tiempo a que los servidores inicien
    resultado_a = check_all("127.0.0.1", [8890, 8891, 8900], timeout=0.5)
    evento_paro.set()
    for hilo in hilos_servidores:
        hilo.join(timeout=1.0)

    assert resultado_a["healthy"] is True, "Caso A: healthy debe ser True"
    for p in [8890, 8891, 8900]:
        clave = str(p)
        assert resultado_a["ports"][clave]["reachable"] is True, (
            f"Caso A: puerto {p} debe ser reachable"
        )
        assert isinstance(resultado_a["ports"][clave]["latency_ms"], float), (
            f"Caso A: latencia de {p} debe ser float"
        )
        assert resultado_a["ports"][clave]["latency_ms"] >= 0, (
            f"Caso A: latencia de {p} debe ser >= 0"
        )

    # --- Caso B: Dos abiertos, uno cerrado ---
    print("  Caso B: Dos abiertos, uno cerrado")
    evento_paro = threading.Event()
    hilos_servidores = []
    for puerto in [8890, 8891]:
        hilo = threading.Thread(
            target=_servidor_efimero, args=(puerto, evento_paro), daemon=True
        )
        hilo.start()
        hilos_servidores.append(hilo)

    time.sleep(0.1)
    resultado_b = check_all("127.0.0.1", [8890, 8891, 8900], timeout=0.5)
    evento_paro.set()
    for hilo in hilos_servidores:
        hilo.join(timeout=1.0)

    assert resultado_b["healthy"] is False, "Caso B: healthy debe ser False"
    assert resultado_b["ports"]["8890"]["reachable"] is True, (
        "Caso B: puerto 8890 debe ser reachable"
    )
    assert resultado_b["ports"]["8891"]["reachable"] is True, (
        "Caso B: puerto 8891 debe ser reachable"
    )
    assert resultado_b["ports"]["8900"]["reachable"] is False, (
        "Caso B: puerto 8900 debe ser unreachable"
    )
    for p in [8890, 8891]:
        clave = str(p)
        assert isinstance(resultado_b["ports"][clave]["latency_ms"], float), (
            f"Caso B: latencia de {p} debe ser float"
        )
        assert resultado_b["ports"][clave]["latency_ms"] >= 0, (
            f"Caso B: latencia de {p} debe ser >= 0"
        )
    assert resultado_b["ports"]["8900"]["latency_ms"] is None, (
        "Caso B: latencia de 8900 debe ser None"
    )

    # Caso C: Ninguno abierto
    print("  Caso C: Ninguno abierto")
    resultado_c = check_all("127.0.0.1", [8890, 8891, 8900], timeout=0.2)
    assert resultado_c["healthy"] is False, "Caso C: healthy debe ser False"
    for p in [8890, 8891, 8900]:
        clave = str(p)
        assert resultado_c["ports"][clave]["reachable"] is False, (
            f"Caso C: puerto {p} debe ser unreachable"
        )
        assert resultado_c["ports"][clave]["latency_ms"] is None, (
            f"Caso C: latencia de {p} debe ser None"
        )

    print("PRUEBAS OK")


def main() -> None:
    """
    Punto de entrada principal: parsea argumentos, ejecuta pruebas y verifica puertos.
    """
    parser = argparse.ArgumentParser(
        description="Verificador de puertos TCP con autoverificación."
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host a verificar (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--ports",
        default="8890,8891,8900",
        help="Puertos separados por coma (default: 8890,8891,8900)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.5,
        help="Timeout en segundos por puerto (default: 0.5)",
    )
    parser.add_argument(
        "--no-selftest",
        action="store_true",
        help="Omite la autoverificación (no recomendado)",
    )
    args = parser.parse_args()

    # Ejecutar autoverificación si no se omite
    if not args.no_selftest:
        try:
            ejecutar_pruebas()
        except AssertionError as e:
            print(f"ERROR en autoverificación: {e}", file=sys.stderr)
            return 2

    # Parsear puertos
    try:
        puertos = [int(p.strip()) for p in args.ports.split(",")]
    except ValueError:
        print("Error: formato de puertos inválido", file=sys.stderr)
        return 2

    # Ejecutar verificación principal
    resultado = check_all(args.host, puertos, args.timeout)
    print(json.dumps(resultado, indent=2))

    return 0 if resultado["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
