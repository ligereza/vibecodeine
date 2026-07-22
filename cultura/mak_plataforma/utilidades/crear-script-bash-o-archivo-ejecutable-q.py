#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import subprocess
import sys
import tempfile

# Rutas fijas según especificación
CONFIG_PATH = "/etc/mak/ajustes_junta.json"
LOG_PATH = "/var/log/mak/auto_review.log"
RELOAD_CMD = "/opt/mak/bin/cadena_de_proveedores"
BACKLOG_CMD = "backlog_codex"
CRON_FILE = "/etc/cron.d/mak_provider_failover"  # No se modifica, solo referencia

# Valores por defecto
DEFAULT_CONFIG = {
    "provider_weights": {
        "cerebras": 0.60,
        "azure": 0.30,
        "groq": 0.10,
        "searxng": 0.00
    },
    "last_action_ts": "2026-07-20T15:46:05Z"
}

logger = None  # Se inicializa en main()


def setup_logging(log_path):
    """Configura el logger para archivo y consola."""
    global logger
    logger = logging.getLogger("auto_review")
    logger.setLevel(logging.DEBUG)

    # Asegurar que el directorio del log existe
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Handler para archivo
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Handler para consola (útil en pruebas)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def leer_config(config_path):
    """Lee el archivo de configuración. Si no existe, lo crea con valores por defecto."""
    if not os.path.exists(config_path):
        logger.info(f"Archivo de configuración {config_path} no existe. Creando con valores por defecto.")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logger.info(f"Archivo de configuración {config_path} creado con éxito.")
        return DEFAULT_CONFIG.copy()
    else:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Archivo de configuración {config_path} leído.")
        return config


def actualizar_config(config_path, nuevo_config):
    """Escribe la nueva configuración en el archivo."""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(nuevo_config, f, indent=4)
    logger.info(f"Archivo de configuración {config_path} actualizado.")


def ejecutar_comando(cmd, descripcion):
    """Ejecuta un comando y registra el resultado. Retorna True si éxito, False si error."""
    try:
        resultado = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if resultado.returncode == 0:
            logger.info(f"Comando '{descripcion}' ejecutado con éxito: {cmd}")
            return True
        else:
            logger.error(
                f"Comando '{descripcion}' falló con código {resultado.returncode}: "
                f"{resultado.stderr.strip()}"
            )
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"Comando '{descripcion}' excedió el tiempo de espera: {cmd}")
        return False
    except Exception as e:
        logger.error(f"Error ejecutando comando '{descripcion}': {e}")
        return False


def main(
    config_path=CONFIG_PATH,
    log_path=LOG_PATH,
    reload_cmd=RELOAD_CMD,
    backlog_cmd=BACKLOG_CMD
):
    """Función principal que orquesta las acciones del script."""
    setup_logging(log_path)

    # 1. Leer/actualizar configuración
    config = leer_config(config_path)
    nuevo_config = {
        "provider_weights": DEFAULT_CONFIG["provider_weights"],
        "last_action_ts": DEFAULT_CONFIG["last_action_ts"]
    }
    actualizar_config(config_path, nuevo_config)

    # 2. Recargar cadena de proveedores
    ejecutar_comando(reload_cmd, "recargar cadena de proveedores")

    # 3. Encolar procesamiento automático de revisiones codex
    exito = ejecutar_comando(backlog_cmd, "encolar procesamiento automático de revisiones codex")
    if not exito:
        logger.error("El comando backlog_codex falló. Se registró el error.")
    else:
        logger.info("Procesamiento automático de revisiones codex encolado con éxito.")


if __name__ == "__main__":
    # ========== CASOS DE PRUEBA ==========
    def pruebas():
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "ajustes_junta.json")
            log_path = os.path.join(tmpdir, "auto_review.log")

            # Crear comandos falsos
            reload_script = os.path.join(tmpdir, "cadena_de_proveedores")
            backlog_script = os.path.join(tmpdir, "backlog_codex")

            # Script de recarga siempre exitoso
            with open(reload_script, 'w') as f:
                f.write("#!/bin/bash\nexit 0")
            os.chmod(reload_script, 0o755)

            def establecer_backlog_exit(codigo):
                with open(backlog_script, 'w') as f:
                    f.write(f"#!/bin/bash\nexit {codigo}")
                os.chmod(backlog_script, 0o755)

            # --- Caso 1: Config no existe ---
            establecer_backlog_exit(0)
            if os.path.exists(config_path):
                os.remove(config_path)
            main(config_path=config_path, log_path=log_path,
                 reload_cmd=reload_script, backlog_cmd=backlog_script)

            assert os.path.exists(config_path), "El archivo de configuración debería haberse creado"
            with open(config_path, 'r') as f:
                config = json.load(f)
            assert config == DEFAULT_CONFIG, f"Configuración incorrecta: {config}"
            with open(log_path, 'r') as f:
                log = f.read()
            assert "creado con éxito" in log, "El log debería indicar creación"
            print("Caso 1 OK")

            # --- Caso 2: Config existe con valores diferentes ---
            config_anterior = {
                "provider_weights": {"cerebras": 0.40, "azure": 0.30, "groq": 0.20, "searxng": 0.10},
                "last_action_ts": "2025-01-01T00:00:00Z"
            }
            with open(config_path, 'w') as f:
                json.dump(config_anterior, f)
            # Limpiar log
            open(log_path, 'w').close()

            main(config_path=config_path, log_path=log_path,
                 reload_cmd=reload_script, backlog_cmd=backlog_script)

            with open(config_path, 'r') as f:
                config = json.load(f)
            assert config == DEFAULT_CONFIG, f"La configuración debería haberse actualizado: {config}"
            with open(log_path, 'r') as f:
                log = f.read()
            assert "actualizado" in log, "El log debería indicar actualización"
            print("Caso 2 OK")

            # --- Caso 3: backlog_codex falla ---
            establecer_backlog_exit(1)
            open(log_path, 'w').close()

            main(config_path=config_path, log_path=log_path,
                 reload_cmd=reload_script, backlog_cmd=backlog_script)

            with open(log_path, 'r') as f:
                log = f.read()
            assert "falló" in log or "Error" in log, "El log debería contener un error"
            print("Caso 3 OK")

            print("PRUEBAS OK")

    pruebas()
