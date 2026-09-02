#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

ROOT="/"
HOME_MAK="/home/mak"
DESKTOP="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
[[ -d "$DESKTOP" ]] || DESKTOP="$HOME_MAK/Escritorio"
[[ -d "$DESKTOP" ]] || DESKTOP="$HOME_MAK/Desktop"
mkdir -p "$DESKTOP"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$DESKTOP/LINUX-externo-inventario-$STAMP.tsv"
ERR="$(mktemp)"
trap 'rm -f "$ERR"' EXIT

if [[ "$EUID" -ne 0 ]]; then
  sudo -v
  SUDO=(sudo)
else
  SUDO=()
fi

{
  printf '# Inventario externo al árbol %s\n' "$HOME_MAK"
  printf '# Solo metadatos, nombres y tamaños; no se leyó contenido.\n'
  printf '# proc, sys, dev, run, home/mak, media y mnt no se recorren.\n\n'

  printf '## MOUNTS\n'
  "${SUDO[@]}" findmnt -R / 2>/dev/null || true

  printf '\n## ROOT_SIZES_BYTES\n'
  printf 'bytes\truta\n'
  for path in /etc /usr /usr/local /opt /var /tmp /media /mnt /srv; do
    [[ -e "$path" ]] || continue
    size="$("${SUDO[@]}" du -sx --bytes --apparent-size -- "$path" 2>/dev/null | awk '{print $1}')"
    [[ -n "$size" ]] && printf '%s\t%s\n' "$size" "$path"
  done

  printf '\n## DIRECTORIES_AND_SYMLINKS\n'
  printf 'tipo\truta\tmetadata_bytes\tdevice\tinode\tnlink\tmtime\n'
  "${SUDO[@]}" find -P "$ROOT" -xdev \
    \( -path /proc -o \
       -path /sys -o \
       -path /dev -o \
       -path /run -o \
       -path "$HOME_MAK" -o \
       -path /media -o \
       -path /mnt \) -prune -o \
    \( -type d -o -type l \) \
    -printf '%y\t%p\t%s\t%D\t%i\t%n\t%TY-%Tm-%TdT%TH:%TM:%TS\n' 2>"$ERR" || true

  if [[ -s "$ERR" ]]; then
    printf '\n## FIND_WARNINGS\n'
    cat "$ERR"
  fi
} > "$OUT"

chmod 0644 "$OUT"
printf 'Inventario creado: %s\n' "$OUT"
sha256sum "$OUT"
