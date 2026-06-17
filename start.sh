#!/usr/bin/env bash
# Lanzador rápido para flujo.
# Evita tener que activar el venv manualmente.

set -euo pipefail

# Ubicarse en la raíz del proyecto
cd "$(dirname "$0")"

echo "🚀 Iniciando FLUJO // Dimensiones del Orden..."

# Ejecutar la app usando el python del entorno virtual directamente
./.venv/Scripts/python scripts/app.py
