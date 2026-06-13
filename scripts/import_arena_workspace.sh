#!/usr/bin/env bash
set -e

ZIP_PATH="$1"
DEST="imports/arena_$(date +%Y-%m-%d_%H-%M)"

if [ -z "$ZIP_PATH" ]; then
  echo "Uso: bash scripts/import_arena_workspace.sh /ruta/al/workspace.zip"
  exit 1
fi

if [ ! -f "$ZIP_PATH" ]; then
  echo "No existe el zip: $ZIP_PATH"
  exit 1
fi

mkdir -p "$DEST"
unzip -q "$ZIP_PATH" -d "$DEST"

echo "Workspace importado en: $DEST"
echo "Revisa archivos, elimina privados/pesados si corresponde, luego ejecuta:"
echo "bash scripts/git_checkpoint.sh \"import arena workspace $(date +%Y-%m-%d)\""
