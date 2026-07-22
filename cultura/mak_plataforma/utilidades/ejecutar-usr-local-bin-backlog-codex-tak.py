#!/usr/bin/env python3
"""
Script para ejecutar backlog_codex con redirección de salida a archivo de log.
Construye y ejecuta el comando equivalente a:
  /usr/local/bin/backlog_codex --take 4 --parallel 2 --provider groq >> /var/log/mak/backlog_codex_run_now.log 2>&1
"""

import argparse
import os
import subprocess
import sys
import tempfile
from typing import Optional


def build_cmd(executable: str, take: int, parallel: int, provider: str) -> List[str]:
    """
    Construye la lista de argumentos para subprocess.run.

    Args:
        executable: Ruta al binario backlog_codex.
        take: Valor para --take.
        parallel: Valor para --parallel.
        provider: Valor para --provider.

    Returns:
        Lista de strings con el comando y sus argumentos.
    """
    return [
        executable,
        "--take",
        str(take),
        "--parallel",
        str(parallel),
        "--provider",
        provider,
    ]


def run_backlog(
    executable: str,
    take: int,
    parallel: int,
    provider: str,
    logfile: str,
    dry_run: bool = False,
) -> int:
    """
    Ejecuta el comando backlog_codex con redirección de salida.

    Args:
        executable: Ruta al binario.
        take: Valor para --take.
        parallel: Valor para --parallel.
        provider: Valor para --provider.
        logfile: Ruta del archivo de log (se abre en modo append).
        dry_run: Si True, no ejecuta el comando y retorna 0.

    Returns:
        Código de retorno del proceso (0 si dry_run).
    """
    cmd = build_cmd(executable, take, parallel, provider)

    if dry_run:
        print(f"[DRY-RUN] Comando que se ejecutaría: {' '.join(cmd)}")
        print(f"[DRY-RUN] Redirigiendo salida a: {logfile}")
        return 0

    # Asegurar que el directorio del logfile existe
    log_dir = os.path.dirname(logfile)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Abrir logfile en modo append y ejecutar con redirección
    with open(logfile, "a", encoding="utf-8") as fh:
        resultado = subprocess.run(
            cmd,
            stdout=fh,
            stderr=subprocess.STDOUT,
            check=False,  # No lanzar excepción, devolver returncode
        )

    return resultado.returncode


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    """
    Parsea los argumentos de línea de comandos.

    Args:
        argv: Lista de argumentos (None para usar sys.argv).

    Returns:
        Namespace con los argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Ejecuta backlog_codex con redirección a archivo de log."
    )
    parser.add_argument(
        "--executable",
        default="/usr/local/bin/backlog_codex",
        help="Ruta al binario backlog_codex (default: %(default)s)",
    )
    parser.add_argument(
        "--take",
        type=int,
        default=4,
        help="Valor para --take (default: %(default)s)",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=2,
        help="Valor para --parallel (default: %(default)s)",
    )
    parser.add_argument(
        "--provider",
        default="groq",
        help="Valor para --provider (default: %(default)s)",
    )
    parser.add_argument(
        "--logfile",
        default="/var/log/mak/backlog_codex_run_now.log",
        help="Ruta del archivo de log (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra el comando sin ejecutarlo",
    )

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    """
    Punto de entrada principal del CLI.

    Args:
        argv: Lista de argumentos (None para usar sys.argv).

    Returns:
        Código de salida del proceso.
    """
    args = parse_args(argv)
    return run_backlog(
        executable=args.executable,
        take=args.take,
        parallel=args.parallel,
        provider=args.provider,
        logfile=args.logfile,
        dry_run=args.dry_run,
    )


def _ejecutar_pruebas() -> None:
    """
    Rutina de autoverificación con asserts.
    Se ejecuta antes del flujo principal si no hay argumentos de CLI.
    """
    print("Ejecutando pruebas de autoverificación...")

    # Caso 1: Construcción de comando
    cmd = build_cmd("/usr/local/bin/backlog_codex", 4, 2, "groq")
    esperado = [
        "/usr/local/bin/backlog_codex",
        "--take",
        "4",
        "--parallel",
        "2",
        "--provider",
        "groq",
    ]
    assert cmd == esperado, f"Caso 1 falló: {cmd} != {esperado}"
    print("  ✓ Caso 1: build_cmd construye correctamente la lista de argumentos")

    # Caso 2: Parsing CLI
    args = parse_args(
        [
            "prog",
            "--take",
            "4",
            "--parallel",
            "2",
            "--provider",
            "groq",
            "--logfile",
            "/var/tmp/log",
        ]
    )
    assert args.executable == "/usr/local/bin/backlog_codex", (
        f"executable incorrecto: {args.executable}"
    )
    assert args.take == 4, f"take incorrecto: {args.take}"
    assert args.parallel == 2, f"parallel incorrecto: {args.parallel}"
    assert args.provider == "groq", f"provider incorrecto: {args.provider}"
    assert args.logfile == "/var/tmp/log", f"logfile incorrecto: {args.logfile}"
    print("  ✓ Caso 2: parse_args extrae correctamente los valores")

    # Caso 3: Ejecución con /bin/echo y redirección a archivo temporal
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".log") as tmp:
        log_path = tmp.name

    try:
        returncode = run_backlog(
            executable="/bin/echo",
            take=4,
            parallel=2,
            provider="groq",
            logfile=log_path,
            dry_run=False,
        )
        assert returncode == 0, f"returncode inesperado: {returncode}"

        with open(log_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        assert "groq" in contenido, (
            f"El contenido del log no contiene 'groq': {contenido}"
        )
        print("  ✓ Caso 3: run_backlog ejecuta correctamente y redirige salida")
    finally:
        os.unlink(log_path)

    print("PRUEBAS OK")


if __name__ == "__main__":
    # Si se invoca sin argumentos (solo el nombre del script), ejecutar pruebas
    if len(sys.argv) == 1:
        _ejecutar_pruebas()
    else:
        sys.exit(main())
