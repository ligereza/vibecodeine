#!/usr/bin/env bash
# Etapa 2 del pipeline WIN->MAK->OneDrive: mueve una carpeta de
# ~/curatoria_inbox/ (staging, dejada por enviar_a_mak.py desde Windows)
# hacia el directorio que percepcion.py realmente procesa.
#
# NADA la ejecuta sola (sin cron): decision manual del usuario o de un
# agente que sepa lo que hace. Vive en MAK en ~/curatoria/curatoria_encolar.sh
# (copia espejo de referencia en el repo, esto NO se sincroniza por el cron
# MAK-REPO-SYNC porque ese cron solo copia cultura/mak_plataforma|research|codex).
#
# Uso:
#   curatoria_encolar.sh                 # lista que hay en el inbox
#   curatoria_encolar.sh <carpeta>        # encola <carpeta> a destino
#   curatoria_encolar.sh <carpeta> <raiz> # encola a raiz custom (default: RD)
set -euo pipefail

INBOX="$HOME/curatoria_inbox"
# Raiz por defecto donde percepcion.py espera material RD (ver --raiz-rd).
# Ajustar si el destino real difiere; percepcion.py se invoca aparte con
# --raiz-rd/--raiz-ig explicitos, este script solo posiciona los archivos.
DESTINO_DEFAULT="$HOME/curatoria_encolado"

if [[ $# -eq 0 ]]; then
    echo "Carpetas en staging (~/curatoria_inbox/):"
    if [[ -d "$INBOX" ]]; then
        ls -la "$INBOX"
    else
        echo "  (vacio: $INBOX no existe)"
    fi
    echo
    echo "Uso: curatoria_encolar.sh <carpeta> [raiz_destino]"
    exit 0
fi

CARPETA="$1"
DESTINO="${2:-$DESTINO_DEFAULT}"
ORIGEN="$INBOX/$CARPETA"

if [[ ! -d "$ORIGEN" ]]; then
    echo "ERROR: '$ORIGEN' no existe en el inbox." >&2
    exit 2
fi

mkdir -p "$DESTINO"

if [[ -e "$DESTINO/$CARPETA" ]]; then
    echo "ERROR: '$DESTINO/$CARPETA' ya existe. Revisa/renombra antes de encolar." >&2
    exit 2
fi

N_ANTES=$(find "$ORIGEN" -type f | wc -l)
B_ANTES=$(du -sb "$ORIGEN" | cut -f1)

mv "$ORIGEN" "$DESTINO/$CARPETA"

N_DESPUES=$(find "$DESTINO/$CARPETA" -type f | wc -l)
B_DESPUES=$(du -sb "$DESTINO/$CARPETA" | cut -f1)

echo "Encolado: $CARPETA -> $DESTINO/$CARPETA"
echo "Archivos: $N_ANTES -> $N_DESPUES | Bytes: $B_ANTES -> $B_DESPUES"
if [[ "$N_ANTES" == "$N_DESPUES" && "$B_ANTES" == "$B_DESPUES" ]]; then
    echo "OK"
else
    echo "FALLO: no coincide el conteo post-mv" >&2
    exit 1
fi
