#!/usr/bin/env python3
"""
mak_admin.py — Administración de la cadena de proveedores MAK.

Este módulo permite actualizar la configuración de pesos de proveedores,
registrar marcas de tiempo y mantenimiento, recargar la cadena, gestionar
entradas de cron y encolar revisiones. Expone una CLI y funciones
reutilizables, usando exclusivamente la biblioteca estándar de Python 3.11.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Funciones públicas (llamables desde CLI o pruebas unitarias)
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    """
    Carga la configuración desde un archivo JSON.

    Args:
        path: Ruta al archivo de configuración.

    Returns:
        Diccionario con la configuración cargada. Si el archivo no existe
        o está vacío, devuelve un diccionario vacío.
    """
    p = Path(path)
    if not p.exists():
        return {}
    texto = p.read_text(encoding="utf-8").strip()
    if not texto:
        return {}
    return json.loads(texto)


def update_provider_weights(cfg: dict, weights: dict) -> None:
    """
    Actualiza (o crea) la clave 'provider_weights' en el diccionario de
    configuración.

    Args:
        cfg: Diccionario de configuración (mutado in‑place).
        weights: Diccionario con los nuevos pesos de proveedores.
    """
    cfg["provider_weights"] = weights


def add_timestamp(cfg: dict, key: str, ts: str) -> None:
    """
    Agrega una marca de tiempo bajo la clave indicada.

    Args:
        cfg: Diccionario de configuración (mutado in‑place).
        key: Nombre de la clave donde guardar la marca.
        ts: Cadena con la marca de tiempo en formato ISO 8601.
    """
    cfg[key] = ts


def record_maintenance(cfg: dict, value: str) -> None:
    """
    Registra un valor de mantenimiento bajo la clave 'last_maintenance'.

    Args:
        cfg: Diccionario de configuración (mutado in‑place).
        value: Valor descriptivo de la acción de mantenimiento.
    """
    cfg["last_maintenance"] = value


def save_config(cfg: dict, path: str) -> None:
    """
    Guarda el diccionario de configuración en un archivo JSON.

    Args:
        cfg: Diccionario a persistir.
        path: Ruta de destino del archivo.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8")


