#!/usr/bin/env bash
# Etapa 3 del pipeline WIN->MAK->OneDrive: archiva una carpeta YA curada
# hacia OneDrive (remote rclone existente "onedrive:", cuenta con mas
# espacio). Reusa infraestructura ya montada en MAK -- NO configura
# credenciales nuevas. Si el remote no existe/esta roto, este script lo
# reporta y no inventa nada.
#
# Seguro por diseno: copy -> rclone check -> recien borra local. Nunca usa
# "move" a ciegas.
#
# Vive en MAK en ~/curatoria/onedrive_archivar.sh (copia espejo de
# referencia en el repo).
#
# Uso:
#   onedrive_archivar.sh                  # lista candidatas (encolado + inbox)
#   onedrive_archivar.sh <ruta_local>      # sube <ruta_local> a
#                                           # onedrive:curatoria_archivo/<nombre>
set -euo pipefail

REMOTE="onedrive"
REMOTE_BASE="${REMOTE}:curatoria_archivo"
INBOX="$HOME/curatoria_inbox"
ENCOLADO="$HOME/curatoria_encolado"

if ! command -v rclone >/dev/null 2>&1; then
    echo "ERROR: rclone no esta instalado/en PATH en MAK." >&2
    exit 2
fi

if ! rclone listremotes 2>/dev/null | grep -qx "${REMOTE}:"; then
    echo "ERROR: remote rclone '${REMOTE}:' no existe (rclone listremotes vacio de eso)." >&2
    echo "No se inventa config nueva. Remote esperado: '${REMOTE}:' (ya usado por otros" >&2
    echo "procesos de MAK, ver bridge de renders 2026-07-20)." >&2
    exit 2
fi

if [[ $# -eq 0 ]]; then
    echo "Candidatas para archivar a OneDrive:"
    echo "-- encoladas/curadas (${ENCOLADO}):"
    [[ -d "$ENCOLADO" ]] && ls -la "$ENCOLADO" || echo "   (no existe)"
    echo "-- staging sin encolar (${INBOX}, probablemente NO curadas aun):"
    [[ -d "$INBOX" ]] && ls -la "$INBOX" || echo "   (no existe)"
    echo
    echo "Uso: onedrive_archivar.sh <ruta_local_absoluta_o_relativa>"
    exit 0
fi

ORIGEN="$1"
if [[ ! -d "$ORIGEN" ]]; then
    echo "ERROR: '$ORIGEN' no existe." >&2
    exit 2
fi
ORIGEN="$(cd "$ORIGEN" && pwd)"
NOMBRE="$(basename "$ORIGEN")"
DESTINO="${REMOTE_BASE}/${NOMBRE}"

N_LOCAL=$(find "$ORIGEN" -type f | wc -l)
B_LOCAL=$(du -sb "$ORIGEN" | cut -f1)
echo "Origen : $ORIGEN ($N_LOCAL archivos, $B_LOCAL bytes)"
echo "Destino: $DESTINO"

echo "Subiendo (rclone copy)..."
rclone copy "$ORIGEN" "$DESTINO" --create-empty-src-dirs

echo "Verificando (rclone check)..."
if rclone check "$ORIGEN" "$DESTINO"; then
    echo "OK: verificacion rclone check paso. Borrando local..."
    rm -rf "$ORIGEN"
    echo "Archivado y local borrado: $ORIGEN -> $DESTINO"
else
    echo "FALLO: rclone check no paso. NO se borra local. Revisar manualmente." >&2
    exit 1
fi
