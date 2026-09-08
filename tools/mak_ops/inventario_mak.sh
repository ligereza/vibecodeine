#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

ROOT="/home/mak"
DESKTOP="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
[[ -d "$DESKTOP" ]] || DESKTOP="$ROOT/Escritorio"
[[ -d "$DESKTOP" ]] || DESKTOP="$ROOT/Desktop"
mkdir -p "$DESKTOP"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$DESKTOP/MAK-inventario-macro-$STAMP.tsv"

{
  printf '# Inventario macro de %s\n' "$ROOT"
  printf '# Solo metadatos, nombres y tamaños; no se leyó contenido.\n'
  printf '# GoogleDrive, OneDrive y curatoria_inbox se registran como frontera y no se recorren.\n\n'

  printf '## TOP_LEVEL_SIZE_BYTES\n'
  printf 'bytes\truta\n'

  while IFS= read -r -d '' path; do
    case "$path" in
      "$ROOT/GoogleDrive"|"$ROOT/OneDrive"|"$ROOT/curatoria_inbox")
        continue
        ;;
    esac
    size="$(du -sx --bytes --apparent-size -- "$path" 2>/dev/null | awk '{print $1}')"
    [[ -n "$size" ]] && printf '%s\t%s\n' "$size" "$path"
  done < <(
    find -P "$ROOT" -xdev -mindepth 1 -maxdepth 1 \
      \( -type d -o -type l \) -print0
  )

  printf '\n## DIRECTORIES_AND_SYMLINKS\n'
  printf 'tipo\truta\tmetadata_bytes\tdevice\tinode\tnlink\tmtime\n'

  find -P "$ROOT" -xdev \
    \( -path "$ROOT/GoogleDrive" -o \
       -path "$ROOT/OneDrive" -o \
       -path "$ROOT/curatoria_inbox" \) -prune -o \
    \( -type d -o -type l \) \
    -printf '%y\t%p\t%s\t%D\t%i\t%n\t%TY-%Tm-%TdT%TH:%TM:%TS\n'
} > "$OUT"

chmod 0644 "$OUT"
printf 'Inventario creado: %s\n' "$OUT"
sha256sum "$OUT"
