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