def reload_chain(config_path: str) -> subprocess.CompletedProcess:
    """
    Ejecuta el comando de recarga de la cadena de proveedores.

    Args:
        config_path: Ruta al archivo de configuración que usará el comando.

    Returns:
        Instancia de subprocess.CompletedProcess con el resultado.
    """
    cmd = ["cadena_de_proveedores", "reload", "--config", config_path]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def create_cron_entry(cron_path: str, line: str) -> None:
    """
    Crea o sobrescribe un archivo de cron con la línea especificada.

    Args:
        cron_path: Ruta donde se escribirá el archivo cron.
        line: Línea completa de cron (incluye schedule, usuario y comando).
    """
    p = Path(cron_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(line.strip() + "\n", encoding="utf-8")


def enqueue_review(cmd_template: str, **kwargs) -> subprocess.CompletedProcess:
    """
    Ejecuta un comando de encolado de revisión usando una plantilla.

    La plantilla puede contener marcadores {clave} que se sustituyen con los
    valores proporcionados en kwargs.

    Args:
        cmd_template: Plantilla del comando (ej. "backlog_codex enqueue ...").
        **kwargs: Valores para sustituir en la plantilla.

    Returns:
        Instancia de subprocess.CompletedProcess con el resultado.
    """
    cmd_str = cmd_template.format(**kwargs)
    # Dividimos respetando comillas simples/dobles (simplificado: split simple)
    partes = cmd_str.split()
    return subprocess.run(partes, capture_output=True, text=True, check=False)


def refresh_chain(config_path: str) -> subprocess.CompletedProcess:
    """
    Ejecuta el comando de refresco de la cadena de proveedores.

    Args:
        config_path: Ruta al archivo de configuración que usará el comando.

    Returns:
        Instancia de subprocess.CompletedProcess con el resultado.
    """
    cmd = ["cadena_de_proveedores", "refresh", "--config", config_path]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


# ---------------------------------------------------------------------------
# CLI principal
# ---------------------------------------------------------------------------

def _ejecutar_paso(nombre: str, resultado: subprocess.CompletedProcess) -> None:
    """
    Verifica el código de retorno de un paso y aborta si es distinto de 0.

    Args:
        nombre: Descripción legible del paso.
        resultado: Resultado del subproceso ejecutado.

    Raises:
        SystemExit: Si returncode != 0, mostrando stderr.
    """
    if resultado.returncode != 0:
        print(f"Error en paso '{nombre}': {resultado.stderr.strip()}",
              file=sys.stderr)
        sys.exit(resultado.returncode)


def main(argv=None) -> None:
    """
    Punto de entrada de la CLI. Parsea argumentos y ejecuta el flujo completo.

    Args:
        argv: Lista de argumentos (por defecto sys.argv[1:]).
    """
    parser = argparse.ArgumentParser(
        description="Administración de la cadena de proveedores MAK."
    )
    parser.add_argument("--config", required=True,
                        help="Ruta al archivo JSON de configuración.")
    parser.add_argument("--weights", required=True,
                        help="JSON con los nuevos pesos de proveedores.")
    parser.add_argument("--timestamp", required=True,
                        help="Marca de tiempo ISO 8601 para last_action_ts.")
    parser.add_argument("--cron", required=True,
                        help="Ruta donde crear/actualizar el archivo cron.")
    parser.add_argument("--cron-line", required=True,
                        help="Línea completa de cron a escribir.")
    parser.add_argument("--enqueue", required=True,
                        help="Plantilla del comando de encolado.")
    parser.add_argument("--maintenance-key", default="last_maintenance",
                        help="Clave bajo la cual registrar mantenimiento.")
    parser.add_argument("--maintenance-val", required=True,
                        help="Valor de mantenimiento a registrar.")
    parser.add_argument("--self-test", action="store_true",
                        help="Ejecuta las pruebas unitarias internas y sale.")

    args = parser.parse_args(argv)

    # Modo auto‑test
    if args.self_test:
        ejecutar_pruebas()
        return

    # 1. Cargar configuración
    cfg = load_config(args.config)

    # 2. Actualizar pesos de proveedores
    pesos = json.loads(args.weights)
    update_provider_weights(cfg, pesos)

    # 3. Insertar marca de tiempo
    add_timestamp(cfg, "last_action_ts", args.timestamp)

    # 4. Registrar mantenimiento
    record_maintenance(cfg, args.maintenance_val)

    # 5. Guardar configuración
    save_config(cfg, args.config)

    # 6. Recargar cadena
    cp_reload = reload_chain(args.config)
    _ejecutar_paso("reload_chain", cp_reload)

    # 7. Crear/actualizar archivo cron
    create_cron_entry(args.cron, args.cron_line)

    # 8. Encolar revisión
    cp_enqueue = enqueue_review(args.enqueue)
    _ejecutar_paso("enqueue_review", cp_enqueue)

    # 9. Refrescar cadena
    cp_refresh = refresh_chain(args.config)
    _ejecutar_paso("refresh_chain", cp_refresh)

    print("Flujo de administración completado exitosamente.")


# ---------------------------------------------------------------------------
# Pruebas unitarias (auto‑contenidas, sin frameworks externos)
# ---------------------------------------------------------------------------

def ejecutar_pruebas() -> None:
    """
    Ejecuta todos los casos de prueba usando assert y tempfile.
    Si todas pasan, imprime 'PRUEBAS OK'.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # --- Caso 1: Actualización básica ---
        archivo_cfg = tmp_path / "ajustes_junta.json"
        archivo_cfg.write_text("{}", encoding="utf-8")

        cfg = load_config(str(archivo_cfg))
        assert cfg == {}, "Carga inicial debe ser diccionario vacío"

        pesos = {"cerebras": 0.60, "azure": 0.30, "groq": 0.10, "searxng": 0.00}
        update_provider_weights(cfg, pesos)
        add_timestamp(cfg, "last_action_ts", "2026-07-20T15:46:05Z")
        record_maintenance(cfg, "auto_review_launch")
        save_config(cfg, str(archivo_cfg))

        resultado = json.loads(archivo_cfg.read_text(encoding="utf-8"))
        esperado = {
            "provider_weights": pesos,
            "last_action_ts": "2026-07-20T15:46:05Z",
            "last_maintenance": "auto_review_launch"
        }
        assert resultado == esperado, f"No coincide: {resultado} != {esperado}"

        # --- Caso 2: Comando reload (mock) ---
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="OK", stderr=""
            )
            cp = reload_chain("/etc/mak/ajustes_junta.json")
            assert cp.returncode == 0
            assert cp.stdout == "OK"
            mock_run.assert_called_once_with(
                ["cadena_de_proveedores", "reload", "--config",
                 "/etc/mak/ajustes_junta.json"],
                capture_output=True, text=True, check=False
            )

        # --- Caso 3: Creación/actualización de cron ---
        cron_path = tmp_path / "cron_test"
        linea = ("*/5 * * * * root /opt/mak/bin/provider_health_check "
                 "--config /etc/mak/ajustes_junta.json --threshold 60 "
                 "--action reload")
        create_cron_entry(str(cron_path), linea)
        contenido = cron_path.read_text(encoding="utf-8").strip()
        assert contenido == linea, f"Contenido cron no coincide: {contenido}"

    print("PRUEBAS OK")


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
