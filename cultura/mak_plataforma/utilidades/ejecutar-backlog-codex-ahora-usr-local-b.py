#!/usr/bin/env python3
"""
backlog_runner.py - Ejecuta el comando externo backlog_codex con parámetros,
capturando stdout/stderr en un archivo de log. Soporta modo dry-run y validación.
Solo utiliza la biblioteca estándar de Python 3.11.
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional

# Ruta fija del binario externo (según especificación)
BACKLOG_CODEX_PATH = "/usr/local/bin/backlog_codex"


def parse_args(argv: List[str]) -> argparse.Namespace:
    """
    Analiza los argumentos de la línea de comandos.
    Lanza SystemExit con código 2 si falta algún argumento obligatorio
    o si los valores no son válidos.
    """
    parser = argparse.ArgumentParser(
        description="Ejecuta backlog_codex con los parámetros indicados.",
        add_help=False  # No queremos que argparse maneje -h automáticamente
    )
    parser.add_argument("--take", type=int, required=True,
                        help="Número de elementos a tomar (debe ser > 0)")
    parser.add_argument("--parallel", type=int, required=True,
                        help="Número de procesos paralelos (debe ser > 0)")
    parser.add_argument("--provider", type=str, required=True,
                        help="Proveedor a utilizar (no vacío)")
    parser.add_argument("--log", type=str, required=True,
                        help="Ruta del archivo de log")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Modo simulación: no ejecuta el comando")

    # Parseamos; si faltan argumentos, argparse lanza SystemExit con código 2
    opts = parser.parse_args(argv)

    # Validaciones adicionales
    if opts.take <= 0:
        print("Error: --take debe ser un entero positivo (> 0).", file=sys.stderr)
        sys.exit(2)
    if opts.parallel <= 0:
        print("Error: --parallel debe ser un entero positivo (> 0).", file=sys.stderr)
        sys.exit(2)
    if not opts.provider.strip():
        print("Error: --provider no puede estar vacío.", file=sys.stderr)
        sys.exit(2)
    if not opts.log.strip():
        print("Error: --log no puede estar vacío.", file=sys.stderr)
        sys.exit(2)

    return opts


def build_command(opts: argparse.Namespace) -> List[str]:
    """
    Convierte los valores de opts en la lista de argumentos para subprocess.run.
    """
    cmd = [
        BACKLOG_CODEX_PATH,
        "--take", str(opts.take),
        "--parallel", str(opts.parallel),
        "--provider", opts.provider,
    ]
    return cmd


def run_backlog(cmd: List[str], log_path: str) -> int:
    """
    Ejecuta el comando cmd, redirigiendo stdout y stderr al archivo log_path.
    Devuelve el código de salida del proceso.
    """
    with open(log_path, "w", encoding="utf-8") as log_file:
        result = subprocess.run(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            # No se especifica shell; se ejecuta directamente el binario
        )
    return result.returncode


def main(argv: Optional[List[str]] = None) -> int:
    """
    Orquesta el flujo: parseo, construcción del comando, dry-run o ejecución.
    Devuelve el código de salida (0 en dry-run, o el código del proceso).
    """
    if argv is None:
        argv = sys.argv[1:]

    try:
        opts = parse_args(argv)
    except SystemExit as e:
        # Si argparse o nuestras validaciones lanzan SystemExit, lo propagamos
        # pero main debe devolver el código, no lanzar excepción.
        # Sin embargo, la especificación dice que parse_args lanza SystemExit,
        # y main debe imprimir errores en stderr. En ese caso, main no debería
        # atraparlo, o bien capturarlo y devolver el código.
        # Para cumplir con la interfaz, main debe devolver int, no lanzar.
        # Por lo tanto, capturamos SystemExit y devolvemos su código.
        return e.code

    cmd = build_command(opts)

    if opts.dry_run:
        # Modo simulación: no ejecutar nada
        print(f"[DRY-RUN] Comando a ejecutar: {' '.join(cmd)}", file=sys.stderr)
        print(f"[DRY-RUN] Log se escribiría en: {opts.log}", file=sys.stderr)
        return 0

    # Ejecución real
    return run_backlog(cmd, opts.log)


if __name__ == "__main__":
    # Si la variable de entorno BACKLOG_RUNNER_SELFTEST está definida,
    # ejecutamos los autotests con assert.
    if os.getenv("BACKLOG_RUNNER_SELFTEST"):
        # Caso 1 – Dry run
        args1 = ["--take", "1", "--parallel", "1", "--provider", "test",
                 "--log", "tmp1.log", "--dry-run"]
        opts1 = parse_args(args1)
        assert opts1.dry_run is True
        assert build_command(opts1) == [
            "/usr/local/bin/backlog_codex", "--take", "1",
            "--parallel", "1", "--provider", "test"
        ]
        result1 = main(args1)
        assert result1 == 0, f"Se esperaba 0, se obtuvo {result1}"

        # Caso 2 – Parámetro inválido (take=0)
        args2 = ["--take", "0", "--parallel", "2", "--provider", "groq",
                 "--log", "tmp2.log"]
        try:
            parse_args(args2)
            assert False, "Debe lanzar SystemExit"
        except SystemExit as e:
            assert e.code == 2, f"Se esperaba código 2, se obtuvo {e.code}"

        # Caso 3 – Ejecución real (asume que el binario existe y devuelve 0)
        args3 = ["--take", "3", "--parallel", "2", "--provider", "groq",
                 "--log", "tmp3.log"]
        result3 = main(args3)
        assert result3 == 0, f"Se esperaba 0, se obtuvo {result3}"
        assert os.path.getsize("tmp3.log") > 0, "El archivo de log está vacío"

        # Limpieza de archivos temporales (opcional)
        for f in ["tmp1.log", "tmp2.log", "tmp3.log"]:
            if os.path.exists(f):
                os.remove(f)

        print("PRUEBAS OK")
    else:
        # Ejecución normal: llamar a main con sys.argv[1:]
        sys.exit(main())
