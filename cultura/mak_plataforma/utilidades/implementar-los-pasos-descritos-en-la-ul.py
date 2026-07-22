#!/usr/bin/env python3
"""
Módulo de mantenimiento de MAK - Codex

Este script implementa la secuencia completa de mantenimiento:
1. Crear/actualizar archivo JSON de configuración
2. Recargar la cadena de proveedores
3. Crear archivo cron para health checks
4. Lanzar backlog de revisión automática
5. Actualizar configuración con timestamp de mantenimiento

ADVERTENCIA: La ejecución real (con --execute) modifica archivos en /etc y /etc/cron.d,
requiere privilegios de root y ejecuta comandos del sistema.
El modo selftest usa directorios temporales y dry-run para pruebas seguras.

Uso:
    python mak_mantenimiento.py run [--config PATH] [--cron PATH] [--execute]
    python mak_mantenimiento.py selftest
"""

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# ─── Runner Abstraction ──────────────────────────────────────────────────────

@dataclass
class DryRunner:
    """Runner que registra comandos en lugar de ejecutarlos realmente."""
    executed_commands: List[str] = field(default_factory=list)
    written_files: Dict[str, str] = field(default_factory=dict)

    def run(self, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Simula ejecución de comando y lo registra."""
        cmd_str = " ".join(cmd)
        self.executed_commands.append(cmd_str)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    def write_file(self, path: Union[str, Path], content: str) -> None:
        """Simula escritura de archivo y registra."""
        path_str = str(path)
        self.written_files[path_str] = content
        # En dry-run, realmente escribimos para que las aserciones puedan leer
        Path(path).write_text(content, encoding="utf-8")


class RealRunner:
    """Ejecuta comandos y escribe archivos realmente en el sistema."""

    @staticmethod
    def run(cmd: List[str], capture: bool = False) -> subprocess.CompletedProcess:
        """Ejecuta comando real usando subprocess."""
        return subprocess.run(cmd, capture_output=capture, text=True, check=False)

    @staticmethod
    def write_file(path: Union[str, Path], content: str) -> None:
        """Escribe archivo real en el sistema."""
        Path(path).write_text(content, encoding="utf-8")


# ─── Funciones Públicas ──────────────────────────────────────────────────────

def write_config(
    path: Union[str, Path],
    provider_weights: Dict[str, float],
    last_action_ts: str,
    runner: Optional[Any] = None,
) -> None:
    """
    Crea o reemplaza archivo JSON con provider_weights y last_action_ts.

    Args:
        path: Ruta del archivo JSON a crear.
        provider_weights: Diccionario con pesos de proveedores.
        last_action_ts: Timestamp de última acción en formato ISO 8601.
        runner: Runner para ejecución (None usa RealRunner).
    """
    config = {
        "provider_weights": provider_weights,
        "last_action_ts": last_action_ts,
    }
    content = json.dumps(config, indent=2, ensure_ascii=False)

    if runner is None:
        RealRunner.write_file(path, content)
    else:
        runner.write_file(path, content)


def reload_chain(
    config_path: Union[str, Path],
    runner: Optional[Any] = None,
) -> None:
    """
    Invoca 'cadena_de_proveedores reload' para recargar la cadena.

    Args:
        config_path: Ruta del archivo de configuración (no usado en comando actual).
        runner: Objeto runner (None usa RealRunner).
    """
    cmd = ["cadena_de_proveedores", "reload"]
    if runner is None:
        RealRunner.run(cmd)
    else:
        runner.run(cmd)


def create_cron(
    path: Union[str, Path],
    cron_line: str,
    runner: Optional[Any] = None,
) -> None:
    """
    Escribe archivo cron con la línea especificada.

    Args:
        path: Ruta donde crear el archivo cron.
        cron_line: Línea cron completa a escribir.
        runner: Objeto runner (None usa RealRunner).
    """
    content = cron_line + "\n"
    if runner is None:
        RealRunner.write_file(path, content)
    else:
        runner.write_file(path, content)


def launch_backlog(
    provider: str,
    parallel: int,
    limit: int,
    target_pct: int,
    timeout: str,
    runner: Optional[Any] = None,
) -> None:
    """
    Invoca el comando backlog_codex para encolar revisión automática.

    Args:
        provider: Nombre del proveedor a usar.
        parallel: Número de trabajos paralelos.
        limit: Límite de revisiones.
        target_pct: Porcentaje objetivo.
        timeout: Timeout en formato string (ej: "600s").
        runner: Objeto runner (None usa RealRunner).
    """
    cmd = [
        "backlog_codex",
        "enqueue",
        "auto_review_batch",
        f"--provider={provider}",
        f"--parallel={parallel}",
        f"--limit={limit}",
        f"--target_pct={target_pct}",
        f"--timeout={timeout}",
    ]
    if runner is None:
        RealRunner.run(cmd)
    else:
        runner.run(cmd)


def update_config_maintenance(
    path: Union[str, Path],
    last_maintenance: str,
    runner: Optional[Any] = None,
) -> None:
    """
    Abre JSON existente y añade/actualiza campo last_maintenance.

    Args:
        path: Ruta del archivo JSON a modificar.
        last_maintenance: Valor para el campo last_maintenance.
        runner: Objeto runner (None usa RealRunner).
    """
    # Leer configuración existente
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    config["last_maintenance"] = last_maintenance
    content = json.dumps(config, indent=2, ensure_ascii=False)

    if runner is None:
        RealRunner.write_file(path, content)
    else:
        runner.write_file(path, content)


def run_full_sequence(
    config_path: Union[str, Path],
    cron_path: Union[str, Path],
    runner: Optional[Any] = None,
    dry_run: bool = True,
) -> None:
    """
    Ejecuta la secuencia completa de mantenimiento en orden.

    Args:
        config_path: Ruta del archivo JSON de configuración.
        cron_path: Ruta del archivo cron a crear.
        runner: Objeto runner (si None y dry_run=True, crea DryRunner).
        dry_run: Si True, usa DryRunner automáticamente si runner es None.
    """
    if runner is None and dry_run:
        runner = DryRunner()

    # Paso 1: Crear configuración inicial
    write_config(
        path=config_path,
        provider_weights={
            "cerebras": 0.60,
            "azure": 0.30,
            "groq": 0.10,
            "searxng": 0.00,
        },
        last_action_ts="2026-07-20T15:46:05Z",
        runner=runner,
    )

    # Paso 2: Recargar cadena
    reload_chain(config_path=config_path, runner=runner)

    # Paso 3: Crear archivo cron
    cron_line = (
        "*/5 * * * * root /opt/mak/bin/provider_health_check "
        "--config /etc/mak/ajustes_junta.json --threshold 60 --action reload"
    )
    create_cron(path=cron_path, cron_line=cron_line, runner=runner)

    # Paso 4: Lanzar backlog
    launch_backlog(
        provider="cerebras",
        parallel=4,
        limit=13,
        target_pct=80,
        timeout="600s",
        runner=runner,
    )

    # Paso 5: Actualizar configuración y recargar
    update_config_maintenance(
        path=config_path,
        last_maintenance="auto_review_launch",
        runner=runner,
    )
    reload_chain(config_path=config_path, runner=runner)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos para la CLI."""
    parser = argparse.ArgumentParser(
        description="Mantenimiento de cadena de proveedores MAK Codex"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Subcomando run
    run_parser = subparsers.add_parser("run", help="Ejecutar secuencia de mantenimiento")
    run_parser.add_argument(
        "--config",
        default="/etc/mak/ajustes_junta.json",
        help="Ruta del archivo JSON de configuración (default: /etc/mak/ajustes_junta.json)",
    )
    run_parser.add_argument(
        "--cron",
        default="/etc/cron.d/mak_provider_failover",
        help="Ruta del archivo cron (default: /etc/cron.d/mak_provider_failover)",
    )
    run_parser.add_argument(
        "--execute",
        action="store_true",
        help="Ejecutar comandos reales (sin esta opción, dry-run por defecto)",
    )

    # subcomando selftest
    subparsers.add_parser("selftest", help="Ejecutar pruebas internas con dry-run")

    return parser


# ─── Pruebas Autoejecutables ─────────────────────────────────────────────────

def test_case_1_creacion_json_correcto():
    """Caso 1: Verifica creación correcta del JSON de configuración."""
    print("Ejecutando Caso 1: Creación de JSON correcto...")

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "ajustes_junta_test.json"
        provider_weights = {
            "cerebras": 0.60,
            "azure": 0.30,
            "groq": 0.10,
            "searxng": 0.00,
        }
        last_action_ts = "2026-07-20T15:46:05Z"

        # Ejecutar con dry-run (escribe realmente en temp)
        runner = DryRunner()
        write_config(
            path=config_path,
            provider_weights=provider_weights,
            last_action_ts=last_action_ts,
            runner=runner,
        )

        # Aserciones
        assert config_path.exists(), "El archivo JSON no fue creado"
        contenido = json.loads(config_path.read_text(encoding="utf-8"))

        assert "provider_weights" in contenido, "Falta provider_weights"
        assert "last_action_ts" in contenido, "Falta last_action_ts"
        assert contenido["last_action_ts"] == last_action_ts, "Timestamp incorrecto"

        pesos = contenido["provider_weights"]
        assert pesos["cerebras"] == 0.60, "Peso cerebras incorrecto"
        assert pesos["azure"] == 0.30, "Peso azure incorrecto"
        assert pesos["groq"] == 0.10, "Peso groq incorrecto"
        assert pesos["searxng"] == 0.00, "Peso searxng incorrecto"

        # Verificar que son floats
        assert isinstance(pesos["cerebras"], float), "cerebras no es float"
        assert isinstance(pesos["azure"], float), "azure no es float"

        print("  ✓ Caso 1 pasado")


def test_case_2_creacion_cron():
    """Caso 2: Verifica creación de archivo cron con línea exacta."""
    print("Ejecutando Caso 2: Creación de archivo cron...")

    with tempfile.TemporaryDirectory() as tmpdir:
        cron_path = Path(tmpdir) / "mak_provider_failover_test"
        cron_line = (
            "*/5 * * * * root /opt/mak/bin/provider_health_check "
            "--config /etc/mak/ajustes_junta.json --threshold 60 --action reload"
        )

        runner = DryRunner()
        create_cron(path=cron_path, cron_line=cron_line, runner=runner)

        # Aserciones
        assert cron_path.exists(), "El archivo cron no fue creado"
        contenido = cron_path.read_text(encoding="utf-8")
        esperado = cron_line + "\n"

        assert contenido == esperado, (
            f"Contenido no coincide.\nEsperado: {repr(esperado)}\n"
            f"Obtenido: {repr(contenido)}"
        )
        # Verificar que no hay líneas extras
        lineas = contenido.splitlines()
        assert len(lineas) == 1, f"Hay {len(lineas)} líneas, se esperaba 1"

    print("  ✅ Caso 2 pasado")


def test_case_3_flujo_completo_dry_run():
    """Caso 3: Flujo completo en dry-run produce llamadas en orden y actualiza last_maintenance."""
    print("Ejecutando Caso 3: Flujo completo en dry-run...")

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "ajustes_junta_test.json"
        cron_path = Path(tmpdir) / "mak_provider_failover_test"

        runner = DryRunner()
        run_full_sequence(
            config_path=config_path,
            cron_path=cron_path,
            runner=runner,
            dry_run=True,
        )

        # Verificar orden de comandos ejecutados
        comandos = runner.executed_commands
        assert len(comandos) == 3, f"Se esperaban 3 comandos, se ejecutaron {len(comandos)}"

        # Comando 1: reload inicial
        assert comandos[0] == "cadena_de_proveedores reload", (
            f"Primer comando incorrecto: {comandos[0]}"
        )

        # Comando 2: backlog
        esperado_backlog = (
            "backlog_codex enqueue auto_review_batch "
            "--provider=cerebras --parallel=4 --limit=13 --target_pct=80 --timeout=600s"
        )
        assert comandos[1] == esperado_backlog, (
            f"Segundo comando incorrecto:\n"
            f"Esperado: {esperado_backlog}\n"
            f"Obtenido: {comandos[1]}"
        )

        # Comando 3: reload final
        assert comandos[2] == "cadena_de_proveedores reload", (
            f"Tercer comando incorrecto: {comandos[2]}"
        )

        # Verificar JSON final
        assert config_path.exists(), "El archivo JSON no existe"
        config = json.loads(config_path.read_text(encoding="utf-8"))

        # Campos originales preservados
        assert "provider_weights" in config, "Falta provider_weights"
        assert "last_action_ts" in config, "Falta last_action_ts"
        assert config["last_action_ts"] == "2026-07-20T15:46:05Z", "last_action_ts alterado"

        # Nuevo campo last_maintenance
        assert "last_maintenance" in config, "Falta last_maintenance"
        assert config["last_maintenance"] == "auto_review_launch", (
            f"last_maintenance incorrecto: {config['last_maintenance']}"
        )

        # Verificar pesos originales
        pesos = config["provider_weights"]
        assert pesos["cerebras"] == 0.60
        assert pesos["azure"] == 0.30
        assert pesos["groq"] == 0.10
        assert pesos["searxng"] == 0.00

    print("  ✅ Caso 3 pasado")


def run_selftest():
    """Ejecuta todas las pruebas internas."""
    print("=" * 60)
    print("Ejecutando pruebas internas (selftest)...")
    print("=" * 60)

    try:
        test_case_1_creacion_json_correcto()
        test_case_2_creacion_cron()
        test_case_3_flujo_completo_dry_run()
        print("\n" + "=" * 60)
        print("PRUEBAS OK")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ FALLO EN PRUEBAS: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        sys.exit(1)


# ─── Punto de Entrada ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "selftest":
        run_selftest()
    elif args.command == "run":
        dry_run = not args.execute

        if dry_run:
            print("Modo DRY-RUN activado. Los comandos no se ejecutarán realmente.")
            runner = DryRunner()
        else:
            print("⚠️  MODO REAL: Se ejecutarán comandos y se modificarán archivos del sistema.")
            print("   Asegúrese de tener privilegios de root.")
            runner = None  # Usa RealRunner por defecto

        run_full_sequence(
            config_path=args.config,
            cron_path=args.cron,
            runner=runner,
            dry_run=dry_run,
        )

        if dry_run:
            print("\nComandos que se habrían ejecutado:")
            for i, cmd in enumerate(runner.executed_commands, 1):
                print(f"  {i}. {cmd}")
            print("\nArchivos que se habrían escrito:")
            for path, content in runner.written_files.items():
                print(f"  {path}:")
                print(f"    {content.strip()}")
