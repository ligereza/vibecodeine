#!/usr/bin/env bash
set -e

URL="$1"
NAME="$2"

if [ -z "$URL" ]; then
  echo "Uso: bash scripts/link_external_repo.sh https://github.com/usuario/repo.git nombre-opcional"
  exit 1
fi

if [ -z "$NAME" ]; then
  NAME=$(basename "$URL" .git)
fi

mkdir -p _external
DEST="_external/$NAME"

if [ -d "$DEST/.git" ]; then
  echo "Repo externo ya existe. Actualizando: $DEST"
  git -C "$DEST" pull --ff-only || true
else
  echo "Clonando repo externo en $DEST"
  git clone "$URL" "$DEST"
fi

echo "Repo externo disponible en: $DEST"
echo "Nota: _external/ está en .gitignore, no se subirá dentro del repo de checkpoints."
