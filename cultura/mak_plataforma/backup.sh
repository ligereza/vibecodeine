#!/bin/bash
# backup.sh -- respaldo diario del archivo del organismo (7 dias de retencion)
set -eu
DEST="$HOME/backups"
mkdir -p "$DEST"
FECHA=$(date +%Y%m%d)
ARCHIVO="$DEST/mak-$FECHA.tar.gz"
cd "$HOME"
tar -czf "$ARCHIVO" \
  --ignore-failed-read \
  research/informes research/paneles research/cadenas \
  research/refutaciones research/correlaciones research/grafos \
  research/memoria codex/piezas codex/revisiones lenguaje/lexico \
  GENESIS.md 2>/dev/null || true
find "$DEST" -name "mak-*.tar.gz" -mtime +7 -delete
echo "backup: $ARCHIVO ($(du -h "$ARCHIVO" | cut -f1))"

# Cloud is an explicit temporary support path, not a hidden dependency of the
# local backup. Enable it only for a run that has an authenticated Azure CLI:
#   MAK_AZURE_BACKUP_UPLOAD=1 ./backup.sh
# Authentication stays in `az login`; no storage key or connection string is
# accepted here. A private Blob container is the durable copy that remains
# available while MAK is powered off.
if [ "${MAK_AZURE_BACKUP_UPLOAD:-0}" = "1" ]; then
    AZ_BIN="${MAK_AZ_BIN:-$HOME/.local/bin/az}"
    ACCOUNT="${MAK_AZURE_STORAGE_ACCOUNT:-makloud}"
    CONTAINER="${MAK_AZURE_STORAGE_CONTAINER:-mak-backups}"
    if [ ! -x "$AZ_BIN" ]; then
        echo "backup: Azure CLI no disponible en $AZ_BIN" >&2
        exit 1
    fi
    "$AZ_BIN" storage container create \
        --account-name "$ACCOUNT" \
        --name "$CONTAINER" \
        --auth-mode login \
        --public-access off \
        --only-show-errors >/dev/null
    "$AZ_BIN" storage blob upload \
        --account-name "$ACCOUNT" \
        --container-name "$CONTAINER" \
        --name "mak-$FECHA.tar.gz" \
        --file "$ARCHIVO" \
        --auth-mode login \
        --overwrite true \
        --only-show-errors >/dev/null
    echo "backup remoto: https://$ACCOUNT.blob.core.windows.net/$CONTAINER/mak-$FECHA.tar.gz"
fi
